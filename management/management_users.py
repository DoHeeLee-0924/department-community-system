import sqlite3

class UserManagement:
    def __init__(self, db_name='user_data.db'):
        """
        초기화
         
        데이터베이스 연결을 설정하고 사용자 테이블을 생성

        매개변수:
            db_name (str): 사용할 데이터베이스의 이름, 기본값은 'user_data.db'
        """

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_user_table()


    def create_user_table(self):
        """
        users 테이블을 생성
        
        테이블이 이미 존재하는 경우, 아무 작업도 수행되지 않음

        매개변수: 없음

        반환값: 없음
        """

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT,
                age TEXT,
                phone TEXT,
                sns_profile TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT '일반'
            )
        ''')
        self.conn.commit()
        self._add_column_if_missing('users', 'role', "TEXT DEFAULT '일반'")

    def _add_column_if_missing(self, table_name, column_name, column_type):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in self.cursor.fetchall()]
        if column_name not in columns:
            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            self.conn.commit()


    def register(self, username=None, password=None, name=None, age=None, phone=None, sns_profile=None, role='일반'):
        """
        새로운 사용자를 등록(회원가입)

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            password (str): 사용자의 비밀번호
            name (str): 사용자의 이름
            age (str): 사용자의 나이
            phone (str): 사용자의 전화번호
            sns_profile (str): 사용자의 SNS 프로필 ID

        반환값: 없음
        """
        if not username or not password:
            print("사용자 이름과 비밀번호는 필수 항목입니다.\n")
            return

        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, name, age, phone, sns_profile, role) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, name, age, phone, sns_profile, role))
            self.conn.commit()
            print("계정이 생성되었습니다.")
            print("로그인 창으로 넘어가세요.\n")
        except sqlite3.IntegrityError:
            print('이미 사용하고 있는 사용자 이름 또는 SNS 프로필입니다.\n다시 "회원가입" 하세요')
            print()


    def login(self, username, password):
        """
        사용자 로그인 처리

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            password (str): 사용자의 비밀번호

        반환값:
            dict: 사용자 정보를 포함한 딕셔너리
            로그인 실패 시 None 반환
        """

        self.cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user_data = self.cursor.fetchone()
        if user_data:
            name, age, phone, sns_profile = user_data[2], user_data[3], user_data[4], user_data[5]
            role = user_data[6] if len(user_data) > 6 and user_data[6] else '일반'
            
            if not sns_profile:
                sns_profile = input("SNS 상 프로필 ID: ")
                self.update_user_info(username, name, age, phone, sns_profile)
            
            if not name or not age or not phone:
                print("추가 정보를 입력하세요.")
                if not name:
                    name = input("이름: ")
                if not age:
                    age = input("나이: ")
                if not phone:
                    phone = input("전화번호: ")
                self.update_user_info(username, name, age, phone, sns_profile)
                user_data = (username, password, name, age, phone, sns_profile, role)
            
            print("로그인 성공!\n")
            return {
                'username': user_data[0],
                'password': user_data[1],
                'name': name,
                'age': age,
                'phone': phone,
                'sns_profile': sns_profile,
                'role': role
            }
        else:
            print("잘못된 사용자 이름 또는 비밀번호입니다.\n")
            return None


    def update_user_info(self, username, name, age, phone, sns_profile):
        """
        사용자 정보 업데이트

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            name (str): 사용자의 이름
            age (str): 사용자의 나이
            phone (str): 사용자의 전화번호
            sns_profile (str): 사용자의 SNS 프로필 ID

        반환값: 없음
        """

        try:
            self.cursor.execute('''
                UPDATE users SET name=?, age=?, phone=?, sns_profile=?
                WHERE username=?
            ''', (name, age, phone, sns_profile, username))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print('이미 사용하고 있는 SNS 프로필입니다. 다른 프로필을 사용하세요.\n')


    def check(self, username, password):
        """
        사용자 확인여부 

        비밀번호 변경 전 사용자를 확인하기 위해서 기존 비밀번호를 확인

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            password (str): 사용자의 비밀번호

        반환값:
            dict: 사용자 정보를 포함한 딕셔너리
            사용자 확인에 실패하면 None 반환
        """

        self.cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user_data = self.cursor.fetchone()
        if user_data:
            return {
                'username': user_data[0],
                'password': user_data[1],
                'name': user_data[2],
                'age': user_data[3],
                'phone': user_data[4],
                'sns_profile': user_data[5],
                'role': user_data[6] if len(user_data) > 6 and user_data[6] else '일반'
            }
        else:
            return None


    def update_password(self, username, new_password):
        """
        사용자의 비밀번호를 업데이트

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            new_password (str): 새로운 비밀번호

        반환값: 없음
        """

        self.cursor.execute('''
            UPDATE users SET password=?
            WHERE username=?
        ''', (new_password, username))
        self.conn.commit()


    def update_sns_profile(self, username, new_sns_profile):
        """
        사용자의 SNS 프로필 ID를 업데이트

        매개변수:
            username (str): 사용자의 사용자 이름(로그인시 ID)
            new_sns_profile (str): 새로운 SNS 프로필 ID

        반환값: 없음
        """

        try:
            self.cursor.execute('''
                UPDATE users SET sns_profile=?
                WHERE username=?
            ''', (new_sns_profile, username))
            self.conn.commit()
            print("SNS 상 프로필 ID가 변경되었습니다.")
        except sqlite3.IntegrityError:
            print('이미 사용하고 있는 SNS 프로필입니다. 다른 프로필을 사용하세요.\n')


    def delete_user(self, sns_profile):
        """
        데이터베이스에서 사용자와 관련된 모든 데이터를 삭제

        1. 사용자가 댓글을 단 모든 게시물의 `posts` 테이블에서 `comments` 수를 업데이트
            (계정 삭제시 사용자가 단 댓글도 지워지기 때문에 comments(게시물의 댓글 수)도 업데이트 해야함)
        2. 사용자가 좋아요를 누른 모든 게시물의 `posts` 테이블에서 `likes` 수를 업데이트
            (계정 삭제시 사용자가 누른 좋아요도 지워지기 때문에 likes(게시물의 좋아요 수)도 업데이트 해야함)
        3. `users` 테이블에서 사용자를 삭제
        4. 사용자가 작성한 모든 게시물, 댓글 및 좋아요를 삭제

        매개변수:
            sns_profile (str): 사용자의 SNS 프로필 ID

        반환값: 없음
        """
        self.cursor.execute('''
            SELECT post_id FROM comments
            WHERE sns_profile = ?
        ''', (sns_profile,))
        comment_posts = self.cursor.fetchall()

        for post_id in comment_posts:
            self.cursor.execute('''
                UPDATE posts
                SET comments = comments - 1
                WHERE id = ?
            ''', (post_id[0],))

        self.cursor.execute('''
            SELECT post_id FROM likes
            WHERE sns_profile = ?
        ''', (sns_profile,))
        liked_posts = self.cursor.fetchall()

        for post_id in liked_posts:
            self.cursor.execute('''
                UPDATE posts
                SET likes = likes - 1
                WHERE id = ?
            ''', (post_id[0],))

        self.cursor.execute('''
            DELETE FROM users WHERE sns_profile = ?
        ''', (sns_profile,))
        self.cursor.execute('''
            DELETE FROM posts WHERE sns_profile = ?
        ''', (sns_profile,))
        self.cursor.execute('''
            DELETE FROM comments WHERE sns_profile = ?
        ''', (sns_profile,))
        self.cursor.execute('''
            DELETE FROM likes WHERE sns_profile = ?
        ''', (sns_profile,))
        self.conn.commit()


    def close(self):
        """ 
        데이터베이스 연결 종료

        매개변수: 없음

        반환값: 없음
        """
        self.conn.close()


user_manager = UserManagement()
