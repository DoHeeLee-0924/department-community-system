from project_final.pages.page import Page
import management.management_users
import pages.SNS_home as SNS_home
import pages.login_or_register as login_or_register

# 설정
class Settings(Page):
    def display_menu(self, user):
        print('''\n<설정>
1. 비밀번호 변경
2. SNS 상 프로필 ID 변경
3. 회원 탈퇴 후 로그아웃
4. 이전 메뉴로 돌아가기
              ''')

    def handle_choice(self, choice, user):
        if choice == "1":
            self.change_password(user)
        elif choice == "2":
            self.change_sns_profile(user)
        elif choice == "3":
            self.delete_account(user)
            login_or_register.login_or_register.page_function()
        elif choice == "4":
            SNS_home.home_page.page_function(user)
        else:
            print("올바른 선택이 아닙니다. 다시 시도해 주세요.")
            self.page_function(user)
    
    def page_function(self, user):
        return super().page_function(user)

    def change_password(self, user):
        old_password = input("기존 비밀번호를 입력하세요: ")
        if management.management_users.user_manager.check(user['username'], old_password):
            new_password = input("새 비밀번호를 입력하세요: ")
            management.management_users.user_manager.update_password(user['username'], new_password)
            print("비밀번호가 변경되었습니다.")
            self.page_function(user)
        else:
            print("기존 비밀번호가 일치하지 않습니다.")
            self.page_function(user)

    def change_sns_profile(self, user):
        new_sns_profile = input("새 SNS 상 프로필 ID를 입력하세요: ")
        management.management_users.user_manager.update_sns_profile(user['username'], new_sns_profile)
        user['sns_profile'] = new_sns_profile
        self.page_function(user)

    def delete_account(self, user):
        confirm = input("정말로 회원 탈퇴하시겠습니까? (y/n): ")
        if confirm.lower() == 'y':
            management.management_users.user_manager.delete_user(user['sns_profile'])
            print("회원 탈퇴가 완료되었습니다.")
        else:
            self.page_function(user)
    
settings_page = Settings()