from project_final.pages.page import Page
import pages.view_profile as view_profile
import pages.updated_posts as updated_posts
import pages.writing as writing
import pages.search as search
import pages.settings as settings
import pages.login_or_register as login_or_register

# SNS 홈 
class Home(Page):
    def display_menu(self, user):
        print('''\n<SNS 메인 홈>
1. 자신의 프로필 보기
2. 업데이트된 글 보기
3. 글쓰기
4. 검색창
5. 설정
6. 로그아웃
        ''')
        self.user = user

    def handle_choice(self, choice, user):
        if choice == "1":
            view_profile.view_profile_page.page_function(user)
        elif choice == "2":
            updated_posts.updated_posts_page.page_function(user)
        elif choice == "3":
            writing.writing_page.page_function(user)
        elif choice == "4":
            search.search_page.page_function(user)
        elif choice == "5":
            settings.settings_page.page_function(user)
        elif choice == "6":
            print("로그아웃합니다.")
            login_or_register.login_or_register.page_function()
        else:
            print("유효한 선택을 입력하세요.")
            self.page_function(user)

    def page_function(self, user):
        return super().page_function(user)

home_page = Home()
