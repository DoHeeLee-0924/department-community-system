import sqlite3
from config import DB_PATH, ADMIN_ID, ADMIN_PW, CATEGORIES, ENABLE_SAMPLE_DATA


def get_db():
    """SQLite DB 연결을 반환한다."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """
    DB와 기본 데이터를 준비한다.

    중요:
    - DROP TABLE을 사용하지 않는다.
    - CREATE TABLE IF NOT EXISTS를 사용한다.
    - 기본 데이터는 INSERT OR IGNORE로 넣는다.

    따라서 서버를 껐다 켜도 회원, 게시글, 댓글, 좋아요, 신고 데이터가 계속 유지된다.
    """
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT,
        profile TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS grade_rules(
        grade_name TEXT PRIMARY KEY,
        min_post_count INTEGER NOT NULL,
        min_comment_count INTEGER NOT NULL,
        weight REAL NOT NULL,
        can_view INTEGER NOT NULL,
        can_interact INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS categories(
        category_name TEXT PRIMARY KEY,
        description TEXT
    );

    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        view_count INTEGER DEFAULT 0,
        archived INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        FOREIGN KEY(profile) REFERENCES users(profile),
        FOREIGN KEY(category) REFERENCES categories(category_name)
    );

    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        profile TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT,
        archived INTEGER DEFAULT 0,
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(profile) REFERENCES users(profile)
    );

    CREATE TABLE IF NOT EXISTS likes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        profile TEXT NOT NULL,
        created_at TEXT,
        UNIQUE(post_id, profile),
        FOREIGN KEY(post_id) REFERENCES posts(id),
        FOREIGN KEY(profile) REFERENCES users(profile)
    );

    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT NOT NULL,
        target_id INTEGER NOT NULL,
        reporter_profile TEXT NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(reporter_profile) REFERENCES users(profile)
    );
    """)

    # 기존 DB 파일을 사용하던 경우에도 새 컬럼이 없으면 추가한다.
    _add_column_if_missing(cur, "posts", "updated_at", "TEXT")
    _add_column_if_missing(cur, "comments", "updated_at", "TEXT")
    _add_column_if_missing(cur, "comments", "archived", "INTEGER DEFAULT 0")
    _add_column_if_missing(cur, "likes", "created_at", "TEXT")

    insert_default_data(cur)
    if ENABLE_SAMPLE_DATA:
        insert_sample_data(cur)

    conn.commit()
    conn.close()


