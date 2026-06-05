import sqlite3
from datetime import datetime

class Posts:
    CATEGORIES = ['수업', '과제', '팀플', '공지', '취업']
    ROLE_WEIGHTS = {'학생회': 3.0, '우수멘토': 2.0, '일반': 1.0}

    def __init__(self, db_name='user_data.db'):
        """
        초기화
         
        데이터베이스 연결을 설정하고 게시물 테이블을 생성

        매개변수:
            db_name (str): 사용할 데이터베이스의 이름, 기본값은 'user_data.db'
        """     

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_post_table()



    def create_post_table(self):
        """
        posts 테이블을 생성
        
        테이블이 이미 존재하는 경우, 아무 작업도 수행되지 않음

        매개변수: 없음

        반환값: 없음
        """

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sns_profile TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '수업',
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0,
                FOREIGN KEY(sns_profile) REFERENCES users(sns_profile)
            )
        ''')
        self.conn.commit()

        # 기존 DB를 그대로 사용할 수 있도록 필요한 컬럼만 추가한다.
        self._add_column_if_missing('posts', 'category', "TEXT NOT NULL DEFAULT '수업'")
        self._add_column_if_missing('posts', 'view_count', 'INTEGER DEFAULT 0')

    def _add_column_if_missing(self, table_name, column_name, column_type):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in self.cursor.fetchall()]
        if column_name not in columns:
            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            self.conn.commit()


    def get_user_posts(self, sns_profile):
        """
        특정 사용자가 작성한 게시물을 가져옴

        매개변수:
            sns_profile (str): 게시물을 작성한 사용자의 SNS 프로필 ID

        반환값:
            list: 해당 사용자가 작성한 게시물의 정보를 포함하는 리스트
        """

        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS likes,
                (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comments,
                p.category,
                COALESCE(u.role, '일반') AS role,
                p.view_count,
                p.archived
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE p.sns_profile = ?
            ORDER BY p.timestamp DESC
        ''', (sns_profile,))
        posts = self.cursor.fetchall()
        return posts


    def get_recent_posts(self):
        """
        최신순으로 게시물을 가져옴

        매개변수: 없음

        반환값:
            list: 해당 조건(최신순)을 만족하는 게시물의 정보를 포함하는 리스트
        """

        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE p.archived = 0
            ORDER BY p.timestamp DESC
            LIMIT 5
        ''')
        posts = self.cursor.fetchall()
        return posts


    def get_popular_posts_by_likes(self):
        """
        좋아요순으로 게시물을 가져옴

        매개변수: 없음

        반환값:
            list: 해당 조건(좋아요순)을 만족하는 게시물의 정보를 포함하는 리스트
        """        

        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE p.archived = 0
            ORDER BY p.likes DESC, p.timestamp DESC
            LIMIT 5
        ''')
        posts = self.cursor.fetchall()
        return posts


    def get_popular_posts_by_comments(self):
        """
        댓글순으로 게시물을 가져옴

        매개변수: 없음

        반환값:
            list: 해당 조건(댓글순)을 만족하는 게시물의 정보를 포함하는 리스트
        """            

        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE p.archived = 0
            ORDER BY p.comments DESC, p.timestamp DESC
            LIMIT 5
        ''')
        posts = self.cursor.fetchall()
        return posts

    def view_posts(self, posts):
        """
        게시물 목록을 화면에 출력

        매개변수:
            posts (list): 출력할 게시물 정보를 담은 리스트

        반환값: 없음
        """

        keys = ['id', 'title', 'content', 'sns_profile', 'timestamp', 'likes', 'comments',
                'category', 'role', 'view_count', 'trust_score', 'exposure_status']
        posts = [dict(zip(keys, post)) for post in posts]

        for idx, post in enumerate(posts, start=1):
            print(f"\n{idx}. 글 제목: {post['title']}")
            if post.get('category'):
                print(f"태그: {post['category']}")
            print(f"내용: {post['content']}")
            print(f"작성자: {post['sns_profile']}")
            if post.get('role'):
                print(f"작성자 등급: {post['role']}")
            print(f"작성일: {post['timestamp']}")
            print(f"좋아요수: {post['likes']}")
            print(f"댓글수: {post['comments']}")
            if post.get('view_count') is not None:
                print(f"조회수: {post['view_count']}")
            if post.get('trust_score') is not None:
                print(f"정보 신뢰도 점수: {round(post['trust_score'], 1)}")
            if post.get('exposure_status'):
                print(f"노출 상태: {post['exposure_status']}")


    def get_post_comments(self, post_id):
        """
        특정 게시물의 댓글을 가져옴

        매개변수:
            post_id (int): 댓글을 가져올 게시물의 ID

        반환값:
            list: 게시물의 댓글 정보를 담은 리스트
        """        

        self.cursor.execute('''
            SELECT id, sns_profile, content, timestamp
            FROM comments
            WHERE post_id = ?
            ORDER BY timestamp ASC
        ''', (post_id,))
        comments = self.cursor.fetchall()
        return [{'id': comment[0], 'sns_profile': comment[1], 'content': comment[2], 'timestamp': comment[3]} for comment in comments]    


    def delete_post(self, post_id):
        """
        글을 삭제

        매개변수:
            post_id (int): 삭제할 글의 ID

        반환값: 없음
        """       

        confirm = input(f"정말로 글을 삭제하시겠습니까? (y/n): ")
        if confirm.lower() == 'y':
            self.cursor.execute('''
                DELETE FROM posts WHERE id = ?
            ''', (post_id,))
            self.cursor.execute('''
                DELETE FROM comments WHERE post_id = ?
            ''', (post_id,))
            self.cursor.execute('''
                DELETE FROM likes WHERE post_id = ?
            ''', (post_id,))
            self.conn.commit()
            print("글이 삭제되었습니다.")
        else:
            print("글 삭제가 취소되었습니다.")


    def archive_or_restore_post(self, post_id):
        """
        글을 보관 또는 복원

        매개변수:
            post_id (int): 보관 또는 복원할 글의 ID

        반환값: 없음
        """

        self.cursor.execute('SELECT archived FROM posts WHERE id = ?', (post_id,))
        post = self.cursor.fetchone()

        if post is None:
            print("해당 글을 찾을 수 없습니다.")
            return

        archived_status = post[0] 

        if archived_status == 0:
            confirm_archive = input("글을 보관할까요? (y/n): ")
            if confirm_archive.lower() == 'y':
                self.cursor.execute('UPDATE posts SET archived = 1 WHERE id = ?', (post_id,))
                self.cursor.connection.commit()
                print("글이 보관되었습니다.")
        else:
            confirm_restore = input("이미 보관된 글입니다. 복원할까요? (y/n): ")
            if confirm_restore.lower() == 'y':
                self.cursor.execute('UPDATE posts SET archived = 0 WHERE id = ?', (post_id,))
                self.cursor.connection.commit()
                print("글이 복원되었습니다.")        
    
    def write_post(self, sns_profile, title, content, timestamp, category):
        """
        게시물을 작성

        매개변수:
            sns_profile (str): 게시물을 작성한 사용자의 SNS 프로필 ID
            title (str): 게시물의 제목
            content (str): 게시물의 내용
            timestamp (str): 게시물이 작성된 시각 (형식 : 'YYYY-MM-DD HH:MM:SS')

        반환값: 없음
        """

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO posts (sns_profile, title, content, timestamp, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (sns_profile, title, content, timestamp, category))
        self.conn.commit()


    def search_posts(self, query):
        """
        게시물을 검색

        매개변수:
            query (str): 검색어

        반환값:
            list: 검색어와 관련된 게시물의 정보를 포함하는 리스트
        """        

        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE (p.title LIKE ? OR p.content LIKE ?) AND p.archived = 0
            ORDER BY p.timestamp DESC
        ''', (f'%{query}%', f'%{query}%'))
        posts = self.cursor.fetchall()
        return posts


    def search_users(self, sns_id):
        """
        사용자를 검색

        매개변수:
            sns_id (str): 검색할 사용자의 SNS 프로필 ID

        반환값:
            list: 검색어와 관련된 사용자의 정보를 포함하는 리스트.
        """    

        self.cursor.execute('''
            SELECT username, name, sns_profile
            FROM users
            WHERE sns_profile LIKE ?
        ''', (f'%{sns_id}%',))
        users = self.cursor.fetchall()
        return [{'username': user[0], 'name': user[1], 'sns_profile': user[2]} for user in users]
    


    def get_categories(self):
        return self.CATEGORIES


    def get_posts_by_category(self, category):
        self.cursor.execute('''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            WHERE p.category = ? AND p.archived = 0
            ORDER BY p.timestamp DESC
            LIMIT 10
        ''', (category,))
        return self.cursor.fetchall()


    def get_trust_ranked_posts(self, category=None):
        where_clause = 'WHERE p.archived = 0'
        params = []
        if category:
            where_clause += ' AND p.category = ?'
            params.append(category)

        self.cursor.execute(f'''
            SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp,
                   p.likes, p.comments, p.category, COALESCE(u.role, '일반') AS role, p.view_count,
                   ((CASE COALESCE(u.role, '일반')
                        WHEN '학생회' THEN 3.0
                        WHEN '우수멘토' THEN 2.0
                        ELSE 1.0
                    END) * 10 + p.likes * 2 + p.comments * 1 + p.view_count * 0.1) AS trust_score,
                   CASE
                       WHEN ((CASE COALESCE(u.role, '일반')
                                WHEN '학생회' THEN 3.0
                                WHEN '우수멘토' THEN 2.0
                                ELSE 1.0
                             END) * 10 + p.likes * 2 + p.comments * 1 + p.view_count * 0.1) >= 30
                       THEN '상단 노출'
                       ELSE '일반 노출'
                   END AS exposure_status
            FROM posts p
            LEFT JOIN users u ON p.sns_profile = u.sns_profile
            {where_clause}
            ORDER BY
                CASE
                    WHEN COALESCE(u.role, '일반') = '학생회' AND p.category = '공지' THEN 1
                    ELSE 0
                END DESC,
                trust_score DESC,
                p.timestamp DESC
            LIMIT 10
        ''', params)
        return self.cursor.fetchall()


    def increment_view_count(self, post_id):
        self.cursor.execute('''
            UPDATE posts
            SET view_count = view_count + 1
            WHERE id = ?
        ''', (post_id,))
        self.conn.commit()


    def close(self):
        """
        데이터베이스 연결 종료

        매개변수: 없음

        반환값: 없음
        """
        self.conn.close()

posts_manager = Posts()