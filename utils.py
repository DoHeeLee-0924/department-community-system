from datetime import datetime
from functools import wraps
from flask import session, flash, redirect, url_for

from config import ADMIN_ID, GRADE_WEIGHT
from database import get_db


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_activity(user_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM posts WHERE user_id=%s AND archived=FALSE",
            (user_id,),
        )
        post_count = cur.fetchone()["cnt"]
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM comments WHERE user_id=%s AND archived=FALSE",
            (user_id,),
        )
        comment_count = cur.fetchone()["cnt"]
    conn.close()
    return post_count, comment_count


def calc_grade(user_id, username=None, role=None):
    if role == "admin" or username == ADMIN_ID:
        return "관리자"

    post_count, comment_count = get_activity(user_id)
    if post_count >= 10 and comment_count >= 10:
        return "최우수"
    if post_count >= 5 and comment_count >= 5:
        return "우수"
    if post_count >= 1:
        return "일반"
    return "신입"


def refresh_user_grade(user):
    grade = calc_grade(user["user_id"], user.get("username"), user.get("role"))
    if user.get("grade_name") != grade:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET grade_name=%s WHERE user_id=%s",
                (grade, user["user_id"]),
            )
        conn.commit()
        conn.close()
    return grade


def current_user():
    if "user_id" not in session:
        return None

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM users WHERE user_id=%s",
            (session["user_id"],),
        )
        user = cur.fetchone()
    conn.close()

    if not user:
        return None

    data = dict(user)
    data["profile"] = data["profile_id"]
    data["grade"] = refresh_user_grade(data)
    data["weight"] = GRADE_WEIGHT[data["grade"]]
    data["can_interact"] = data["grade"] != "신입"
    return data


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("로그인이 필요합니다.")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user["grade"] != "관리자":
            flash("관리자만 접근할 수 있습니다.")
            return redirect(url_for("posts.index"))
        return view_func(*args, **kwargs)
    return wrapper


def calc_trust_score(post):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT username, role, grade_name FROM users WHERE user_id=%s",
            (post["user_id"],),
        )
        writer = cur.fetchone()
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM likes WHERE post_id=%s",
            (post["id"],),
        )
        like_count = cur.fetchone()["cnt"]
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM comments WHERE post_id=%s AND archived=FALSE",
            (post["id"],),
        )
        comment_count = cur.fetchone()["cnt"]
    conn.close()

    grade = calc_grade(post["user_id"], writer["username"], writer["role"]) if writer else "신입"
    score = (
        GRADE_WEIGHT[grade] * 10
        + like_count * 2
        + comment_count
        + post["view_count"] * 0.1
    )

    if post.get("archived"):
        exposure = "조회 제외"
    elif score >= 40:
        exposure = "최상단 노출"
    elif score >= 30:
        exposure = "상단 노출"
    elif score >= 20:
        exposure = "일반 노출"
    else:
        exposure = "낮은 우선순위"

    return {
        "grade": grade,
        "like_count": like_count,
        "comment_count": comment_count,
        "score": round(score, 1),
        "exposure": exposure,
    }
