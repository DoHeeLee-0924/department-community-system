import pymysql

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DB,
    MYSQL_CHARSET,
    ADMIN_ID,
    ADMIN_PW,
    CATEGORIES,
)


def get_server_db():
    """MySQL 서버 연결을 반환한다. DB 생성 전 단계에서 사용한다."""
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset=MYSQL_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_db():
    """department_community MySQL DB 연결을 반환한다."""
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset=MYSQL_CHARSET,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def init_db():
    """
    MySQL DB와 기본 데이터를 준비한다.

    중요:
    - 실제 실행 DB는 SQLite가 아니라 MySQL이다.
    - DROP TABLE을 사용하지 않는다.
    - CREATE TABLE IF NOT EXISTS를 사용한다.
    - 기본 등급, 기본 카테고리, 관리자 계정만 INSERT IGNORE로 넣는다.
    - 샘플 게시글/댓글/좋아요/신고 데이터는 mysql_sample_data.sql에서 별도로 넣는다.
    """
    server_conn = get_server_db()
    with server_conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
    server_conn.commit()
    server_conn.close()

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        _create_tables(cur)
        _create_indexes(cur)
        insert_default_data(cur)
    conn.commit()
    conn.close()


def _create_tables(cur):
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS grade_rules (
          grade_name VARCHAR(20) PRIMARY KEY,
          min_post_count INT NOT NULL,
          min_comment_count INT NOT NULL,
          weight DECIMAL(3,1) NOT NULL,
          can_view BOOLEAN NOT NULL,
          can_interact BOOLEAN NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
          user_id INT AUTO_INCREMENT PRIMARY KEY,
          username VARCHAR(50) UNIQUE NOT NULL,
          password VARCHAR(255) NOT NULL,
          profile_id VARCHAR(50) UNIQUE NOT NULL,
          role ENUM('user', 'admin') NOT NULL DEFAULT 'user',
          grade_name VARCHAR(20) NOT NULL DEFAULT '신입',
          FOREIGN KEY (grade_name) REFERENCES grade_rules(grade_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
          category_id INT AUTO_INCREMENT PRIMARY KEY,
          category_name VARCHAR(20) UNIQUE NOT NULL,
          description VARCHAR(255)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
          post_id INT AUTO_INCREMENT PRIMARY KEY,
          user_id INT NOT NULL,
          category_id INT NOT NULL,
          title VARCHAR(200) NOT NULL,
          content TEXT NOT NULL,
          view_count INT NOT NULL DEFAULT 0,
          archived BOOLEAN NOT NULL DEFAULT FALSE,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (user_id) REFERENCES users(user_id),
          FOREIGN KEY (category_id) REFERENCES categories(category_id),
          CHECK (CHAR_LENGTH(TRIM(title)) > 0),
          CHECK (CHAR_LENGTH(TRIM(content)) > 0)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
          comment_id INT AUTO_INCREMENT PRIMARY KEY,
          post_id INT NOT NULL,
          user_id INT NOT NULL,
          content TEXT NOT NULL,
          archived BOOLEAN NOT NULL DEFAULT FALSE,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
          FOREIGN KEY (post_id) REFERENCES posts(post_id),
          FOREIGN KEY (user_id) REFERENCES users(user_id),
          CHECK (CHAR_LENGTH(TRIM(content)) > 0)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
          like_id INT AUTO_INCREMENT PRIMARY KEY,
          post_id INT NOT NULL,
          user_id INT NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(post_id, user_id),
          FOREIGN KEY (post_id) REFERENCES posts(post_id),
          FOREIGN KEY (user_id) REFERENCES users(user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
          report_id INT AUTO_INCREMENT PRIMARY KEY,
          reporter_id INT NOT NULL,
          target_type ENUM('post', 'comment') NOT NULL,
          target_id INT NOT NULL,
          reason TEXT NOT NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY (reporter_id) REFERENCES users(user_id),
          CHECK (CHAR_LENGTH(TRIM(reason)) > 0)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    )


def _create_index_if_missing(cur, table_name, index_name, column_sql):
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
        """,
        (table_name, index_name),
    )
    exists = cur.fetchone()["cnt"]
    if not exists:
        cur.execute(f"CREATE INDEX {index_name} ON {table_name}({column_sql})")


def _create_indexes(cur):
    # 메인 페이지의 JOIN/GROUP BY 속도 개선용 인덱스
    _create_index_if_missing(cur, "posts", "idx_posts_user_id", "user_id")
    _create_index_if_missing(cur, "posts", "idx_posts_category_id", "category_id")
    _create_index_if_missing(cur, "posts", "idx_posts_archived", "archived")
    _create_index_if_missing(cur, "comments", "idx_comments_post_id", "post_id")
    _create_index_if_missing(cur, "comments", "idx_comments_user_id", "user_id")
    _create_index_if_missing(cur, "comments", "idx_comments_archived", "archived")
    _create_index_if_missing(cur, "likes", "idx_likes_post_id", "post_id")
    _create_index_if_missing(cur, "likes", "idx_likes_user_id", "user_id")
    _create_index_if_missing(cur, "users", "idx_users_grade_name", "grade_name")


def insert_default_data(cur):
    """등급 규칙, 카테고리, 관리자 계정을 없을 때만 삽입한다."""
    cur.executemany(
        """
        INSERT IGNORE INTO grade_rules
        (grade_name, min_post_count, min_comment_count, weight, can_view, can_interact)
        VALUES (%s, %s, %s, %s, %s, %s)
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
        "인사방": "신입 사용자가 인사글을 작성하고 확인하는 공간",
        "수업": "수업 관련 정보",
        "과제": "과제 관련 정보",
        "팀플": "팀플 관련 정보",
        "공지": "공지 관련 정보",
        "취업": "취업 관련 정보",
    }
    cur.executemany(
        """
        INSERT IGNORE INTO categories(category_name, description)
        VALUES (%s, %s)
        """,
        [(category, category_descriptions.get(category, "")) for category in CATEGORIES],
    )

    cur.execute(
        """
        INSERT IGNORE INTO users(username, password, profile_id, role, grade_name)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (ADMIN_ID, ADMIN_PW, "admin", "admin", "관리자"),
    )
    cur.execute(
        """
        UPDATE users
        SET password=%s, profile_id=%s, role=%s, grade_name=%s
        WHERE username=%s
        """,
        (ADMIN_PW, "admin", "admin", "관리자", ADMIN_ID),
    )
