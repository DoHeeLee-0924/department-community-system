# SNS 만들기

# 전체 개요
![Database](./outline.png)

# 데이터베이스 _ (user_data.db)
## 파일 구성
### main.py
프로그램 실행시 사용
(실행하면 로그인/회원가입 페이지로 넘어감)

## management_users.py
계정 정보 관리
- class UserManagement 사용
  - users 테이블 생성
  - register 메소드 : 회원가입
  - login 메소드 : 로그인
  - update_user_info 메소드 : 로그인시에 필요한 회원정보가 누락된 경우 입력받고 업데이트
  - check 메소드 : 설정(Settings)에서 비밀번호 변경시 기존 비밀번호 확인할때 사용
  - update_password 메소드 : 변경된 비밀번호 업데이트
  - update_sns_profile 메소드 : 변경된 sns_profile 업데이트
  - delete user 메소드 : 사용자 정보 삭제 _ user 정보 삭제시 user관련된 것들까지 다 삭제

  management_pages.py
  - 페이지 정보 관리
    class Page : 부모 클래스 생성

    < 로그인 / 회원가입 관련 >
    class Login_or_Register(Page) : 로그인 / 회원가입 선택 페이지
    class LoginPage(Login_or_Register) : 로그인 페이지 
    class RegisterPage(Login_or_Register) : 회원가입 페이지

    < SNS 홈 페이지 관련 >
    class Home(Page) : SNS 홈 페이지

    < 자신의 프로필 페이지 관련 >
    class ViewProfile(Page) : 자신의 프로필 페이지
    class SelectMyPost(ViewProfile) : 관리할 글 선택 페이지
    class SelectMyPostAction(SelectMyPost) : 관리할 글의 관리 기능 선택 페이지

    < 업데이트 된 글 보기 페이지 관련 >
    class UpdatedPosts(Page) : 업데이트 된 글 보는 방식 선택 페이지 -> SelectPost

    < 글 쓰기 페이지 관련 >
    class Writing(Page) : 게시물(글) 쓰기 페이지

    < 검색창 페이지 관련 >
    class Search(Page) : 검색창 페이지 -> SelectPost

    < 설정 페이지 관련 >
    class Settings(Page) : 설정 페이지 

    < 글 선택 페이지 관련 >
    class SelectPost(Page) : 글 선택 페이지
    class SelectPostAction(SelectPost) : 글 선택 후 기능 선택 페이지  



  management_posts.py
  - 게시물(글 정보) 관리
    class Posts
      posts 테이블 생성
      get_user_posts 메소드 : 특정 user의 글을 선택
      get_recent_posts 메소드 : 최신순으로 글을 선택
      get_popular_posts_by_likes 메소드 : 좋아요순으로 글을 선택
      get_popular_posts_by_comments 메소드 : 댓글순으로 글을 선택
      view_post 메소드 : 글을 형식으로 보여주기
      get_post_comments 메소드 : 글을 가져오기
      delete_post 메소드 : post_id 선택 후 글 삭제
      archive_or_restore_post 메소드 : post_id 선택 후 글을 보관 or 복원
      write_post 메소드 : 글쓰기
      serach_posts 메소드 : 내용으로 글 찾기
      search_users 메소드 : 아이디 검색

  management_likes.py
  - 게시물(좋아요) 관리
    class Likes
      likes 테이블 생성
      like_post 메소드 : 게시물에 좋아요 달기
      unlike_post 메소드 : 게시물 좋아요 취소하기


  management_comments.py
  - 게시물(댓글) 관리
    class Comments
      comments 테이블 생성
      get_user_comments 메소드 : 게시물에 단 내(특정 user의) 댓글 선택 
      delete_my_comment 메소드 : 게시물에 단 내 댓글 삭제 _ 글보기에서
      add_comment 메소드 : 댓글 달기
      delete_comment 메소드 : 내 게시물 댓글 관리(삭제) _ 자신의 프로필(글 관리)

# user_data.db
![Database](./table.png)


# 첫 화면(로그인 or 회원가입 선택)
  - 로그인
    > 사용자 이름, 비밀번호 입력
    > 회원가입 되어있는 사용자일 경우만 로그인

  - 회원가입
    > 사용자 이름, 비밀번호 생성 
    > 중복된 사용자 이름이라면 생성되지 않는다
    > 계정 생성 진행
      - 회원정보 입력받기(이름, 나이, 전화번호, sns상 프로필 ID)

# SNS 메인 홈(로그인 성공 후)
  - 자신의 프로필 보기
  - 업데이트된 글 보기
  - 글쓰기 (완료)
  - 검색창
  - 설정 (완료)

  # SNS 자신의 프로필
    - 회원 정보(계정 정보) 보기 _ (완성)
    - 자신의 글 관리 
      - 글 전체(삭제, 보관 등) _ (완성)
      - 글 댓글 or 좋아요 관리(삭제, 보관 등) ----> 이번주에 여기까지

  # SNS 업데이트된 글 보기(5~10개 정도만 표시)
    - 최신순
    - 좋아요순(좋아요 갯수 동일시 동일 갯수 내에 최신순)
    - 댓글순(댓글수 동일시 동일 갯수 내에 최신순)
    # 댓글달기
      - 댓글 입력받기
    # 좋아요달기
      - 좋아요 받기
    
    ------
    <example>
    (2024년 01월 01일 00:00분)  (좋아요 : 5개)  (댓글 : 3개)
    ID : user 
    제목 : 가나다라
    본문 : abcd

    1. 댓글달기
    2. 좋아요달기
    ------


  # 글쓰기 _ (완성)
    - 제목 입력받기
    - 본문 입력받기

  # 검색창
    - 제목에서 검색(키워드 _ 최신순으로 10개 정도만)
    - 본문에서 검색(키워드 _ 최신순으로 10개 정도만)

  
  # 설정 _ (완성)
    - 사용자 이름, 비밀번호 변경 or sns상 ID 변경
    - 회원 탈퇴

