import os

# 프로젝트 폴더 기준으로 DB 경로를 고정한다.
# 따라서 어느 위치에서 python main.py를 실행해도 같은 DB 파일을 사용한다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

# 첫 실행 시 시연용 샘플 데이터를 자동 삽입한다.
ENABLE_SAMPLE_DATA = True
