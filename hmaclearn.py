import hmac, random, re


def hmac_sha256(key, s):
    return hmac.new(key.encode('utf-8'), s.encode('utf-8'), 'sha256').hexdigest()


class User(object):

    def __init__(self, username, password):
        self.username = username
        self.key = str([random.randint(48, 122) for x in range(20)])
        self.password = hmac_sha256(self.key, password)


db = {
    'michael': User('michael', '123456'),
    'bob': User('bob', 'abc999'),
    'alice': User('alice', 'alice2008')
}


def login(username, password):
    try:
        user = db[username]
    except KeyError as e:
        print(f'无效的用户名或密码:{eval(str(e))}/{password}')
        return False
    else:
        if not user.password == hmac_sha256(user.key, password):
            print('密码错误')
            return False
        else:
            return True


def add_user(username):
    try:
        db[username]
    except KeyError:
        pw_double_check = False
        while pw_double_check == False:
            pw_valid_check = False
            while pw_valid_check == False:
                pw = input('输入新密码：')
                if re.match('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', pw):
                    pw_valid_check = True
                else:
                    print('密码不符合规范')
            pw_check = input('再次输入密码：')
            if pw == pw_check:
                db[username] = User(username, pw)
                pw_double_check = True
            else:
                print('两次输入不匹配！')
    else:
        raise ValueError('该用户已存在')


def del_user(username):
    pass


logged = False
while not logged:
    access = False
    while not access:
        inputname = input('Username:')
        inputpw = input('Password:')

        if not login(inputname, inputpw):
            print('登录失败')
        else:
            print('登录成功')
            logged_user = inputname
            logged = True
            access = True

    while access:
        choose = input('修改密码/退出登录/添加用户/删除用户(1/2/3/4)')
        if choose == '3':
            add_user('asdfsdf')
        elif choose == '5':
            print(str(db))
