import sqlite3
from datetime import datetime

class Comments:
    def __init__(self, db_name='user_data.db'):
        """
        초기화
         
        데이터베이스 연결을 설정하고 댓글 테이블을 생성

        매개변수:
            db_name (str): 사용할 데이터베이스의 이름, 기본값은 'user_data.db'
        """

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_comment_table()

    def create_comment_table(self):
        """
        comments 테이블을 생성
        
        테이블이 이미 존재하는 경우, 아무 작업도 수행되지 않음

        매개변수: 없음

        반환값: 없음
        """     

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                sns_profile TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        ''')
        self.conn.commit()


    def get_user_comments(self, post_id, sns_profile):
        """
        사용자가 특정 게시물에 작성한 댓글을 가져옴

        매개변수:
            post_id (int): 댓글을 가져올 게시물의 ID
            sns_profile (str): 댓글을 작성한 사용자의 SNS 프로필 ID

        반환값:
            list: 댓글 정보를 담은 리스트
        """    

        self.cursor.execute('''
            SELECT id, timestamp, content
            FROM comments
            WHERE post_id = ? AND sns_profile = ?
        ''', (post_id, sns_profile))
        user_comments =  self.cursor.fetchall()
        return [{'id': comment[0], 'timestamp' : comment[1], 'content':comment[2]} for comment in user_comments]

    def add_comment(self, post_id, sns_profile, content):
        """
        게시물에 댓글을 추가

        댓글을 추가하고 댓글수도 업데이트 시킴

        매개변수:
            post_id (int): 댓글을 추가할 게시물의 ID
            sns_profile (str): 댓글을 작성한 사용자의 SNS 프로필 ID
            content (str): 댓글 내용

        반환값: 없음
        """

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO comments (post_id, sns_profile, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (post_id, sns_profile, content, timestamp))
        self.cursor.execute('''
            UPDATE posts
            SET comments = comments + 1
            WHERE id = ?
        ''', (post_id,))
        self.conn.commit()
        print("댓글이 추가되었습니다.")

    def delete_comment(self, comment_id):
        """
        댓글을 삭제

        댓글 삭제 후 댓글 수 업데이트

        매개변수:
            comment_id (int): 삭제할 댓글의 ID

        반환값: 없음
        """

        self.cursor.execute('''
            SELECT post_id FROM comments WHERE id = ?
        ''', (comment_id,))
        post_id = self.cursor.fetchone()
        if post_id:
            post_id = post_id[0]
            self.cursor.execute('''
                DELETE FROM comments WHERE id = ?
            ''', (comment_id,))
            self.cursor.execute('''
                UPDATE posts
                SET comments = comments - 1
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
        
comments_manager = Comments()