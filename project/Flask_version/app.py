from flask import Flask
from flask import redirect
from flask import  render_template
from flask import request
from flask import  flash
from flask import  url_for
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
		elif len(password) < 6:
			flash(u'密码太短，不安全，请输入6位以上密码')
		else:
			flash(u'注册成功')
			#保存注册账号
			with open("./user/user.json", "w") as f:
				d = {}
				d["password"] = password
				userDict[username] = d
				json.dump(userDict, f)

	return render_template('sign_up.html')
@app.route('/login',methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		with open('./user/user.json', 'r') as f:
			userDict = f.read()
			userDict = json.loads(userDict)
		username = request.form.get('username')
		password = request.form.get('password')

		#处理用户名不存在的异常
		if username not in userDict:
			flash(u'用户名不存在,请注册')
		elif userDict[username]["password"] == password:
			flash(u'登陆成功！')
			return redirect(url_for('person', name=username))
		else:
			flash(u'密码错误')
	return render_template('login.html')

@app.route('/<name>')
def person(name):
	with open("./user/user.json", 'r') as f:
		userDict = json.load(f)
	friend = userDict.get("friend", 0)
	print(friend)
	if friend == 0:
		my_friend = ["你当前还没有朋友"]
	else:
		my_friend = friend
	return render_template('person.html', name=name, my_friend=my_friend)

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
	if request.method == "POST":
		input_text = request.form.get('input_text')
		print(input_text)
	return render_template('chatbot.html')

if __name__ == '__main__':
	app.run(debug = True)