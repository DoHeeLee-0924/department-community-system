# 학과 정보공유 시스템

태그 분류와 신뢰도 점수를 활용한 학과 정보공유 플랫폼입니다.

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

브라우저에서 접속:

```text
http://127.0.0.1:5000
```

## 관리자 계정

```text
ID: qwer
PW: 1234
```

## 프로젝트 구조

```text
project_final/
├─ main.py                 # Flask 앱 실행 파일
├─ config.py               # 설정값
├─ database.py             # DB 연결 및 초기화
├─ utils.py                # 등급 산정, 신뢰도 점수 등 공통 로직
├─ pages/
│  ├─ auth.py              # 로그인/회원가입
│  ├─ posts.py             # 게시글/댓글/좋아요/수정
│  └─ admin.py             # 신고/관리자 삭제
├─ templates/              # HTML 화면
├─ static/style.css         # CSS
├─ requirements.txt
└─ mysql_schema.sql
```

## 핵심 기능

- 회원가입 시 신입 등급으로 시작
- 신입은 인사방만 조회/작성 가능
- 게시글 1개 이상 작성 시 일반 등급
- 우수/최우수 등급은 신뢰도 점수 가중치 상승
- 작성자 본인은 게시글/댓글 수정 가능
- 관리자는 수정 불가, 삭제만 가능
- 일반 등급 이상은 신고 가능
- 관리자만 신고 목록 조회 가능
