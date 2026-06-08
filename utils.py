from datetime import datetime
from functools import wraps
from flask import session, flash, redirect, url_for

from config import ADMIN_ID, GRADE_WEIGHT
from database import get_db


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_activity(profile):
    conn = get_db()
    post_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM posts WHERE profile=? AND archived=0",
        (profile,),
    ).fetchone()["cnt"]
    comment_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM comments WHERE profile=?",
        (profile,),
    ).fetchone()["cnt"]
    conn.close()
    return post_count, comment_count


def calc_grade(username, profile):
    if username == ADMIN_ID or profile == "관리자":
        return "관리자"

    post_count, comment_count = get_activity(profile)
    if post_count >= 10 and comment_count >= 10:
        return "최우수"
    if post_count >= 5 and comment_count >= 5:
        return "우수"
    if post_count >= 1:
        return "일반"
    return "신입"


def current_user():
    if "username" not in session:
        return None

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (session["username"],),
    ).fetchone()
    conn.close()

    if not user:
        return None

    data = dict(user)
    data["grade"] = calc_grade(data["username"], data["profile"])
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
    writer = conn.execute(
        "SELECT username, profile FROM users WHERE profile=?",
        (post["profile"],),
    ).fetchone()
    like_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM likes WHERE post_id=?",
        (post["id"],),
    ).fetchone()["cnt"]
    comment_count = conn.execute(
        "SELECT COUNT(*) AS cnt FROM comments WHERE post_id=?",
        (post["id"],),
    ).fetchone()["cnt"]
    conn.close()

    grade = calc_grade(writer["username"], writer["profile"]) if writer else "신입"
    score = (
        GRADE_WEIGHT[grade] * 10
        + like_count * 2
        + comment_count
        + post["view_count"] * 0.1
    )

    if score >= 40:
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
