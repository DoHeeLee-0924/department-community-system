from project_final.pages.page import Page
import management.management_users
import pages.SNS_home as SNS_home
import sys

# 로그인 / 회원가입 선택 페이지
class Login_or_Register(Page):
    def display_menu(self):
        print('''\n<로그인 / 회원가입>
1. 로그인
2. 회원가입
3. 종료
              ''')

    def handle_choice(self, choice):
        if choice == "1":
            login_page.page_function()
        elif choice == "2":
            register_page.page_function()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            management.management_users.user_manager.close()
            sys.exit()
        else:
            print("올바른 선택이 아닙니다. 다시 시도해 주세요.")
            self.page_function()
    
    def page_function(self):
        try:
            while True:
                self.display_menu()
                choice = input("> ")
                self.handle_choice(choice)
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
        finally:
            management.management_users.user_manager.close()

login_or_register = Login_or_Register()

# 로그인
class LoginPage(Login_or_Register):
    def page_function(self):
        print('\n<로그인>')
        username = input("사용자 이름(아이디)을(를) 입력하세요: ")
        password = input("비밀번호를 입력하세요: ")
        user = management.management_users.user_manager.login(username, password)
        if user:
            print(f"\n{user['sns_profile']}님 환영합니다!")
            SNS_home.home_page.page_function(user)
        else:
            print("로그인에 실패했습니다. 다시 시도해 주세요.")
            login_or_register.page_function()

login_page = LoginPage()

# 회원가입
class RegisterPage(Login_or_Register):
    def page_function(self):
        print('\n<회원가입>')
        username = input("사용자 이름(아이디)을(를) 입력하세요: ")
        password = input("비밀번호를 입력하세요: ")
        name = input("이름: ")
        age = input("나이: ")
        phone = input("전화번호: ")
        sns_profile = input("SNS 상 프로필 ID: ")
        print("작성자 등급을 선택하세요. 1. 일반  2. 우수멘토  3. 학생회")
        role_choice = input("> ")
        role = {'1': '일반', '2': '우수멘토', '3': '학생회'}.get(role_choice, '일반')
        management.management_users.user_manager.register(username, password, name, age, phone, sns_profile, role)
        login_or_register.page_function()

register_page = RegisterPage()
