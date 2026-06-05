from project_final.pages.page import Page
import management.management_posts
import pages.SNS_home as SNS_home
import pages.select_post as select_post
# 검색창

class Search(Page):
    def display_menu(self, user):
        print('''\n<검색창>
1. 내용 검색
2. ID 검색
3. 이전 메뉴로 돌아가기
              ''')

    def handle_choice(self, choice, user):
        if choice == "1":
            query = input("검색어를 입력하세요: ")
            results = management.management_posts.posts_manager.search_posts(query)
            management.management_posts.posts_manager.view_posts(results)
            select_post.select_post_page.page_function(user, results)
            self.page_function(user)

        elif choice == "2":
            sns_id = input("검색할 SNS ID를 입력하세요: ")
            users = management.management_posts.posts_manager.search_users(sns_id)
            print(f'"{sns_id}"에 대한 검색 결과:')
            if len(users) == 0:
                print("존재하지 않는 SNS ID 입니다.")
            else:
                for idx, user in enumerate(users, start=1):
                    print(f"{idx}. ID: {user['sns_profile']}, 이름: {user['name']}")
                sns_id_choice = int(input("글을 보고 싶은 SNS ID의 번호를 선택하세요: "))
                if 1 <= sns_id_choice <= len(users):
                    user_posts = management.management_posts.posts_manager.get_user_posts(users[sns_id_choice - 1]['sns_profile'])
                    management.management_posts.posts_manager.view_posts(user_posts)
                    select_post.select_post_page.page_function(user, user_posts) 
                    self.page_function(user)
                else:
                    print("유효한 번호를 선택하세요.")
        elif choice == "3":
            SNS_home.home_page.page_function(user)
        else:
            print("올바른 선택이 아닙니다. 다시 시도해 주세요.")
            self.page_function(user)
        
    def page_function(self, user):
        return super().page_function(user)

search_page = Search()
