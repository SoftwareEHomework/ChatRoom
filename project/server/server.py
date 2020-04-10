import socket
import threading
import time
import os
import json
"""
C/S模式的服务器，首先客户端将信息发送到服务器，服务器接收信息，并将消息转发给其他客户
服务器应该提供登录注册的功能
服务器应该能转发消息和接收消息
"""


#创建user文件夹
if not os.path.exists("./user"):
    os.mkdir("./user")

#创建user.json文件，存放用户名和密码
if not os.path.exists("./user/user.json"):
    f = open("./user/user.json", "w")
    f.write("{}")
    f.close()

#注册账号
def sign_up(conn):
    msg = conn.recv(1024).decode()
    with open("./user/user.json", 'r') as f:
        userInfo = f.read()
    userDict = json.loads(userInfo)
    #如果用户名存在，返回密码，不存在，返回-1
    password = userDict.get(msg, -1)
    #如果密码不存在，说明用户名有效,将用户的密码保存起来
    if password == -1:
        conn.send("yes".encode())
        password = conn.recv(1024).decode()
        userDict[msg] = password
        with open("./user/user.json", "w") as f:
            json.dump(userDict, f)
        conn.send("yes".encode())


#登录账号
def login():
    pass

#发送消息
def send_msg():
    pass

#多线程函数，客户机最初发送消息过来启动这个函数
def serverFunc(conn):
    login_msg = conn.recv(1024).decode()
    if login_msg == "sign_up":
        sign_up(conn)
    elif login_msg == "login":
        login()

    while True:
        msg = conn.recv(1024).decode()




if __name__ == '__main__':
    #创建套接字
    host = "127.0.0.1"
    port = 6666
    server = socket.socket()
    server.bind((host, port))
    server.listen(10)
    print("服务器正在监听......")
    while True:
        conn, addr = server.accept()
        print("connect with: {} ,{}".format(conn.getsockname(), conn.fileno()))
        print(conn)
        print(addr)

        msg = conn.recv(1024).decode()
        if msg == "test":
            #给客户机发送一个确认消息
            conn.send("start".encode())
            t = threading.Thread(target=serverFunc, args=(conn,))
            t.setDaemon(True)
            t.start()