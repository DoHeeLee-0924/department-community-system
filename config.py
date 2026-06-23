import os

# Flask 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY = "department-community-demo-key"

# MySQL 연결 설정
# 본인 MySQL Workbench 접속 정보에 맞게 MYSQL_USER / MYSQL_PASSWORD를 수정하면 된다.
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "3122"
MYSQL_DB = "department_community"
MYSQL_CHARSET = "utf8mb4"

ADMIN_ID = "qwer"
ADMIN_PW = "1234"

CATEGORIES = ["인사방", "수업", "과제", "팀플", "공지", "취업"]
GRADE_WEIGHT = {
    "신입": 0.5,
    "일반": 1.0,
    "우수": 2.0,
    "최우수": 3.0,
    "관리자": 3.0,
}
