import pages.login_or_register
import management.management_users

if __name__ == "__main__":
    try:
        pages.login_or_register.login_or_register.page_function()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
    finally:
        management.management_users.user_manager.close()


# pydoc으로 메소드별 설명 쓰고
# md 파일에는 개요, 테이블(col _ 이름, 타입), 어떻게 흘러가는지 쓰기
# post id 는 참조

