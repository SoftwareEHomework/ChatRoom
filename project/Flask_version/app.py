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
from seq2seq import Encoder
from seq2seq import Decoder
import jieba

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

@app.route('/user/<name>', methods=['GET', 'POST'])
def person(name):
	with open("./user/user.json", 'r') as f:
		userDict = json.load(f)
	friend = userDict[name].get("friends", 0)
	print(userDict[name])
	print(type(userDict[name]))
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
    start_string2 = jieba.cut(start_string)
    input_eval = [word_to_id.get(s, 0) for s in start_string2]
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
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()

      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(id_to_word[predicted_id])

    return start_string + ''.join(text_generated)

#聊天机器人生成回复的句子
def predict(sentence):
	for ch in "#@$%^&*():;：；{}[]'_<>-+/~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
		sentence = sentence.replace(ch, "")
	sentence = jieba.cut(sentence)
	sentence = [word2id.get(word, word2id["<pad>"]) for word in sentence]
	sentence = tf.keras.preprocessing.sequence.pad_sequences([sentence], value=word2id["<pad>"],
															 maxlen=20, padding='post')
	sentence = tf.convert_to_tensor(sentence)

	result = ''
	hidden = [tf.zeros((1, units))]  # 现在只输入了一个所以batch_size是1
	encoder_output, encoder_hidden = encoder(sentence, hidden)

	decoder_hidden = encoder_hidden
	decoder_input = tf.expand_dims([word2id["<start>"]], 0)

	for t in range(20):
		predictions, decoder_hidden, attention_weights = decoder(decoder_input,
																 decoder_hidden,
																 encoder_output)
		predicted_id = tf.argmax(predictions[0]).numpy()

		if id2word[predicted_id] == "<end>":
			return result
		result += id2word[predicted_id]

		decoder_input = tf.expand_dims([predicted_id], 0)

	return result

#聊天机器人聊天的websocket路由
@app.route("/chatbot_ws/<username>")
def chatbot_ws(username):
	user_socket = request.environ.get("wsgi.websocket")
	flag = False
	global model

	while True:
		msg = user_socket.receive()
		if msg == "小说":
			flag = True
			user_socket.send("请随意输入一段话")
			continue
		elif msg == "q" and flag == True:
			flag = False

		if flag:
			msg = generate_text(model, start_string=msg, num_generate=100)
			user_socket.send(msg)
		else:
			msg = predict(msg)
			user_socket.send(msg)
		print(msg)

#处理添加好友请求的路由
@app.route('/add_friends/<name>')
def add_friends(name):
	user_socket = request.environ.get("wsgi.websocket")

	with open('./user/user.json', 'r') as f:
		userDict = json.load(f)
	while True:
		msg = user_socket.receive()
		if userDict.get(msg, 0):
			print("user {} 存在".format(msg))
			#添加过好友直接append，没加过得先创建一个列表
			if userDict[name].get("friends", 0) == 0:
				userDict[name]["friends"] = [msg]
			else:
				userDict[name]["friends"].append(msg)

			with open('./user/user.json', 'w') as f:
				json.dump(userDict, f)
			user_socket.send("ok")
		else:
			print("user {} 不存在".format(msg))
			user_socket.send("no")

@app.route('/chat_with_friend/<your_name>/<friend>', methods=['GET', 'POST'])
def chat_with_friend(your_name, friend):
	return render_template('chat_with_friend.html', your_name=your_name, friend=friend)

# @app.route("/ws/<username>")
# def ws(username):
#     user_socket = request.environ.get("wsgi.websocket") #type:WebSocket
#     if user_socket:
#         user_socket_dict[username] = user_socket
#     print(len(user_socket_dict),user_socket_dict)
#     while 1:
#         msg = user_socket.receive() # 收件人 消息 发件人
#         msg_dict = json.loads(msg)
#         msg_dict["from_user"] = username
#         to_user = msg_dict.get("to_user")
#         # chat = msg_dict.get("msg")
#         u_socket = user_socket_dict.get(to_user) # type:WebSocket
#         u_socket.send(json.dumps(msg_dict))



if __name__ == '__main__':
	print("服务器正在运行.....")
	model = tf.keras.models.load_model('./chatbot/AIwriter/AI_write_novel.h5')
	#写小说的词表
	with open("./chatbot/AIwriter/data/id2word.txt", 'r') as f:
		id_to_word = f.read().split()
	with open("./chatbot/AIwriter/data/word2id.json", 'r') as f:
		word_to_id = json.load(f)

	#聊天机器人的词表
	with open("./chatbot/seq2seqchat/train/id2word.json", 'r') as f:
		id2word = json.load(f)
	id2word = {int(k): v for k, v in id2word.items()}
	with open("./chatbot/seq2seqchat/train/word2id.json", 'r') as f:
		word2id = json.load(f)

	BUFFER_SIZE = 114969
	BATCH_SIZE = 64
	steps_per_epoch = 114969 // BATCH_SIZE
	embedding_dim = 100
	units = 512
	vocab_size = len(word2id) + 1

	encoder = Encoder(vocab_size, embedding_dim, units, BATCH_SIZE)
	decoder = Decoder(vocab_size, embedding_dim, units, BATCH_SIZE)

	checkpoint_dir = './chatbot/seq2seqchat/train/training_checkpoints'
	optimizer = tf.keras.optimizers.RMSprop()
	checkpoint = tf.train.Checkpoint(optimizer=optimizer,
									 encoder=encoder,
									 decoder=decoder)
	checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))
	print("服务器地址:http://127.0.0.1:5000")
	http_serv = WSGIServer(("127.0.0.1", 5000), app, handler_class=WebSocketHandler)
	http_serv.serve_forever()