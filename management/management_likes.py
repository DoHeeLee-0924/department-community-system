import sqlite3

class Likes:
    def __init__(self, db_name='user_data.db'):
        """
        초기화
         
        데이터베이스 연결을 설정하고 좋아요 테이블을 생성

        매개변수:
            db_name (str): 사용할 데이터베이스의 이름, 기본값은 'user_data.db'
        """

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_like_table()

    def create_like_table(self):
        """
        likes 테이블을 생성
        
        테이블이 이미 존재하는 경우, 아무 작업도 수행되지 않음

        매개변수: 없음

        반환값: 없음
        """

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                sns_profile TEXT NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        ''')
        self.conn.commit()

    def like_post(self, post_id, sns_profile):
        """
        게시물에 좋아요를 추가

        post_id와 sns_profile을 받아서 already_liked == 0일 경우에만 좋아요 추가
        already_liked == 1일 경우에는 좋아요 추가 할 수 없음
        좋아요를 추가하면 좋아요수 업데이트

        매개변수:
            post_id (int): 좋아요를 추가할 게시물의 ID
            sns_profile (str): 좋아요를 누른 사용자의 SNS 프로필 ID

        반환값: 없음
        """

        self.cursor.execute('''
            SELECT COUNT(*) FROM likes
            WHERE post_id = ? AND sns_profile = ?
        ''', (post_id, sns_profile))
        already_liked = self.cursor.fetchone()[0]

        if already_liked == 0:
            self.cursor.execute('''
                INSERT INTO likes (post_id, sns_profile)
                VALUES (?, ?)
            ''', (post_id, sns_profile))
            self.cursor.execute('''
                UPDATE posts
                SET likes = likes + 1
                WHERE id = ?
            ''', (post_id,))
            self.conn.commit()
            print("좋아요를 추가했습니다.")
        else:
            print("이미 좋아요를 누른 게시물입니다.")


    def unlike_post(self, post_id, sns_profile):
        """
        게시물에 좋아요를 취소

        post_id와 sns_profile을 받아서 already_liked == 1일 경우에만 좋아요 취소 가능
        already_liked == 0일 경우에는 좋아요 취소 할 수 없음
        좋아요를 취소하면 좋아요수 업데이트 
        
        매개변수:
            post_id (int): 좋아요를 추가할 게시물의 ID
            sns_profile (str): 좋아요를 누른 사용자의 SNS 프로필 ID

        반환값: 없음
        """        

        self.cursor.execute('''
            SELECT COUNT(*) FROM likes
            WHERE post_id = ? AND sns_profile = ?
        ''', (post_id, sns_profile))
        liked = self.cursor.fetchone()[0]

        if liked == 1:
            self.cursor.execute('''
                DELETE FROM likes
                WHERE post_id = ? AND sns_profile = ?
            ''', (post_id, sns_profile))
            self.cursor.execute('''
                UPDATE posts
                SET likes = likes - 1
                WHERE id = ?
            ''', (post_id,))
            self.conn.commit()
            print("좋아요를 취소했습니다.")
        else:
            print("좋아요를 누른 게시물이 아닙니다.")
 

    def close(self):
        """ 
        데이터베이스 연결 종료

        매개변수: 없음

        반환값: 없음
        """        
        self.conn.close()

likes_manager = Likes()