def _add_column_if_missing(cur, table_name, column_name, column_definition):
    columns = [row[1] for row in cur.execute(f"PRAGMA table_info({table_name})").fetchall()]
    if column_name not in columns:
        cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def insert_default_data(cur):
    """등급 규칙, 카테고리, 관리자 계정을 없을 때만 삽입한다."""
    cur.executemany(
        """
        INSERT OR IGNORE INTO grade_rules
        (grade_name, min_post_count, min_comment_count, weight, can_view, can_interact)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            ("신입", 0, 0, 0.5, 0, 0),
            ("일반", 1, 0, 1.0, 1, 1),
            ("우수", 5, 5, 2.0, 1, 1),
            ("최우수", 10, 10, 3.0, 1, 1),
            ("관리자", 0, 0, 3.0, 1, 1),
        ],
    )

    category_descriptions = {
        "인사방": "신입 사용자가 인사글을 작성하는 공간",
        "수업": "수업 관련 정보",
        "과제": "과제 관련 정보",
        "팀플": "팀플 관련 정보",
        "공지": "공지 관련 정보",
        "취업": "취업 관련 정보",
    }
    cur.executemany(
        """
        INSERT OR IGNORE INTO categories(category_name, description)
        VALUES (?, ?)
        """,
        [(category, category_descriptions.get(category, "")) for category in CATEGORIES],
    )

    # 관리자 계정은 없을 때만 만든다. 일반 사용자의 데이터는 건드리지 않는다.
    cur.execute(
        """
        INSERT OR IGNORE INTO users(username, password, name, profile)
        VALUES (?, ?, ?, ?)
        """,
        (ADMIN_ID, ADMIN_PW, "관리자", "관리자"),
    )
    # 관리자는 고정 비밀번호를 유지한다.
    cur.execute(
        "UPDATE users SET password=?, name=?, profile=? WHERE username=?",
        (ADMIN_PW, "관리자", "관리자", ADMIN_ID),
    )



def _get_user_profile(cur, username):
    row = cur.execute("SELECT profile FROM users WHERE username=?", (username,)).fetchone()
    return row[0] if row else None


def _get_post_id(cur, profile, title):
    row = cur.execute(
        "SELECT id FROM posts WHERE profile=? AND title=?",
        (profile, title),
    ).fetchone()
    return row[0] if row else None


def _insert_post_if_missing(cur, profile, category, title, content, view_count=0, created_at="2026-06-05 10:00:00"):
    post_id = _get_post_id(cur, profile, title)
    if post_id:
        return post_id
    cur.execute(
        """
        INSERT INTO posts(profile, category, title, content, view_count, archived, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
        """,
        (profile, category, title, content, view_count, created_at),
    )
    return cur.lastrowid


def _insert_comment_if_missing(cur, post_id, profile, content, created_at="2026-06-05 11:00:00"):
    exists = cur.execute(
        "SELECT id FROM comments WHERE post_id=? AND profile=? AND content=?",
        (post_id, profile, content),
    ).fetchone()
    if exists:
        return exists[0]
    cur.execute(
        """
        INSERT INTO comments(post_id, profile, content, created_at, archived)
        VALUES (?, ?, ?, ?, 0)
        """,
        (post_id, profile, content, created_at),
    )
    return cur.lastrowid


def _insert_like_if_missing(cur, post_id, profile, created_at="2026-06-05 12:00:00"):
    cur.execute(
        """
        INSERT OR IGNORE INTO likes(post_id, profile, created_at)
        VALUES (?, ?, ?)
        """,
        (post_id, profile, created_at),
    )


def _insert_report_if_missing(cur, target_type, target_id, reporter_profile, reason, created_at="2026-06-05 13:00:00"):
    exists = cur.execute(
        """
        SELECT id FROM reports
        WHERE target_type=? AND target_id=? AND reporter_profile=? AND reason=?
        """,
        (target_type, target_id, reporter_profile, reason),
    ).fetchone()
    if exists:
        return exists[0]
    cur.execute(
        """
        INSERT INTO reports(target_type, target_id, reporter_profile, reason, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (target_type, target_id, reporter_profile, reason, created_at),
    )
    return cur.lastrowid


def insert_sample_data(cur):
    """
    시연용 샘플 데이터를 없을 때만 삽입한다.

    샘플 계정
    - newbie / 1234: 신입
    - general / 1234: 일반
    - mentor / 1234: 우수
    - topmentor / 1234: 최우수
    - qwer / 1234: 관리자
    """
    sample_users = [
        ("newbie", "1234", "신입 사용자", "신입학생"),
        ("general", "1234", "일반 사용자", "일반학생"),
        ("mentor", "1234", "우수 멘토", "우수멘토"),
        ("topmentor", "1234", "최우수 멘토", "최우수멘토"),
        ("student1", "1234", "김수업", "수업질문러"),
        ("student2", "1234", "박과제", "과제도우미"),
    ]
    cur.executemany(
        """
        INSERT OR IGNORE INTO users(username, password, name, profile)
        VALUES (?, ?, ?, ?)
        """,
        sample_users,
    )

    profiles = {name: _get_user_profile(cur, name) for name, *_ in sample_users}
    admin_profile = _get_user_profile(cur, ADMIN_ID)

    # 일반 등급: 게시글 1개 이상
    p_general = _insert_post_if_missing(
        cur,
        profiles["general"],
        "인사방",
        "안녕하세요 일반 등급 테스트 글입니다",
        "신입 사용자가 인사방에 글을 1개 작성하면 일반 등급으로 상승하는 흐름을 확인하기 위한 샘플입니다.",
        8,
        "2026-06-05 09:00:00",
    )

    # 우수 등급: 게시글 5개 이상 + 댓글 5개 이상
    mentor_titles = [
        ("수업", "데이터베이스 정규화 핵심 정리", "1NF, 2NF, 3NF의 차이를 간단히 정리한 글입니다.", 42),
        ("과제", "ERD 과제 작성 팁", "엔티티, 관계, 카디널리티를 먼저 잡고 속성을 배치하면 좋습니다.", 35),
        ("팀플", "팀플 역할 분담 예시", "발표, 자료조사, 설계, 구현으로 역할을 나누면 관리가 쉽습니다.", 21),
        ("공지", "정보시스템설계 발표 준비 체크리스트", "목적, ERD, Relation Schema, Decision Table을 반드시 확인하세요.", 55),
        ("취업", "IT 직무 포트폴리오 구성 팁", "프로젝트 설명, ERD, 실행 화면, GitHub 링크를 함께 정리하면 좋습니다.", 31),
    ]
    mentor_post_ids = []
    for i, (category, title, content, views) in enumerate(mentor_titles, start=1):
        mentor_post_ids.append(_insert_post_if_missing(
            cur, profiles["mentor"], category, title, content, views, f"2026-06-05 10:0{i}:00"
        ))

    # 최우수 등급: 게시글 10개 이상 + 댓글 10개 이상
    top_titles = [
        ("수업", "SQL JOIN 개념 한 번에 정리", "INNER JOIN, LEFT JOIN의 차이를 예시 중심으로 정리했습니다.", 70),
        ("수업", "GROUP BY와 HAVING 차이", "집계 이후 조건은 HAVING을 사용합니다.", 44),
        ("과제", "Decision Table 작성 예시", "조건부와 실행부를 분리하면 Rule이 명확해집니다.", 66),
        ("과제", "Relation Schema 작성 방법", "PK와 FK를 함께 적으면 논리 모델링이 명확해집니다.", 58),
        ("팀플", "발표자료 흐름 추천", "문제, 목적, 설계, Rule, 기대효과 순서로 구성하면 좋습니다.", 40),
        ("팀플", "GitHub 제출 전 체크사항", "requirements.txt와 README.md를 반드시 확인하세요.", 26),
        ("공지", "기말 팀프로젝트 제출 안내", "실행 방법과 관리자 계정을 발표 전에 확인하세요.", 82),
        ("공지", "관리자 신고 처리 정책", "신고된 글과 댓글은 관리자가 삭제할 수 있습니다.", 34),
        ("취업", "데이터 분석 직무 준비 자료", "SQL, Python, 프로젝트 문서화 역량이 중요합니다.", 48),
        ("취업", "면접에서 프로젝트 설명하는 법", "문제 정의와 본인의 역할을 먼저 설명하는 것이 좋습니다.", 37),
    ]
    top_post_ids = []
    for i, (category, title, content, views) in enumerate(top_titles, start=1):
        top_post_ids.append(_insert_post_if_missing(
            cur, profiles["topmentor"], category, title, content, views, f"2026-06-05 10:{10+i:02d}:00"
        ))

    # 추가 일반 학생 게시글
    p_student1 = _insert_post_if_missing(
        cur,
        profiles["student1"],
        "수업",
        "JOIN 문제에서 INNER JOIN과 그냥 JOIN 차이가 있나요?",
        "MySQL에서 JOIN과 INNER JOIN이 같은 의미인지 궁금합니다.",
        12,
        "2026-06-05 11:10:00",
    )
    p_student2 = _insert_post_if_missing(
        cur,
        profiles["student2"],
        "과제",
        "ERD에서 카테고리를 따로 빼는 게 맞나요?",
        "게시글 테이블에 category를 문자열로 넣는 것과 별도 테이블로 빼는 것 중 어떤 게 좋은지 질문합니다.",
        18,
        "2026-06-05 11:15:00",
    )

    # 우수/최우수 등급 충족을 위한 댓글 작성
    for idx, post_id in enumerate(top_post_ids[:5], start=1):
        _insert_comment_if_missing(cur, post_id, profiles["mentor"], f"우수멘토 댓글 {idx}: 좋은 자료 감사합니다.")
    for idx, post_id in enumerate(mentor_post_ids + top_post_ids[:5], start=1):
        _insert_comment_if_missing(cur, post_id, profiles["topmentor"], f"최우수멘토 댓글 {idx}: 발표 때 이 부분을 강조하면 좋겠습니다.")

    # 게시글에 다양한 댓글 추가
    _insert_comment_if_missing(cur, mentor_post_ids[0], profiles["general"], "정규화 예시가 있어서 이해가 잘 됩니다.")
    _insert_comment_if_missing(cur, mentor_post_ids[0], profiles["student1"], "3NF 부분을 발표 때 넣어도 좋을 것 같아요.")
    _insert_comment_if_missing(cur, top_post_ids[2], profiles["student2"], "Decision Table 양식 참고하겠습니다.")
    _insert_comment_if_missing(cur, p_student1, profiles["mentor"], "MySQL에서는 JOIN이 INNER JOIN과 동일하게 동작합니다.")
    _insert_comment_if_missing(cur, p_student2, profiles["topmentor"], "카테고리는 별도 테이블로 분리하는 것이 설계상 더 좋습니다.")

    # 좋아요 샘플
    all_like_posts = [p_general, p_student1, p_student2] + mentor_post_ids + top_post_ids
    like_profiles = [profiles["general"], profiles["mentor"], profiles["topmentor"], profiles["student1"], profiles["student2"]]
    for i, post_id in enumerate(all_like_posts):
        for profile in like_profiles[: (i % len(like_profiles)) + 1]:
            _insert_like_if_missing(cur, post_id, profile)

    # 신고 샘플: 관리자 페이지 확인용
    _insert_report_if_missing(cur, "post", p_student1, profiles["general"], "중복 질문 여부 확인 필요")
    comment_to_report = cur.execute(
        "SELECT id FROM comments WHERE post_id=? LIMIT 1",
        (mentor_post_ids[0],),
    ).fetchone()
    if comment_to_report:
        _insert_report_if_missing(cur, "comment", comment_to_report[0], profiles["student2"], "표현이 부정확할 수 있음")
