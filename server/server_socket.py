'''
Author:　秦浩
key technology: TCP协议　多进程
data:2018-6-9
describe:建立服务器对象，启动服务器，完成多进程任务分发；
'''

import socket
import multiprocessing
import sqlite3
from login import server_register, server_login

class Server:
    '''这是一个服务器类，用于创建和启动服务器对象'''

    def __init__(self, addr):
        self.sockfd = socket.socket()
        self.addr = addr
        self.sockfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockfd.bind(self.addr)
        self.sockfd.listen(5)

    def serverForever(self):
        '''启动服务器'''
        #连接数据库
        self.db = sqlite3.connect('customers.db')
        #存放在线人员的列表
        self.online=[]
        #等待客户端连接
        while True:
            print('正在等待连接．．．')
            self.connfd, self.client_addr = self.sockfd.accept()
            #创建子进程
            process=multiprocessing.Process(target=self.handle_chart)
            process.start()

    def receive_data(self):
        '''用于接收和解析客户端发来的各种请求指令'''
        data=self.connfd.recv(2048).decode()
        print('客户端传来的data为:',data)
        return data

    def handle_chart(self):
        '''处理服务器接收到的各种请求指令'''
        while True:
            data = self.receive_data()
            if data[0] == "R":
                print("注册用户")
                server_register(self.connfd,self.db,data)
            elif data[0] == 'L':
                print("用户登录")
                server_login(self.connfd, self.db, data)
            elif data[0] == 'C':
                print("聊天开始")
                # do_cahrt(self.connfd,self.db, data)
            elif data[0] == 'A':
                print('管理员操作')
                # do_admin(self.connfd, self.db, self.online"在线用户列表")
            elif data[0] == 'F':
                print("文件上传下载操作")
                # do_file(self.connfd,self.db)
            elif data[0] == 'Q':
                print("退出聊天")
                # do_quit(self.connfd)

def run_server():
    ADDR= ('127.0.0.1', 9999)
    server=Server(ADDR)
    server.serverForever()

if __name__ == '__main__':
    run_server()








