import os
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'user_data.db')
CATEGORIES = ['인사방', '수업', '과제', '팀플', '공지', '취업']
GRADE_RULES = {
    '신입': {'weight': 0.5, 'can_view': False, 'can_interact': False},
    '일반': {'weight': 1.0, 'can_view': True, 'can_interact': True},
    '우수': {'weight': 2.0, 'can_view': True, 'can_interact': True},
    '최우수': {'weight': 3.0, 'can_view': True, 'can_interact': True},
    '관리자': {'weight': 4.0, 'can_view': True, 'can_interact': True},
}
ADMIN_USERNAME = 'qwer'
ADMIN_PASSWORD = '1234'

app = Flask(__name__)
app.secret_key = 'department-community-demo-key'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def add_column_if_missing(conn, table_name, column_name, column_type):
    cols = [row['name'] for row in conn.execute(f'PRAGMA table_info({table_name})')]
    if column_name not in cols:
        conn.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')
        conn.commit()


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT,
            age TEXT,
            phone TEXT,
            sns_profile TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT '신입'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sns_profile TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '수업',
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            archived INTEGER DEFAULT 0,
            FOREIGN KEY(sns_profile) REFERENCES users(sns_profile)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            sns_profile TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            sns_profile TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS post_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            reporter_profile TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comment_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id INTEGER NOT NULL,
            reporter_profile TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(comment_id) REFERENCES comments(id)
        )
    """)
    conn.commit()
    add_column_if_missing(conn, 'users', 'role', "TEXT DEFAULT '신입'")
    add_column_if_missing(conn, 'posts', 'category', "TEXT NOT NULL DEFAULT '수업'")
    add_column_if_missing(conn, 'posts', 'view_count', 'INTEGER DEFAULT 0')
    add_column_if_missing(conn, 'posts', 'archived', 'INTEGER DEFAULT 0')

    existing_admin = conn.execute('SELECT username FROM users WHERE username = ?', (ADMIN_USERNAME,)).fetchone()
    if existing_admin:
        conn.execute("""
            UPDATE users
            SET password = ?, name = '관리자', sns_profile = '관리자', role = '관리자'
            WHERE username = ?
        """, (ADMIN_PASSWORD, ADMIN_USERNAME))
    else:
        conn.execute("""
            INSERT INTO users(username, password, name, sns_profile, role)
            VALUES (?, ?, '관리자', '관리자', '관리자')
        """, (ADMIN_USERNAME, ADMIN_PASSWORD))
    conn.commit()
    conn.close()


def get_activity_counts(conn, sns_profile):
    post_count = conn.execute("""
        SELECT COUNT(*) AS cnt FROM posts
        WHERE sns_profile = ? AND archived = 0
    """, (sns_profile,)).fetchone()['cnt']
    comment_count = conn.execute("""
        SELECT COUNT(*) AS cnt FROM comments
        WHERE sns_profile = ?
    """, (sns_profile,)).fetchone()['cnt']
    return post_count, comment_count


def decide_grade(username, sns_profile, post_count, comment_count):
    if username == ADMIN_USERNAME or sns_profile == '관리자':
        return '관리자'
    if post_count >= 10 and comment_count >= 10:
        return '최우수'
    if post_count >= 5 and comment_count >= 5:
        return '우수'
    if post_count >= 1:
        return '일반'
    return '신입'


def current_user():
    if 'username' not in session:
        return None
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
    if not row:
        conn.close()
        return None
    data = dict(row)
    post_count, comment_count = get_activity_counts(conn, data['sns_profile'])
    grade = decide_grade(data['username'], data['sns_profile'], post_count, comment_count)
    data['grade'] = grade
    data['grade_weight'] = GRADE_RULES[grade]['weight']
    data['post_count'] = post_count
    data['comment_count'] = comment_count
    data['can_view'] = GRADE_RULES[grade]['can_view']
    data['can_interact'] = GRADE_RULES[grade]['can_interact']
    conn.close()
    return data


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def general_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            flash('로그인이 필요합니다.')
            return redirect(url_for('login'))
        if not user['can_interact']:
            flash('일반 등급 이상부터 게시글 상세 조회, 댓글, 좋아요, 신고 기능을 사용할 수 있습니다. 단, 신입도 인사방 게시글은 상세 조회할 수 있습니다. 일반 등급 조건: 게시글 1개 이상')
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped



def detail_view_allowed(user, post):
    if not user:
        return False
    if user['can_view']:
        return True
    if post and post['category'] == '인사방':
        return True
    return False


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user['grade'] != '관리자':
            flash('관리자만 접근할 수 있습니다.')
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped


def post_count_expr():
    return "(SELECT COUNT(*) FROM posts p2 WHERE p2.sns_profile = u.sns_profile AND p2.archived = 0)"


def comment_count_expr():
    return "(SELECT COUNT(*) FROM comments c2 WHERE c2.sns_profile = u.sns_profile)"


def grade_case_sql():
    pc = post_count_expr()
    cc = comment_count_expr()
    return f"""
        CASE
            WHEN u.username = '{ADMIN_USERNAME}' THEN '관리자'
            WHEN {pc} >= 10 AND {cc} >= 10 THEN '최우수'
            WHEN {pc} >= 5 AND {cc} >= 5 THEN '우수'
            WHEN {pc} >= 1 THEN '일반'
            ELSE '신입'
        END
    """


def weight_case_sql():
    pc = post_count_expr()
    cc = comment_count_expr()
    return f"""
        CASE
            WHEN u.username = '{ADMIN_USERNAME}' THEN 4.0
            WHEN {pc} >= 10 AND {cc} >= 10 THEN 3.0
            WHEN {pc} >= 5 AND {cc} >= 5 THEN 2.0
            WHEN {pc} >= 1 THEN 1.0
            ELSE 0.5
        END
    """


def trust_score_sql():
    weight = weight_case_sql()
    return f"""
        ({weight} * 10
         + p.likes * 2
         + p.comments * 1
         + p.view_count * 0.1)
    """


def fetch_posts(category=None, mode='trust'):
    conn = get_db()
    where = ['p.archived = 0']
    params = []
    if category in CATEGORIES:
        where.append('p.category = ?')
        params.append(category)
    where_sql = ' AND '.join(where)
    score = trust_score_sql()
    grade = grade_case_sql()
    weight = weight_case_sql()
    order_sql = 'p.timestamp DESC'
    if mode == 'trust':
        order_sql = f"""
            CASE WHEN p.category = '공지' AND {grade} = '관리자' THEN 1 ELSE 0 END DESC,
            trust_score DESC,
            p.timestamp DESC
        """
    rows = conn.execute(f"""
        SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp, p.category,
               p.likes, p.comments, p.view_count,
               {grade} AS grade,
               {weight} AS grade_weight,
               {score} AS trust_score,
               CASE WHEN {score} >= 30 THEN '상단 노출' ELSE '일반 노출' END AS exposure_status
        FROM posts p
        LEFT JOIN users u ON p.sns_profile = u.sns_profile
        WHERE {where_sql}
        ORDER BY {order_sql}
    """, params).fetchall()
    conn.close()
    return rows


@app.context_processor
def inject_globals():
    return {'categories': CATEGORIES, 'user': current_user()}


@app.route('/')
def index():
    category = request.args.get('category')
    mode = request.args.get('mode', 'trust')
    posts = fetch_posts(category=category, mode=mode)
    return render_template('index.html', posts=posts, selected_category=category, mode=mode)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        sns_profile = request.form.get('sns_profile', '').strip()
        if username == ADMIN_USERNAME:
            flash('qwer는 관리자 전용 아이디입니다.')
            return redirect(url_for('register'))
        if not username or not password or not sns_profile:
            flash('아이디, 비밀번호, 프로필 ID를 모두 입력하세요.')
            return redirect(url_for('register'))
        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO users(username, password, name, sns_profile, role)
                VALUES (?, ?, ?, ?, '신입')
            """, (username, password, name, sns_profile))
            conn.commit()
            flash('회원가입이 완료되었습니다. 모든 신규 회원은 신입 등급으로 시작합니다.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('이미 사용 중인 아이디 또는 프로필 ID입니다.')
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['username'] = user['username']
            flash('로그인되었습니다.')
            return redirect(url_for('index'))
        flash('아이디 또는 비밀번호가 올바르지 않습니다.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('로그아웃되었습니다.')
    return redirect(url_for('index'))


@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '').strip()
        user = current_user()
        if not title or not content or category not in CATEGORIES:
            flash('제목, 내용, 태그를 모두 입력해야 게시글 등록이 가능합니다.')
            return redirect(url_for('write'))
        if user['grade'] == '신입' and category != '인사방':
            flash('신입 등급은 등업을 위해 인사방에만 글을 작성할 수 있습니다. 글 1개 작성 후 일반 등급으로 전환됩니다.')
            return redirect(url_for('write'))
        conn = get_db()
        conn.execute("""
            INSERT INTO posts(sns_profile, title, content, timestamp, category)
            VALUES (?, ?, ?, ?, ?)
        """, (user['sns_profile'], title, content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), category))
        conn.commit()
        conn.close()
        flash(f'[{category}] 게시글이 등록되었습니다.')
        return redirect(url_for('index', category=category))
    return render_template('write.html')


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    user = current_user()
    if user['grade'] == '관리자':
        flash('관리자는 게시글 수정 권한이 없으며 삭제만 가능합니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ? AND archived = 0', (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('게시글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    if post['sns_profile'] != user['sns_profile']:
        conn.close()
        flash('작성자 본인만 게시글을 수정할 수 있습니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', '').strip()
        if not title or not content or category not in CATEGORIES:
            flash('제목, 내용, 태그를 모두 입력해야 게시글 수정이 가능합니다.')
            conn.close()
            return redirect(url_for('edit_post', post_id=post_id))
        if user['grade'] == '신입' and category != '인사방':
            flash('신입 등급은 인사방 게시글만 작성·수정할 수 있습니다.')
            conn.close()
            return redirect(url_for('edit_post', post_id=post_id))
        conn.execute("""
            UPDATE posts
            SET title = ?, content = ?, category = ?
            WHERE id = ?
        """, (title, content, category, post_id))
        conn.commit()
        conn.close()
        flash('게시글이 수정되었습니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    conn.close()
    return render_template('edit_post.html', post=post)


@app.route('/post/<int:post_id>')
@login_required
def post_detail(post_id):
    conn = get_db()
    score = trust_score_sql()
    grade = grade_case_sql()
    weight = weight_case_sql()
    post = conn.execute(f"""
        SELECT p.id, p.title, p.content, p.sns_profile, p.timestamp, p.category,
               p.likes, p.comments, p.view_count,
               {grade} AS grade,
               {weight} AS grade_weight,
               {score} AS trust_score,
               CASE WHEN {score} >= 30 THEN '상단 노출' ELSE '일반 노출' END AS exposure_status
        FROM posts p
        LEFT JOIN users u ON p.sns_profile = u.sns_profile
        WHERE p.id = ? AND p.archived = 0
    """, (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('게시글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    user = current_user()
    if not detail_view_allowed(user, post):
        conn.close()
        flash('신입 등급은 인사방 게시글만 상세 조회할 수 있습니다. 일반 등급 조건: 게시글 1개 이상')
        return redirect(url_for('index'))
    conn.execute('UPDATE posts SET view_count = view_count + 1 WHERE id = ?', (post_id,))
    conn.commit()
    comments = conn.execute("""
        SELECT c.id, c.sns_profile, c.content, c.timestamp
        FROM comments c
        WHERE c.post_id = ?
        ORDER BY c.timestamp ASC
    """, (post_id,)).fetchall()
    conn.close()
    return render_template('post_detail.html', post=post, comments=comments)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
@general_required
def add_comment(post_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('댓글 내용을 입력하세요.')
        return redirect(url_for('post_detail', post_id=post_id))
    user = current_user()
    conn = get_db()
    post = conn.execute('SELECT id FROM posts WHERE id = ? AND archived = 0', (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('게시글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    conn.execute("""
        INSERT INTO comments(post_id, sns_profile, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (post_id, user['sns_profile'], content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.execute('UPDATE posts SET comments = comments + 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
    user = current_user()
    if user['grade'] == '관리자':
        flash('관리자는 댓글 수정 권한이 없으며 삭제만 가능합니다.')
        return redirect(url_for('admin'))
    conn = get_db()
    comment = conn.execute('SELECT * FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        conn.close()
        flash('댓글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    if comment['sns_profile'] != user['sns_profile']:
        post_id = comment['post_id']
        conn.close()
        flash('작성자 본인만 댓글을 수정할 수 있습니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        if not content:
            flash('댓글 내용을 입력해야 수정할 수 있습니다.')
            conn.close()
            return redirect(url_for('edit_comment', comment_id=comment_id))
        conn.execute('UPDATE comments SET content = ? WHERE id = ?', (content, comment_id))
        conn.commit()
        post_id = comment['post_id']
        conn.close()
        flash('댓글이 수정되었습니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    conn.close()
    return render_template('edit_comment.html', comment=comment)


@app.route('/post/<int:post_id>/like', methods=['POST'])
@general_required
def like_post(post_id):
    user = current_user()
    conn = get_db()
    exists = conn.execute('SELECT COUNT(*) AS cnt FROM likes WHERE post_id = ? AND sns_profile = ?', (post_id, user['sns_profile'])).fetchone()['cnt']
    if exists:
        flash('이미 좋아요를 누른 게시글입니다.')
    else:
        conn.execute('INSERT INTO likes(post_id, sns_profile) VALUES (?, ?)', (post_id, user['sns_profile']))
        conn.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
        conn.commit()
        flash('좋아요를 눌렀습니다.')
    conn.close()
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/post/<int:post_id>/report', methods=['POST'])
@general_required
def report_post(post_id):
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('신고 사유를 입력해야 합니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    user = current_user()
    conn = get_db()
    post = conn.execute('SELECT id FROM posts WHERE id = ? AND archived = 0', (post_id,)).fetchone()
    if not post:
        conn.close()
        flash('게시글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    conn.execute("""
        INSERT INTO post_reports(post_id, reporter_profile, reason, timestamp)
        VALUES (?, ?, ?, ?)
    """, (post_id, user['sns_profile'], reason, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    flash('게시글 신고가 접수되었습니다.')
    return redirect(url_for('post_detail', post_id=post_id))


@app.route('/comment/<int:comment_id>/report', methods=['POST'])
@general_required
def report_comment(comment_id):
    reason = request.form.get('reason', '').strip()
    post_id = request.form.get('post_id', type=int)
    if not reason:
        flash('신고 사유를 입력해야 합니다.')
        return redirect(url_for('post_detail', post_id=post_id))
    user = current_user()
    conn = get_db()
    comment = conn.execute('SELECT id, post_id FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if not comment:
        conn.close()
        flash('댓글을 찾을 수 없습니다.')
        return redirect(url_for('index'))
    conn.execute("""
        INSERT INTO comment_reports(comment_id, reporter_profile, reason, timestamp)
        VALUES (?, ?, ?, ?)
    """, (comment_id, user['sns_profile'], reason, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    flash('댓글 신고가 접수되었습니다.')
    return redirect(url_for('post_detail', post_id=comment['post_id']))


@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    category_stats = conn.execute("""
        SELECT category, COUNT(*) AS cnt
        FROM posts
        WHERE archived = 0
        GROUP BY category
        ORDER BY cnt DESC
    """).fetchall()
    users = conn.execute(f"""
        SELECT u.username, u.sns_profile,
               {post_count_expr()} AS post_count,
               {comment_count_expr()} AS comment_count,
               COALESCE((SELECT SUM(p3.likes) FROM posts p3 WHERE p3.sns_profile = u.sns_profile AND p3.archived = 0), 0) AS received_likes
        FROM users u
        ORDER BY u.username
    """).fetchall()
    user_rows = []
    for row in users:
        d = dict(row)
        d['grade'] = decide_grade(d['username'], d['sns_profile'], d['post_count'], d['comment_count'])
        d['activity_score'] = d['post_count'] * 3 + d['comment_count'] * 2 + d['received_likes']
        user_rows.append(d)
    user_rows.sort(key=lambda x: x['activity_score'], reverse=True)
    posts = conn.execute("""
        SELECT p.id, p.title, p.category, p.sns_profile, p.timestamp, p.likes, p.comments, p.view_count
        FROM posts p
        WHERE p.archived = 0
        ORDER BY p.timestamp DESC
        LIMIT 50
    """).fetchall()
    comments = conn.execute("""
        SELECT c.id, c.post_id, c.sns_profile, c.content, c.timestamp, p.title AS post_title
        FROM comments c
        LEFT JOIN posts p ON c.post_id = p.id
        ORDER BY c.timestamp DESC
        LIMIT 50
    """).fetchall()
    post_reports = conn.execute("""
        SELECT r.id, r.post_id, r.reporter_profile, r.reason, r.timestamp,
               p.title, p.sns_profile AS writer_profile
        FROM post_reports r
        LEFT JOIN posts p ON r.post_id = p.id
        ORDER BY r.timestamp DESC
    """).fetchall()
    comment_reports = conn.execute("""
        SELECT r.id, r.comment_id, r.reporter_profile, r.reason, r.timestamp,
               c.content, c.post_id, c.sns_profile AS writer_profile,
               p.title AS post_title
        FROM comment_reports r
        LEFT JOIN comments c ON r.comment_id = c.id
        LEFT JOIN posts p ON c.post_id = p.id
        ORDER BY r.timestamp DESC
    """).fetchall()
    conn.close()
    return render_template('admin.html', category_stats=category_stats, users=user_rows,
                           posts=posts, comments=comments,
                           post_reports=post_reports, comment_reports=comment_reports)


@app.route('/admin/post/<int:post_id>/delete', methods=['POST'])
@admin_required
def delete_post(post_id):
    conn = get_db()
    conn.execute('UPDATE posts SET archived = 1 WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    flash('게시글을 삭제 처리했습니다.')
    return redirect(url_for('admin'))


@app.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@admin_required
def delete_comment(comment_id):
    conn = get_db()
    comment = conn.execute('SELECT post_id FROM comments WHERE id = ?', (comment_id,)).fetchone()
    if comment:
        conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.execute('UPDATE posts SET comments = CASE WHEN comments > 0 THEN comments - 1 ELSE 0 END WHERE id = ?', (comment['post_id'],))
        conn.commit()
        flash('댓글을 삭제했습니다.')
    conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
