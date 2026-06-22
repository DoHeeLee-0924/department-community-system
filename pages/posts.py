import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash

from config import CATEGORIES
from database import get_db
from utils import current_user, login_required, now, calc_trust_score


posts_bp = Blueprint("posts", __name__)


def _get_category_id(cur, category_name):
    cur.execute("SELECT category_id FROM categories WHERE category_name=%s", (category_name,))
    row = cur.fetchone()
    return row["category_id"] if row else None


def _select_posts_sql(where_clause="", order_clause="p.created_at DESC"):
    return f"""
        SELECT
          p.post_id AS id,
          p.post_id,
          p.user_id,
          p.category_id,
          c.category_name AS category,
          p.title,
          p.content,
          p.view_count,
          p.archived,
          p.created_at,
          p.updated_at,
          u.username,
          u.profile_id AS profile,
          u.grade_name
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        JOIN categories c ON p.category_id = c.category_id
        {where_clause}
        ORDER BY {order_clause}
    """


@posts_bp.route("/")
def index():
    selected_category = request.args.get("category")
    mode = request.args.get("mode", "trust")

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(_select_posts_sql("WHERE p.archived=FALSE"))
        rows = cur.fetchall()
    conn.close()

    posts = []
    for row in rows:
        if selected_category and row["category"] != selected_category:
            continue
        post = dict(row)
        post.update(calc_trust_score(row))
        posts.append(post)

    if mode == "trust":
        posts.sort(key=lambda x: (x["score"], x["created_at"]), reverse=True)

    return render_template(
        "index.html",
        posts=posts,
        selected_category=selected_category,
        mode=mode,
    )


@posts_bp.route("/write", methods=["GET", "POST"])
@login_required
def write():
    user = current_user()

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        category = request.form["category"]

        if not title or not content or category not in CATEGORIES:
            flash("제목, 내용, 태그를 모두 입력해야 합니다.")
            return redirect(url_for("posts.write"))

        if user["grade"] == "신입" and category != "인사방":
            flash("신입은 인사방에만 글을 작성할 수 있습니다.")
            return redirect(url_for("posts.write"))

        conn = get_db()
        with conn.cursor() as cur:
            category_id = _get_category_id(cur, category)
            if not category_id:
                conn.close()
                flash("존재하지 않는 카테고리입니다.")
                return redirect(url_for("posts.write"))
            cur.execute(
                """
                INSERT INTO posts(user_id, category_id, title, content, created_at)
                VALUES(%s, %s, %s, %s, %s)
                """,
                (user["user_id"], category_id, title, content, now()),
            )
        conn.commit()
        conn.close()

        flash("게시글이 등록되었습니다.")
        return redirect(url_for("posts.index", category=category))

    return render_template("write.html")


@posts_bp.route("/post/<int:post_id>")
@login_required
def post_detail(post_id):
    user = current_user()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(_select_posts_sql("WHERE p.post_id=%s AND p.archived=FALSE"), (post_id,))
        post = cur.fetchone()

        if not post:
            conn.close()
            flash("게시글을 찾을 수 없습니다.")
            return redirect(url_for("posts.index"))

        if user["grade"] == "신입" and post["category"] != "인사방":
            conn.close()
            flash("신입은 인사방 게시글만 상세 조회할 수 있습니다.")
            return redirect(url_for("posts.index"))

        cur.execute("UPDATE posts SET view_count=view_count+1 WHERE post_id=%s", (post_id,))
        conn.commit()
        cur.execute(_select_posts_sql("WHERE p.post_id=%s"), (post_id,))
        post = cur.fetchone()
        cur.execute(
            """
            SELECT
              cm.comment_id AS id,
              cm.comment_id,
              cm.post_id,
              cm.user_id,
              cm.content,
              cm.created_at,
              cm.updated_at,
              cm.archived,
              u.profile_id AS profile,
              u.username
            FROM comments cm
            JOIN users u ON cm.user_id = u.user_id
            WHERE cm.post_id=%s AND cm.archived=FALSE
            ORDER BY cm.created_at
            """,
            (post_id,),
        )
        comments = cur.fetchall()
    conn.close()

    trust = calc_trust_score(post)
    return render_template("post_detail.html", post=post, comments=comments, trust=trust)


