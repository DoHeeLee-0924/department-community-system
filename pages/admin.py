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
    conn.execute(
        "INSERT INTO reports(target_type, target_id, reporter_profile, reason, created_at) VALUES(?,?,?,?,?)",
        (target_type, target_id, user["profile"], reason, now()),
    )
    conn.commit()
    conn.close()

    flash("신고가 접수되었습니다.")
    return redirect(request.referrer or url_for("posts.index"))


@admin_bp.route("/admin")
@admin_required
def admin_home():
    conn = get_db()
    posts = conn.execute(
        "SELECT * FROM posts WHERE archived=0 ORDER BY created_at DESC"
    ).fetchall()
    comments = conn.execute(
        """
        SELECT c.*, p.title
        FROM comments c
        LEFT JOIN posts p ON c.post_id=p.id
        ORDER BY c.created_at DESC
        """
    ).fetchall()
    reports = conn.execute(
        "SELECT * FROM reports ORDER BY created_at DESC"
    ).fetchall()
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
    conn.execute("UPDATE posts SET archived=1 WHERE id=?", (post_id,))
    conn.commit()
    conn.close()
    flash("게시글을 삭제 처리했습니다.")
    return redirect(url_for("admin.admin_home"))


@admin_bp.route("/admin/comment/<int:comment_id>/delete", methods=["POST"])
@admin_required
def delete_comment(comment_id):
    conn = get_db()
    conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    flash("댓글을 삭제했습니다.")
    return redirect(url_for("admin.admin_home"))
