from flask import Flask , render_template , request, flash , redirect
import os
import json
app = Flask(__name__)

#设置secret_key防止flash消息闪现报错
app.secret_key = '666'

#创建user文件夹
if not os.path.exists("./user"):
    os.mkdir("./user")

#创建user.json文件，存放用户名和密码
if not os.path.exists("./user/user.json"):
    f = open("./user/user.json", "w")
    f.write("{}")
    f.close()

@app.route('/', methods=['GET', 'POST'])
def index():
	return render_template('index.html')

@app.route('/sign_up',methods=['GET', 'POST'])
def sign_up():
	with open('./user/user.json', 'r') as f:
		userDict = json.load(f)
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		password2 = request.form.get('password2')

		#消息闪现
		if username in userDict:
			flash(u'用户名已存在')
		elif not all([username, password, password2]):
			flash(u"输入不完整")
		elif password != password2:
			flash(u"密码不一致")
		else:
			flash(u'注册成功')
			#保存注册账号
			with open("./user/user.json", "w") as f:
				userDict[username] = password
				json.dump(userDict, f)
	return render_template('sign_up.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
	return render_template('login.html')

if __name__ == '__main__':
	app.run(debug = True)