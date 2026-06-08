import os

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "community.db")
SECRET_KEY = "department-community-demo-key"

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
