from flask import Flask
from flask import redirect
from flask import  render_template
from flask import request
from flask import  flash
from flask import  url_for
import os
import json
import tensorflow as tf
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket.websocket import WebSocket
from gevent.pywsgi import WSGIServer
app = Flask(__name__)
app.debug = True
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

user_socket_list = []
user_socket_dict = {}

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
	if friend == 0:
		my_friend = ["你当前还没有朋友"]
	else:
		my_friend = friend
	return render_template('person.html', name=name, my_friend=my_friend)

@app.route("/chatbot/<name>", methods=['GET', 'POST'])
def chatbot(name):
	return render_template("chatbot.html", name=name)

def generate_text(model, start_string,num_generate = 100):
  # 评估步骤（用学习过的模型生成文本）
  # 要生成的字符个数
  # 将起始字符串转换为数字（向量化）
    input_eval = [word_to_id[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
  # 空字符串用于存储结果
    text_generated = []
  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
    temperature = 0.4     #可调整
  # 这里批大小为 1
    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
      # 删除批次的维度
        predictions = tf.squeeze(predictions, 0)
      # 用分类分布预测模型返回的字符
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(id_to_word[predicted_id])

    return start_string + ''.join(text_generated)


@app.route("/chatbot_ws/<username>")
def chatbot_ws(username):
	user_socket = request.environ.get("wsgi.websocket")
	user_socket_dict[username] = user_socket
	print(len(user_socket_dict), user_socket_dict)
	flag = False
	global model

	while True:
		msg = user_socket.receive()
		if msg == "小说":
			flag = True
			user_socket.send("请随意输入一段话")
		elif msg == "q" and flag == True:
			flag = False

		if flag:
			msg = generate_text(model, start_string=msg, num_generate=100)
			user_socket.send(msg)
		else:
			user_socket.send(msg)
		print(msg)

if __name__ == '__main__':
	print("服务器正在运行.....")
	model = tf.keras.models.load_model('./chatbot/AIwriter/AI_write_novel.h5')
	with open("./chatbot/AIwriter/data/id2word.txt", 'r') as f:
		id_to_word = f.read().split()
	with open("./chatbot/AIwriter/data/word2id.json", 'r') as f:
		word_to_id = json.load(f)
	http_serv = WSGIServer(("127.0.0.1", 5000), app, handler_class=WebSocketHandler)
	http_serv.serve_forever()