CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  name VARCHAR(50),
  profile VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE grade_rules (
  grade_name VARCHAR(20) PRIMARY KEY,
  min_post_count INT NOT NULL,
  min_comment_count INT NOT NULL,
  weight DECIMAL(3,1) NOT NULL,
  can_view BOOLEAN NOT NULL,
  can_interact BOOLEAN NOT NULL
);

CREATE TABLE categories (
  category_name VARCHAR(20) PRIMARY KEY
);

CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  profile VARCHAR(50) NOT NULL,
  category VARCHAR(20) NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  view_count INT DEFAULT 0,
  archived BOOLEAN DEFAULT FALSE,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (profile) REFERENCES users(profile),
  FOREIGN KEY (category) REFERENCES categories(category_name)
);

CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  profile VARCHAR(50) NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (profile) REFERENCES users(profile)
);

CREATE TABLE likes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  profile VARCHAR(50) NOT NULL,
  UNIQUE(post_id, profile),
  FOREIGN KEY (post_id) REFERENCES posts(id),
  FOREIGN KEY (profile) REFERENCES users(profile)
);

CREATE TABLE reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  target_type ENUM('post','comment') NOT NULL,
  target_id INT NOT NULL,
  reporter_profile VARCHAR(50) NOT NULL,
  reason TEXT NOT NULL,
  created_at DATETIME NOT NULL,
  FOREIGN KEY (reporter_profile) REFERENCES users(profile)
);
