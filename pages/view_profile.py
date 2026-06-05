from project_final.pages.page import Page
import management.management_posts
import management.management_comments
import pages.SNS_home as SNS_home

class ViewProfile(Page):
    def display_menu(self, user):
        print('''\n<프로필>
1. 회원 정보(계정 정보) 보기
2. 자신의 글 관리
3. 이전 메뉴로 돌아가기
        ''')
        self.user = user

    def handle_choice(self, choice, user):
        if choice == "1":
            self.view_profile_info()
            self.page_function(user)
        elif choice == "2":
            select_my_post_page.page_function(user)
        elif choice == "3":
            SNS_home.home_page.page_function(user)
        else:
            print("유효한 선택을 입력하세요.")
            self.page_function(user)

    def view_profile_info(self):
        print(f"\n<회원 정보(계정 정보)>")
        print(f"사용자 이름: {self.user['username']}\n이름: {self.user['name']}\n나이: {self.user['age']}\n전화번호: {self.user['phone']}\nSNS 프로필: {self.user['sns_profile']}\n")

    def page_function(self, user):
        return super().page_function(user)

view_profile_page = ViewProfile()


# 내 글 선택
class SelectMyPost(Page):
    def display_menu(self, user):
        print('''\n<내글 선택>
관리할 글을 선택하세요
(종료하려면 0을 입력하세요)              
        ''')

    def handle_choice(self, choice, user, select_posts):
        if choice == "0":
            SNS_home.home_page.page_function(user)
            return
        try:
            choice = int(choice) - 1
            if 0 <= choice < len(select_posts):
                self.view_post(choice, select_posts)
                post_id = select_posts[choice][0]
                select_post_my_page_action.page_function(user, post_id)
            else:
                print("유효한 번호를 입력하세요.")
                self.page_function(user, select_posts)                
        except ValueError:
            print("유효한 번호를 입력하세요.")
            self.page_function(user, select_posts)
    
    def view_post(self, choice, select_posts):
        post = select_posts[choice]
        post_id = post[0]  # id
        title = post[1]  # title
        content = post[2]  # content
        sns_profile = post[3]  # sns_profile
        timestamp = post[4]  # timestamp
        
        print(f"\n선택한 글: {title}")
        print(f"내용: {content}")
        print(f"작성자: {sns_profile}")
        print(f"작성일: {timestamp}")
        
        comments = management.management_posts.posts_manager.get_post_comments(post_id)
        print("\n<댓글 목록>")
        for comment in comments:
            print(f"{comment['timestamp']} - {comment['sns_profile']}: {comment['content']}")

    def page_function(self, user):
        select_posts = management.management_posts.posts_manager.get_user_posts(user['sns_profile'])
        if len(select_posts) == 0:
            print("작성한 글이 없습니다.")
            SNS_home.home_page.page_function(user)
        else:
            management.management_posts.posts_manager.view_posts(select_posts)
            while True:
                self.display_menu(user)
                choice = input("> ")
                self.handle_choice(choice, user, select_posts)

select_my_post_page = SelectMyPost()


# 내 글 관리 _ 세부사항   
class SelectMyPostAction(Page):
    def display_menu(self, user):
        print('''
1. 글 삭제
2. 글 보관 / 복원
3. 댓글 관리
4. 이전 메뉴로 돌아가기
              ''')

    def handle_choice(self, choice, user, post_id):
        if choice == "1":
            management.management_posts.posts_manager.delete_post(post_id)
            self.page_function(user, post_id)
        elif choice == "2":
            management.management_posts.posts_manager.archive_or_restore_post(post_id)
            self.page_function(user, post_id)
        elif choice == "3":
            self.manage_comments(post_id)
            self.page_function(user, post_id)            
        elif choice == "4":
            select_my_post_page.page_function(user)
        else:
            print("유효한 번호를 입력하세요.")
        self.page_function(user, post_id)

    def manage_comments(self, post_id):
        comments = management.management_posts.posts_manager.get_post_comments(post_id)
        print(comments)
        if comments:
            print("\n<댓글 목록>")
            for idx, comment in enumerate(comments, start=1):
                print(f"{idx}. {comment['timestamp']} - {comment['sns_profile']}: {comment['content']}")
            comment_choice = int(input("삭제할 댓글 번호를 입력하세요: ")) - 1
            if 0 <= comment_choice < len(comments):
                comment_id = comments[comment_choice]['id']
                management.management_comments.comments_manager.delete_comment(comment_id)
                print("댓글이 삭제되었습니다.")
            else:
                print("유효한 번호를 입력하세요.")
        else:
            print("삭제할 댓글이 없습니다.")

    def page_function(self, user, post_id=None):
        if post_id is not None:
            while True:
                self.display_menu(user)
                choice = input("> ")
                self.handle_choice(choice, user, post_id)

select_post_my_page_action = SelectMyPostAction()