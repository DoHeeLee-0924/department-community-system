from project_final.pages.page import Page
import management.management_posts
import management.management_likes
import management.management_comments
import pages.SNS_home as SNS_home

# 글 선택

class SelectPost(Page):
    def display_menu(self, user):
        print('''\n<글 선택>
댓글을 달거나, 좋아요를 누르려면 글 번호를 입력하세요.
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
                select_post_page_action.page_function(user, post_id)
            else:
                print("유효한 번호를 입력하세요.")
                self.page_function(user, select_posts)                
        except ValueError:
            print("유효한 번호를 입력하세요.")
            self.page_function(user, select_posts)
    
    def view_post(self, choice, select_posts):
        post = select_posts[choice]
        post_id = post[0]
        title = post[1]
        content = post[2]
        sns_profile = post[3]
        timestamp = post[4]
        category = post[7] if len(post) > 7 else None
        role = post[8] if len(post) > 8 else None

        management.management_posts.posts_manager.increment_view_count(post_id)

        print(f"\n선택한 글: {title}")
        if category:
            print(f"태그: {category}")
        print(f"내용: {content}")
        print(f"작성자: {sns_profile}")
        if role:
            print(f"작성자 등급: {role}")
        print(f"작성일: {timestamp}")

        comments = management.management_posts.posts_manager.get_post_comments(post_id)
        print("\n<댓글 목록>")
        if len(comments) == 0:
            print("댓글이 없습니다.")
        else:
            for comment in comments:
                print(f"{comment['timestamp']} - {comment['sns_profile']}: {comment['content']}")

    def page_function(self, user, select_posts):
        if len(select_posts)== 0:
            print("업데이트 된 글이 없습니다.")
            SNS_home.home_page.page_function(user)
        else:
            while True:
                self.display_menu(user)
                choice = input("> ")
                self.handle_choice(choice, user, select_posts)
        
select_post_page = SelectPost()

# 글 선택 _  세부사항
    
class SelectPostAction(SelectPost):
    def display_menu(self, user):
        print('''
1. 댓글 달기
2. 좋아요 누르기
3. 내 댓글 삭제하기
4. 좋아요 취소하기
5. SNS 홈으로 돌아가기
              ''')

    def handle_choice(self, choice, user, post_id):
        if choice == "1":
            comment_content = input("댓글 내용을 입력하세요: ")
            management.management_comments.comments_manager.add_comment(post_id, user['sns_profile'], comment_content)
        elif choice == "2":
            management.management_likes.likes_manager.like_post(post_id, user['sns_profile'])
        elif choice == "3":
            self.delete_my_comments(post_id, user['sns_profile'])
        elif choice == "4":
            management.management_likes.likes_manager.unlike_post(post_id, user['sns_profile'])
        elif choice == "5":
            SNS_home.home_page.page_function(user)
        else:
            print("유효한 번호를 입력하세요.")
            self.page_function(user, post_id)

    def delete_my_comments(self, post_id, user):
        user_comments = management.management_comments.comments_manager.get_user_comments(post_id, user)
        if user_comments:
            print("\n<내 댓글 목록>")
            for idx, comment in enumerate(user_comments, start=1):
                print(f"{idx}. {comment['timestamp']} - {comment['content']}")
            comment_choice = int(input("삭제할 댓글 번호를 입력하세요: ")) - 1
            if 0 <= comment_choice < len(user_comments):
                comment_id = user_comments[comment_choice]['id']
                management.management_comments.comments_manager.delete_comment(comment_id)
                print("댓글이 삭제되었습니다.")
            else:
                print("유효한 번호를 입력하세요.")
        else:
            print("삭제할 댓글이 없습니다.")
    
    def page_function(self, user, post_id):
        while True:
            self.display_menu(user)
            choice = input("> ")
            self.handle_choice(choice, user, post_id)    

select_post_page_action = SelectPostAction()