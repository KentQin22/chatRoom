'''
Author:　秦浩
key technology: TCP协议
data:2018-6-9
describe:建立客户端对象，启动客户端，在可视化界面下，调用不同功能函数；
'''


import tkinter
import socket
import sys
from login import start_login

class Client:
    def __init__(self, addr):
        self.sockfd = socket.socket()
        self.addr = addr
    def start_connect(self):
        '''连接服务器，实现功能'''
        self.sockfd.connect(self.addr)
        start_login(self.sockfd)


def run_client():
    ADDR = ('127.0.0.1', 9999)
    client=Client(ADDR)
    client.start_connect()


if __name__ == '__main__':
    run_client()




