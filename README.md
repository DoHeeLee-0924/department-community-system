# 학과 정보공유 시스템

태그 분류와 신뢰도 점수를 활용한 학과 정보공유 커뮤니티 시스템입니다.  
이 버전은 **Flask + MySQL** 기반으로 실행됩니다.

## 1. 주요 변경 사항

기존 SQLite `community.db` 방식이 아니라 실제 MySQL DB를 사용합니다.

| 구분 | 변경 전 | 변경 후 |
|---|---|---|
| DB | SQLite `community.db` | MySQL `department_community` |
| 연결 라이브러리 | sqlite3 | PyMySQL |
| 사용자 PK | id/profile | user_id/profile_id |
| 게시글 FK | profile/category | user_id/category_id |
| 카테고리 PK | category_name | category_id |
| 신고자 FK | reporter_profile | reporter_id |

## 2. 실행 전 준비

MySQL Workbench에서 MySQL 서버가 실행 중이어야 합니다.

`config.py`에서 본인 MySQL 접속 정보에 맞게 수정하세요.

```python
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "본인 MySQL 비밀번호"
MYSQL_DB = "department_community"
```

비밀번호가 없으면 빈 문자열 그대로 두면 됩니다.

## 3. 패키지 설치

```powershell
pip install -r requirements.txt
```

## 4. 실행

```powershell
python main.py
```

실행 시 `database.py`가 MySQL에 접속해서 `department_community` DB와 기본 테이블을 준비합니다.

브라우저 접속:

```text
http://127.0.0.1:5000
```

## 5. 기본 계정

| 구분 | 아이디 | 비밀번호 |
|---|---|---|
| 관리자 | qwer | 1234 |

## 6. 샘플 데이터 넣기

샘플 게시글, 댓글, 좋아요, 신고 데이터는 코드에 자동 삽입하지 않습니다.  
필요할 때 MySQL Workbench에서 `mysql_sample_data.sql`을 직접 실행하세요.

실행 순서:

1. `mysql_schema.sql` 실행 또는 `python main.py` 실행
2. `mysql_sample_data.sql` 실행
3. `python main.py` 실행 후 웹에서 확인

## 7. 제출용 SQL 파일

| 파일 | 용도 |
|---|---|
| `mysql_schema.sql` | ERD, EER, Relation Schema와 일치하는 MySQL 테이블 생성 파일 |
| `mysql_sample_data.sql` | 시연용 샘플 데이터 삽입 파일 |

## 8. 주요 기능

- 회원가입/로그인
- 신입/일반/우수/최우수/관리자 등급 산정
- 신입은 인사방만 작성 및 상세 조회 가능
- 태그 필수 글쓰기
- 카테고리별 조회
- 좋아요/댓글
- 신뢰도 점수 계산
- 작성자 본인 수정
- 일반 이상 신고 가능
- 관리자 신고 목록 조회 및 삭제 처리

## 9. 신뢰도 점수 공식

```text
신뢰도 점수 = 등급가중치 × 10 + 좋아요 수 × 2 + 댓글 수 × 1 + 조회수 × 0.1
```
