# ChatRoom智能聊天室
开发环境：
- Python 3.6
- Pycharm社区版
- 第三方库：tensorflow2.0，flask，geventwebsocket，jieba
## 项目简述
实现一个智能聊天室，包括注册账号，登录，添加好友，以及和机器人聊天等功能。
## 使用方法
初期写了一个客户端和服务器，打算做成桌面程序，后期改变了策略，改做web聊天室。 <br>
启动web服务器需要运行/project/Flask_version/app.py，因为缺少聊天机器人的模型（模型300M没能传上来），所以你需要先运行/project/Flask_version/chatbot/seq2seqchat/train/目录下的三个.ipynb文件（jupyter notebook上运行）以获得聊天机器人的模型。或者联系我们，我们会以其他途径提供给你聊天机器人的模型。<br>
运行服务器后，在浏览器中输入http://127.0.0.1:5000 ,打开web页面即可。
