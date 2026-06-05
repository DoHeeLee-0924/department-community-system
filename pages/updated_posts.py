from project_final.pages.page import Page
import management.management_posts
import pages.SNS_home as SNS_home
import pages.select_post as select_post

class UpdatedPosts(Page):
    def display_menu(self, user):
        print('''\n<업데이트된 글 보기>
1. 최신순
2. 좋아요순
3. 댓글순
4. 태그별 조회
5. 정보 신뢰도순 조회
6. 이전 메뉴로 돌아가기
              ''')

    def handle_choice(self, choice, user):
        if choice == "1":
            recent_posts = management.management_posts.posts_manager.get_recent_posts()
            management.management_posts.posts_manager.view_posts(recent_posts)
            select_post.select_post_page.page_function(user, recent_posts)
            self.page_function(user)
        elif choice == "2":
            popular_posts_by_likes = management.management_posts.posts_manager.get_popular_posts_by_likes()
            management.management_posts.posts_manager.view_posts(popular_posts_by_likes)
            select_post.select_post_page.page_function(user, popular_posts_by_likes)
            self.page_function(user)
        elif choice == "3":
            popular_posts_by_comments = management.management_posts.posts_manager.get_popular_posts_by_comments()
            management.management_posts.posts_manager.view_posts(popular_posts_by_comments)
            select_post.select_post_page.page_function(user, popular_posts_by_comments)
            self.page_function(user)
        elif choice == "4":
            category_posts = self.select_category_posts()
            management.management_posts.posts_manager.view_posts(category_posts)
            select_post.select_post_page.page_function(user, category_posts)
            self.page_function(user)
        elif choice == "5":
            trust_posts = self.select_trust_posts()
            management.management_posts.posts_manager.view_posts(trust_posts)
            select_post.select_post_page.page_function(user, trust_posts)
            self.page_function(user)
        elif choice == "6":
            SNS_home.home_page.page_function(user)
        else:
            print("올바른 선택이 아닙니다. 다시 시도해 주세요.")
            self.page_function(user)

    def select_category(self):
        categories = management.management_posts.posts_manager.get_categories()
        print("\n조회할 태그를 선택하세요.")
        for idx, category in enumerate(categories, start=1):
            print(f"{idx}. {category}")
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        print("올바른 태그를 선택하지 않아 전체 조회로 전환합니다.")
        return None

    def select_category_posts(self):
        category = self.select_category()
        if category:
            return management.management_posts.posts_manager.get_posts_by_category(category)
        return management.management_posts.posts_manager.get_recent_posts()

    def select_trust_posts(self):
        category = self.select_category()
        return management.management_posts.posts_manager.get_trust_ranked_posts(category)

    def page_function(self, user):
        return super().page_function(user)

updated_posts_page = UpdatedPosts()
