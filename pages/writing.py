from project_final.pages.page import Page
import management.management_posts
import pages.SNS_home as SNS_home
from datetime import datetime


class Writing(Page):
    def page_function(self, user):
        post_title = input("글 제목을 입력하세요: ").strip()
        post_content = input("글 내용을 입력하세요: ").strip()

        categories = management.management_posts.posts_manager.get_categories()
        print("\n태그를 선택하세요. 태그 선택은 필수입니다.")
        for idx, category in enumerate(categories, start=1):
            print(f"{idx}. {category}")
        category_choice = input("> ").strip()

        if not post_title or not post_content or not category_choice.isdigit():
            print("제목, 내용, 태그를 모두 입력해야 글을 등록할 수 있습니다.\n")
            self.page_function(user)
            return

        category_idx = int(category_choice) - 1
        if category_idx < 0 or category_idx >= len(categories):
            print("올바른 태그를 선택해야 글을 등록할 수 있습니다.\n")
            self.page_function(user)
            return

        category = categories[category_idx]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        management.management_posts.posts_manager.write_post(
            user['sns_profile'], post_title, post_content, timestamp, category
        )
        print(f"\n{user['sns_profile']}님이 작성한 [{category}] 글이 저장되었습니다.\n")
        SNS_home.home_page.page_function(user)

writing_page = Writing()
