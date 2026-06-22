from flask import Blueprint, render_template, request, redirect, url_for, flash

from database import get_db
from utils import current_user, login_required, admin_required, now


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/report/<target_type>/<int:target_id>", methods=["POST"])
@login_required
def report(target_type, target_id):
    user = current_user()
    reason = request.form.get("reason", "").strip()

    if not user["can_interact"]:
        flash("일반 등급 이상부터 신고할 수 있습니다.")
        return redirect(url_for("posts.index"))

    if not reason:
        flash("신고 사유를 입력해야 합니다.")
        return redirect(request.referrer or url_for("posts.index"))

    if target_type not in ["post", "comment"]:
        flash("신고 대상을 확인할 수 없습니다.")
        return redirect(url_for("posts.index"))

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO reports(target_type, target_id, reporter_id, reason, created_at)
            VALUES(%s, %s, %s, %s, %s)
            """,
            (target_type, target_id, user["user_id"], reason, now()),
        )
    conn.commit()
    conn.close()

    flash("신고가 접수되었습니다.")
    return redirect(request.referrer or url_for("posts.index"))


@admin_bp.route("/admin")
@admin_required
def admin_home():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              p.post_id AS id,
              p.post_id,
              p.title,
              p.created_at,
              u.profile_id AS profile
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.archived=FALSE
            ORDER BY p.created_at DESC
            """
        )
        posts = cur.fetchall()

        cur.execute(
            """
            SELECT
              cm.comment_id AS id,
              cm.comment_id,
              cm.content,
              cm.created_at,
              p.title,
              u.profile_id AS profile
            FROM comments cm
            LEFT JOIN posts p ON cm.post_id=p.post_id
            JOIN users u ON cm.user_id=u.user_id
            WHERE cm.archived=FALSE
            ORDER BY cm.created_at DESC
            """
        )
        comments = cur.fetchall()

        cur.execute(
            """
            SELECT
              r.report_id,
              r.target_type,
              r.target_id,
              u.profile_id AS reporter_profile,
              r.reason,
              r.created_at
            FROM reports r
            JOIN users u ON r.reporter_id = u.user_id
            ORDER BY r.created_at DESC
            """
        )
        reports = cur.fetchall()
    conn.close()

    return render_template(
        "admin.html",
        posts=posts,
        comments=comments,
        reports=reports,
    )


@admin_bp.route("/admin/post/<int:post_id>/delete", methods=["POST"])
@admin_required
def delete_post(post_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE posts SET archived=TRUE WHERE post_id=%s", (post_id,))
    conn.commit()
    conn.close()
    flash("게시글을 삭제 처리했습니다.")
    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/admin/comment/<int:comment_id>/delete", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE comments SET archived=TRUE WHERE comment_id=%s", (comment_id,))
    conn.commit()
    conn.close()
    flash("댓글을 삭제 처리했습니다.")
    return redirect(url_for("admin.admin_home"))
