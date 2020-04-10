import socket
import threading
import time

#注册
def sign_up(client):
    while True:
        send_input = input("请输入注册用户名：")
        # 发送用户名给服务器验证用户名是否已经被注册了
        client.send(send_input.encode())
        msg = client.recv(1024).decode()
        if msg == "yes":
            break
        else:
            print("该用户名已存在")

    while True:
        send_input = input("请输入密码，密码不少于6位：")
        if len(send_input) < 6:
            print("密码过短")
        else:
            client.send(send_input.encode())
            msg = client.recv(1024).decode()
            if msg == "yes":
                print("注册成功")
                break


#登录
def login(client):
    send_input = input("登录或者注册：输入login or sign_up")
    client.send(send_input.encode())
    try:
        if send_input == "login":
            pass
        elif send_input == "sign_up":
            sign_up(client)
    except:
        pass

if __name__ == "__main__":
    #创建套接字
    host = "127.0.0.1"
    port = 6666
    client = socket.socket()
    client.connect((host, port))


    #向服务器发送test，启动服务
    client.send("test".encode())
    msg = client.recv(1024).decode()

    #接收到服务器的确认消息
    #选择注册或者登录账号
    if msg == "start":
        login(client)



