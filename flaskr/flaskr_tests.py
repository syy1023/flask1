import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No entries here so far' in rv.data.decode()


    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data.decode()
        rv = self.logout()
        assert 'You were logged out' in rv.data.decode()
        rv = self.login('adminx', 'default')
        assert 'Invalid username' in rv.data.decode()
        rv = self.login('admin', 'defaultx')
        assert 'Invalid password' in rv.data.decode()

    def test_messages(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data.decode()
        assert '&lt;Hello&gt;' in rv.data.decode()
        assert '<strong>HTML</strong> allowed here' in rv.data.decode()

'''
我们应用的大部分功能只允许具有管理员资格的用户访问。所以我们需要一种方法来帮助我们的测试客户端登录和注销。 
为此，我们向登录和注销页面发送一些请求，这些请求都携带了表单数据（用户名和密码）， 
因为登录和注销页面都会重定向，我们将客户端设置为 follow_redirects 
'''



if __name__ == '__main__':
    unittest.main()