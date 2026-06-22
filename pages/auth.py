import pymysql
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from config import ADMIN_ID
from database import get_db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        profile_id = request.form["profile"].strip()

        if username == ADMIN_ID:
            flash("qwer는 관리자 전용 아이디입니다.")
            return redirect(url_for("auth.register"))

        try:
            conn = get_db()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users(username, password, profile_id, role, grade_name)
                    VALUES(%s, %s, %s, 'user', '신입')
                    """,
                    (username, password, profile_id),
                )
            conn.commit()
            conn.close()
            flash("회원가입 완료: 신규 회원은 신입 등급입니다.")
            return redirect(url_for("auth.login"))
        except pymysql.err.IntegrityError:
            flash("이미 사용 중인 아이디 또는 프로필 ID입니다.")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s",
                (username, password),
            )
            user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            flash("로그인되었습니다.")
            return redirect(url_for("posts.index"))

        flash("아이디 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃되었습니다.")
    return redirect(url_for("posts.index"))