@posts_bp.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    user = current_user()
    if not user["can_interact"]:
        flash("일반 등급 이상부터 댓글을 작성할 수 있습니다.")
        return redirect(url_for("posts.post_detail", post_id=post_id))

    content = request.form["content"].strip()
    if content:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO comments(post_id, user_id, content, created_at)
                VALUES(%s, %s, %s, %s)
                """,
                (post_id, user["user_id"], content, now()),
            )
        conn.commit()
        conn.close()

    return redirect(url_for("posts.post_detail", post_id=post_id))


@posts_bp.route("/post/<int:post_id>/like", methods=["POST"])
@login_required
def like_post(post_id):
    user = current_user()
    if not user["can_interact"]:
        flash("일반 등급 이상부터 좋아요를 누를 수 있습니다.")
        return redirect(url_for("posts.post_detail", post_id=post_id))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO likes(post_id, user_id, created_at) VALUES(%s, %s, %s)",
                (post_id, user["user_id"], now()),
            )
        conn.commit()
        flash("좋아요를 눌렀습니다.")
    except pymysql.err.IntegrityError:
        flash("이미 좋아요를 눌렀습니다.")
    finally:
        conn.close()

    return redirect(url_for("posts.post_detail", post_id=post_id))


@posts_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    user = current_user()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(_select_posts_sql("WHERE p.post_id=%s AND p.archived=FALSE"), (post_id,))
        post = cur.fetchone()

    if not post or post["user_id"] != user["user_id"]:
        conn.close()
        flash("작성자 본인만 게시글을 수정할 수 있습니다.")
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        category = request.form["category"]

        if not title or not content or category not in CATEGORIES:
            flash("제목, 내용, 태그를 모두 입력해야 합니다.")
            return redirect(url_for("posts.edit_post", post_id=post_id))

        if user["grade"] == "신입" and category != "인사방":
            flash("신입은 인사방 글만 수정할 수 있습니다.")
            return redirect(url_for("posts.edit_post", post_id=post_id))

        with conn.cursor() as cur:
            category_id = _get_category_id(cur, category)
            cur.execute(
                """
                UPDATE posts
                SET title=%s, content=%s, category_id=%s, updated_at=%s
                WHERE post_id=%s AND user_id=%s
                """,
                (title, content, category_id, now(), post_id, user["user_id"]),
            )
        conn.commit()
        conn.close()
        flash("게시글을 수정했습니다.")
        return redirect(url_for("posts.post_detail", post_id=post_id))

    conn.close()
    return render_template("edit_post.html", post=post)


@posts_bp.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    user = current_user()
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              cm.comment_id AS id,
              cm.comment_id,
              cm.post_id,
              cm.user_id,
              cm.content,
              cm.created_at,
              cm.updated_at,
              cm.archived,
              u.profile_id AS profile
            FROM comments cm
            JOIN users u ON cm.user_id = u.user_id
            WHERE cm.comment_id=%s AND cm.archived=FALSE
            """,
            (comment_id,),
        )
        comment = cur.fetchone()

    if not comment or comment["user_id"] != user["user_id"]:
        conn.close()
        flash("작성자 본인만 댓글을 수정할 수 있습니다.")
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        content = request.form["content"].strip()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE comments SET content=%s, updated_at=%s WHERE comment_id=%s AND user_id=%s",
                (content, now(), comment_id, user["user_id"]),
            )
        conn.commit()
        conn.close()
        flash("댓글을 수정했습니다.")
        return redirect(url_for("posts.post_detail", post_id=comment["post_id"]))

    conn.close()
    return render_template("edit_comment.html", comment=comment)
