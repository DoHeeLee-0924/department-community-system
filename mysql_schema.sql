DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS grade_rules;

CREATE TABLE grade_rules (
  grade_name VARCHAR(20) PRIMARY KEY,
  min_post_count INT NOT NULL,
  min_comment_count INT NOT NULL,
  weight DECIMAL(3,1) NOT NULL,
  can_view BOOLEAN NOT NULL,
  can_interact BOOLEAN NOT NULL
);

CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  profile_id VARCHAR(50) UNIQUE NOT NULL,
  role ENUM('user', 'admin') DEFAULT 'user',
  grade_name VARCHAR(20) DEFAULT '신입',
  FOREIGN KEY (grade_name) REFERENCES grade_rules(grade_name)
);

CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(20) UNIQUE NOT NULL,
  description VARCHAR(255)
);

CREATE TABLE posts (
  post_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  view_count INT DEFAULT 0,
  archived BOOLEAN DEFAULT FALSE,
  created_at DATETIME NOT NULL,
  updated_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE comments (
  comment_id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  content TEXT NOT NULL,
  archived BOOLEAN DEFAULT FALSE,
  created_at DATETIME NOT NULL,
  updated_at DATETIME,
  FOREIGN KEY (post_id) REFERENCES posts(post_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE likes (
  like_id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  created_at DATETIME,
  UNIQUE(post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES posts(post_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE reports (
  report_id INT AUTO_INCREMENT PRIMARY KEY,
  reporter_id INT NOT NULL,
  target_type ENUM('post', 'comment') NOT NULL,
  target_id INT NOT NULL,
  reason TEXT NOT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (reporter_id) REFERENCES users(user_id)
);


INSERT INTO grade_rules
(grade_name, min_post_count, min_comment_count, weight, can_view, can_interact)
VALUES
('신입', 0, 0, 0.5, FALSE, FALSE),
('일반', 1, 0, 1.0, TRUE, TRUE),
('우수', 5, 5, 2.0, TRUE, TRUE),
('최우수', 10, 10, 3.0, TRUE, TRUE),
('관리자', 0, 0, 3.0, TRUE, TRUE);


INSERT INTO categories (category_name, description)
VALUES
('인사방', '신입 사용자가 인사글을 작성하고 확인하는 공간'),
('수업', '수업 관련 정보'),
('과제', '과제 관련 정보'),
('팀플', '팀플 관련 정보'),
('공지', '공지 관련 정보'),
('취업', '취업 관련 정보');


INSERT INTO users (username, password, profile_id, role, grade_name)
VALUES ('qwer', '1234', 'admin', 'admin', '관리자');


SELECT
  p.post_id,
  p.title,
  u.username,
  u.grade_name,
  g.weight,
  COUNT(DISTINCT l.like_id) AS like_count,
  COUNT(DISTINCT c.comment_id) AS comment_count,
  p.view_count,
  (
    g.weight * 10
    + COUNT(DISTINCT l.like_id) * 2
    + COUNT(DISTINCT c.comment_id) * 1
    + p.view_count * 0.1
  ) AS reliability_score,
  CASE
    WHEN p.archived = TRUE THEN '조회 제외'
    WHEN (
      g.weight * 10
      + COUNT(DISTINCT l.like_id) * 2
      + COUNT(DISTINCT c.comment_id) * 1
      + p.view_count * 0.1
    ) >= 40 THEN '최상단 노출'
    WHEN (
      g.weight * 10
      + COUNT(DISTINCT l.like_id) * 2
      + COUNT(DISTINCT c.comment_id) * 1
      + p.view_count * 0.1
    ) >= 30 THEN '상단 노출'
    WHEN (
      g.weight * 10
      + COUNT(DISTINCT l.like_id) * 2
      + COUNT(DISTINCT c.comment_id) * 1
      + p.view_count * 0.1
    ) >= 20 THEN '일반 노출'
    ELSE '낮은 우선순위'
  END AS exposure_result
FROM posts p
JOIN users u ON p.user_id = u.user_id
JOIN grade_rules g ON u.grade_name = g.grade_name
LEFT JOIN likes l ON p.post_id = l.post_id
LEFT JOIN comments c ON p.post_id = c.post_id AND c.archived = FALSE
GROUP BY p.post_id, p.title, u.username, u.grade_name, g.weight, p.view_count, p.archived
ORDER BY reliability_score DESC;