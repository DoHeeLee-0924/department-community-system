import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash

from config import CATEGORIES
from database import get_db
from utils import current_user, login_required, now, calc_trust_score


posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/")
def index():
    selected_category = request.args.get("category")
    mode = request.args.get("mode", "trust")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM posts WHERE archived=0 ORDER BY created_at DESC"
    ).fetchall()
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
        conn.execute(
            "INSERT INTO posts(profile, category, title, content, created_at) VALUES(?,?,?,?,?)",
            (user["profile"], category, title, content, now()),
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
    post = conn.execute(
        "SELECT * FROM posts WHERE id=? AND archived=0",
        (post_id,),
    ).fetchone()

    if not post:
        conn.close()
        flash("게시글을 찾을 수 없습니다.")
        return redirect(url_for("posts.index"))

    if user["grade"] == "신입" and post["category"] != "인사방":
        conn.close()
        flash("신입은 인사방 게시글만 상세 조회할 수 있습니다.")
        return redirect(url_for("posts.index"))

    conn.execute("UPDATE posts SET view_count=view_count+1 WHERE id=?", (post_id,))
    conn.commit()
    post = conn.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    comments = conn.execute(
        "SELECT * FROM comments WHERE post_id=? ORDER BY created_at",
        (post_id,),
    ).fetchall()
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
        conn.execute(
            "INSERT INTO comments(post_id, profile, content, created_at) VALUES(?,?,?,?)",
            (post_id, user["profile"], content, now()),
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
        conn.execute(
            "INSERT INTO likes(post_id, profile) VALUES(?,?)",
            (post_id, user["profile"]),
        )
        conn.commit()
        flash("좋아요를 눌렀습니다.")
    except sqlite3.IntegrityError:
        flash("이미 좋아요를 눌렀습니다.")
    conn.close()

    return redirect(url_for("posts.post_detail", post_id=post_id))


@posts_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    user = current_user()
    conn = get_db()
    post = conn.execute(
        "SELECT * FROM posts WHERE id=? AND archived=0",
        (post_id,),
    ).fetchone()

    if not post or post["profile"] != user["profile"]:
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

        conn.execute(
            "UPDATE posts SET title=?, content=?, category=? WHERE id=?",
            (title, content, category, post_id),
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
    comment = conn.execute(
        "SELECT * FROM comments WHERE id=?",
        (comment_id,),
    ).fetchone()

    if not comment or comment["profile"] != user["profile"]:
        conn.close()
        flash("작성자 본인만 댓글을 수정할 수 있습니다.")
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        content = request.form["content"].strip()
        conn.execute("UPDATE comments SET content=? WHERE id=?", (content, comment_id))
        conn.commit()
        conn.close()
        flash("댓글을 수정했습니다.")
        return redirect(url_for("posts.post_detail", post_id=comment["post_id"]))

    conn.close()
    return render_template("edit_comment.html", comment=comment)
