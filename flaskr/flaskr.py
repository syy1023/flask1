#!/usr/bin/env python
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/Users/yuanyuan.shao/Documents/flask/flask1/flaskr/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode())
        db.commit()




@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


'视图函数将会把条目作为字典传入 show_entries.html 模版以及返回渲染结果'
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


'这个视图允许登录的用户添加新的条目。它只回应 POST 请求，实际的表单是显示在 show_entries 页面。 如果一些工作正常的话，我们用 flash() 向下一个请求闪现一条信息并且跳转回 show_entries 页'

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))
'''
这些函数是用于用户登录以及注销。依据在配置中的值登录时检查用户名和密码并且在会话中设置 logged_in 键值。 
如果用户成功登录，logged_in 键值被设置成 True ，并跳转回 show_entries 页。
此外，会有消息闪现来提示用户登入成功。 
如果发生一个错误，模板会通知，并提示重新登录
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

'''
如果你使用字典的 pop() 方法并传入第二个参数（默认），
 这个方法会从字典中删除这个键，如果这个键不存在则什么都不做。
 这很有用，因为 我们不需要检查用户是否已经登入
'''
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run()