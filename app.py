from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from functools import wraps
import hashlib  # 在文件顶部添加导入

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DB_PATH = "records.db"

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("请先登录", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 初始化数据库
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT,
                date TEXT NOT NULL,
                user_id INTEGER
            )
        ''')
        conn.commit()

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                flash("注册成功，请登录", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("用户名已存在", "danger")
    return render_template('register.html')

# 登录
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['user'] = username
                return redirect(url_for('home'))
            else:
                flash("用户名或密码错误", "danger")
    return render_template('login.html')

# 主页
@app.route('/jz/home')
@login_required
def home():
    return render_template('home.html')

# 添加记录页
@app.route('/jz/add_page')
@login_required
def add_page():
    return render_template('add_record.html')

# 添加记录提交
@app.route('/jz/add', methods=['POST'])
@login_required
def add_record():
    record_type = request.form['type']
    amount = float(request.form['amount'])
    note = request.form.get('note', '')
    date = request.form['date']

    current_user = session['user']
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (current_user,))
        user = c.fetchone()
        if user:
            user_id = user[0]
            c.execute("INSERT INTO records (type, amount, note, date, user_id) VALUES (?, ?, ?, ?, ?)",
                      (record_type, amount, note, date, user_id))
            conn.commit()
    flash("记录添加成功", "success")
    return redirect(url_for('add_page'))

# 查询页
@app.route('/jz/stats_page')
@login_required
def stats_page():
    return render_template('stats.html')

# 查询提交
@app.route('/jz/stats')
@login_required
def stats():
    query_type = request.args.get('query_type')
    display_type = request.args.get('display_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    current_user = session['user']
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=?", (current_user,))
        user = c.fetchone()
        if not user:
            flash("用户不存在", "danger")
            return redirect(url_for("stats_page"))
        user_id = user[0]

        query = "SELECT * FROM records WHERE user_id = ? AND type = ? AND date BETWEEN ? AND ?"
        c.execute(query, (user_id, query_type, start_date, end_date))
        results = c.fetchall()

    if display_type == 'total':
        total = sum([r[2] for r in results])
        return render_template("stats.html", stats={
            "label": "收入总计" if query_type == "income" else "支出总计",
            "start_date": start_date,
            "end_date": end_date,
            "total": round(total, 2),
            "display_type": "total"
        })
    else:
        records = [{
            "date": r[4],
            "type": "收入" if r[1] == "income" else "支出",
            "amount": round(r[2], 2),
            "note": r[3]
        } for r in results]
        total = sum([r["amount"] for r in records])
        return render_template("stats.html", stats={
            "label": "收入记录" if query_type == "income" else "支出记录",
            "start_date": start_date,
            "end_date": end_date,
            "total": round(total, 2),
            "display_type": "all"
        }, records=records)

# 登出
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("已退出登录", "info")
    return redirect(url_for('login'))

# 快捷指令接口
@app.route('/api/add', methods=['POST'])
def api_add_record():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    record_type = data.get('type')
    amount = data.get('amount')
    note = data.get('note', '')
    date = data.get('date')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        if not user:
            return {"status": "error", "message": "用户名或密码错误"}, 403
        user_id = user[0]

        try:
            amount = float(amount)
        except:
            return {"status": "error", "message": "金额格式不正确"}, 400

        c.execute("INSERT INTO records (type, amount, note, date, user_id) VALUES (?, ?, ?, ?, ?)",
                  (record_type, amount, note, date, user_id))
        conn.commit()

    return {"status": "success", "message": "记录添加成功"}


# 初始化数据库
init_db()

@app.route('/api/bill', methods=['GET'])
def api_bill():
    username = request.args.get('username')
    sign = request.args.get('sign')
    token_fixed = 'lsh88nihao'  # 固定token

    # 参数校验
    if not username or not sign:
        return {"status": "error", "message": "参数不完整"}, 400

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if not user:
            return {"status": "error", "message": "用户不存在"}, 404

        user_id, password = user

        # 生成签名校验
        s = f"{username}{password}{token_fixed}".encode()
        computed_sign = hashlib.sha256(s).hexdigest()
        if computed_sign != sign:
            return {"status": "error", "message": "签名验证失败"}, 403

        # 获取查询参数
        record_type = request.args.get('type', 'expense')
        if record_type not in ('income', 'expense'):
            record_type = 'expense'

        page = request.args.get('page', 1, type=int)
        per_page = 10
        offset = (page - 1) * per_page

        # 查询记录总数和金额总和
        c.execute("""
            SELECT COUNT(*), SUM(amount) 
            FROM records 
            WHERE user_id=? AND type=?
        """, (user_id, record_type))
        total_records, total_amount = c.fetchone()
        total_amount = total_amount or 0
        total_pages = (total_records + per_page - 1) // per_page

        # 查询当前页数据
        c.execute("""
            SELECT date, type, amount, note 
            FROM records 
            WHERE user_id=? AND type=?
            ORDER BY date DESC 
            LIMIT ? OFFSET ?
        """, (user_id, record_type, per_page, offset))
        records = [{
            "date": r[0],
            "type": "收入" if r[1] == "income" else "支出",
            "amount": round(r[2], 2),
            "note": r[3]
        } for r in c.fetchall()]

    return render_template(
        'bill.html',
        records=records,
        username=username,
        sign=sign,
        record_type=record_type,
        current_page=page,
        total_pages=total_pages,
        total_amount=round(total_amount, 2)
    )

if __name__ == '__main__':
    app.run(debug=True)
