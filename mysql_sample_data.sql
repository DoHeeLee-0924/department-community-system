-- Optional sample data for Department Community System
-- Run this file after mysql_schema.sql only when sample data is needed.

USE department_community;

INSERT INTO users (username, password, profile_id, role, grade_name)
VALUES
('newbie', '1234', 'newbie01', 'user', '신입'),
('general', '1234', 'general01', 'user', '일반'),
('mentor', '1234', 'mentor01', 'user', '우수'),
('topmentor', '1234', 'topmentor01', 'user', '최우수'),
('student1', '1234', 'student01', 'user', '일반'),
('student2', '1234', 'student02', 'user', '일반');

INSERT INTO posts (user_id, category_id, title, content, view_count, archived, created_at)
VALUES
((SELECT user_id FROM users WHERE username='general'), (SELECT category_id FROM categories WHERE category_name='인사방'), '안녕하세요 일반 등급 테스트 글입니다', '인사방 샘플 게시글입니다.', 8, FALSE, '2026-06-05 09:00:00'),
((SELECT user_id FROM users WHERE username='mentor'), (SELECT category_id FROM categories WHERE category_name='수업'), '데이터베이스 정규화 핵심 정리', '1NF, 2NF, 3NF의 차이를 간단히 정리한 글입니다.', 42, FALSE, '2026-06-05 10:01:00'),
((SELECT user_id FROM users WHERE username='mentor'), (SELECT category_id FROM categories WHERE category_name='과제'), 'ERD 과제 작성 팁', '엔티티, 관계, 카디널리티를 먼저 잡고 속성을 배치하면 좋습니다.', 35, FALSE, '2026-06-05 10:02:00'),
((SELECT user_id FROM users WHERE username='mentor'), (SELECT category_id FROM categories WHERE category_name='팀플'), '팀플 역할 분담 예시', '발표, 자료조사, 설계, 구현으로 역할을 나누면 관리가 쉽습니다.', 21, FALSE, '2026-06-05 10:03:00'),
((SELECT user_id FROM users WHERE username='mentor'), (SELECT category_id FROM categories WHERE category_name='공지'), '정보시스템설계 발표 준비 체크리스트', '목적, ERD, Relation Schema, Decision Table을 반드시 확인하세요.', 55, FALSE, '2026-06-05 10:04:00'),
((SELECT user_id FROM users WHERE username='mentor'), (SELECT category_id FROM categories WHERE category_name='취업'), 'IT 직무 포트폴리오 구성 팁', '프로젝트 설명, ERD, 실행 화면, GitHub 링크를 함께 정리하면 좋습니다.', 31, FALSE, '2026-06-05 10:05:00'),
((SELECT user_id FROM users WHERE username='topmentor'), (SELECT category_id FROM categories WHERE category_name='수업'), 'SQL JOIN 개념 한 번에 정리', 'INNER JOIN, LEFT JOIN의 차이를 예시 중심으로 정리했습니다.', 70, FALSE, '2026-06-05 10:11:00'),
((SELECT user_id FROM users WHERE username='topmentor'), (SELECT category_id FROM categories WHERE category_name='과제'), 'Decision Table 작성 예시', '조건부와 실행부를 분리하면 Rule이 명확해집니다.', 66, FALSE, '2026-06-05 10:12:00'),
((SELECT user_id FROM users WHERE username='student1'), (SELECT category_id FROM categories WHERE category_name='수업'), 'JOIN과 INNER JOIN 차이가 있나요?', 'MySQL에서 JOIN과 INNER JOIN이 같은 의미인지 궁금합니다.', 12, FALSE, '2026-06-05 11:10:00'),
((SELECT user_id FROM users WHERE username='student2'), (SELECT category_id FROM categories WHERE category_name='과제'), 'ERD에서 카테고리를 따로 빼는 게 맞나요?', '게시글 테이블에 category를 문자열로 넣는 것과 별도 테이블로 빼는 것 중 어떤 게 좋은지 질문합니다.', 18, FALSE, '2026-06-05 11:15:00');

INSERT INTO comments (post_id, user_id, content, archived, created_at)
VALUES
((SELECT post_id FROM posts WHERE title='데이터베이스 정규화 핵심 정리'), (SELECT user_id FROM users WHERE username='general'), '정규화 예시가 있어서 이해가 잘 됩니다.', FALSE, '2026-06-05 11:00:00'),
((SELECT post_id FROM posts WHERE title='데이터베이스 정규화 핵심 정리'), (SELECT user_id FROM users WHERE username='student1'), '3NF 부분을 발표 때 넣어도 좋을 것 같아요.', FALSE, '2026-06-05 11:01:00'),
((SELECT post_id FROM posts WHERE title='Decision Table 작성 예시'), (SELECT user_id FROM users WHERE username='student2'), 'Decision Table 양식 참고하겠습니다.', FALSE, '2026-06-05 11:02:00'),
((SELECT post_id FROM posts WHERE title='JOIN과 INNER JOIN 차이가 있나요?'), (SELECT user_id FROM users WHERE username='mentor'), 'MySQL에서는 JOIN이 INNER JOIN과 동일하게 동작합니다.', FALSE, '2026-06-05 11:03:00'),
((SELECT post_id FROM posts WHERE title='ERD에서 카테고리를 따로 빼는 게 맞나요?'), (SELECT user_id FROM users WHERE username='topmentor'), '카테고리는 별도 테이블로 분리하는 것이 설계상 더 좋습니다.', FALSE, '2026-06-05 11:04:00');

INSERT INTO likes (post_id, user_id, created_at)
VALUES
((SELECT post_id FROM posts WHERE title='데이터베이스 정규화 핵심 정리'), (SELECT user_id FROM users WHERE username='general'), '2026-06-05 12:00:00'),
((SELECT post_id FROM posts WHERE title='데이터베이스 정규화 핵심 정리'), (SELECT user_id FROM users WHERE username='student1'), '2026-06-05 12:01:00'),
((SELECT post_id FROM posts WHERE title='ERD 과제 작성 팁'), (SELECT user_id FROM users WHERE username='general'), '2026-06-05 12:02:00'),
((SELECT post_id FROM posts WHERE title='Decision Table 작성 예시'), (SELECT user_id FROM users WHERE username='mentor'), '2026-06-05 12:03:00'),
((SELECT post_id FROM posts WHERE title='JOIN과 INNER JOIN 차이가 있나요?'), (SELECT user_id FROM users WHERE username='topmentor'), '2026-06-05 12:04:00');

INSERT INTO reports (reporter_id, target_type, target_id, reason, created_at)
VALUES
((SELECT user_id FROM users WHERE username='general'), 'post', (SELECT post_id FROM posts WHERE title='JOIN과 INNER JOIN 차이가 있나요?'), '중복 질문 여부 확인 필요', '2026-06-05 13:00:00');
