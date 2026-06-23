from datetime import datetime
from functools import wraps
from flask import session, flash, redirect, url_for, g

from config import ADMIN_ID, GRADE_WEIGHT
from database import get_db


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def grade_from_counts(username, role, post_count, comment_count):
    if role == "admin" or username == ADMIN_ID:
        return "관리자"
    if post_count >= 10 and comment_count >= 10:
        return "최우수"
    if post_count >= 5 and comment_count >= 5:
        return "우수"
    if post_count >= 1:
        return "일반"
    return "신입"


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
    return grade_from_counts(username, role, post_count, comment_count)


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
    # 한 요청 안에서 current_user가 여러 번 호출되어도 DB를 한 번만 조회하도록 캐싱한다.
    if hasattr(g, "current_user_cache"):
        return g.current_user_cache

    if "user_id" not in session:
        g.current_user_cache = None
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
        g.current_user_cache = None
        return None

    data = dict(user)
    data["profile"] = data["profile_id"]
    data["grade"] = refresh_user_grade(data)
    data["weight"] = GRADE_WEIGHT[data["grade"]]
    data["can_interact"] = data["grade"] != "신입"
    g.current_user_cache = data
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


def trust_from_counts(row):
    grade = grade_from_counts(
        row.get("username"),
        row.get("role"),
        int(row.get("writer_post_count") or 0),
        int(row.get("writer_comment_count") or 0),
    )
    like_count = int(row.get("like_count") or 0)
    comment_count = int(row.get("comment_count") or 0)
    view_count = int(row.get("view_count") or 0)
    score = GRADE_WEIGHT[grade] * 10 + like_count * 2 + comment_count + view_count * 0.1

    if row.get("archived"):
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


def calc_trust_score(post):
    # 상세 페이지 등 단건 계산용. 기존처럼 여러 연결을 만들지 않고 한 번의 쿼리로 필요한 값을 가져온다.
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              p.post_id AS id,
              p.user_id,
              p.view_count,
              p.archived,
              u.username,
              u.role,
              COALESCE(wp.post_count, 0) AS writer_post_count,
              COALESCE(wc.comment_count, 0) AS writer_comment_count,
              COALESCE(lc.like_count, 0) AS like_count,
              COALESCE(cc.comment_count, 0) AS comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            LEFT JOIN (
              SELECT user_id, COUNT(*) AS post_count
              FROM posts
              WHERE archived=FALSE
              GROUP BY user_id
            ) wp ON p.user_id = wp.user_id
            LEFT JOIN (
              SELECT user_id, COUNT(*) AS comment_count
              FROM comments
              WHERE archived=FALSE
              GROUP BY user_id
            ) wc ON p.user_id = wc.user_id
            LEFT JOIN (
              SELECT post_id, COUNT(*) AS like_count
              FROM likes
              GROUP BY post_id
            ) lc ON p.post_id = lc.post_id
            LEFT JOIN (
              SELECT post_id, COUNT(*) AS comment_count
              FROM comments
              WHERE archived=FALSE
              GROUP BY post_id
            ) cc ON p.post_id = cc.post_id
            WHERE p.post_id=%s
            """,
            (post["id"],),
        )
        row = cur.fetchone()
    conn.close()
    return trust_from_counts(row or post)
