
import tkinter
import socket
import sys
import getpass


def do_register(name, passwd, s, ld):
    '''得到用户注册名和密码 '''
    # 建立数据包
    msg ='R {} {}'.format(name ,passwd)
    if not msg:
        print(msg)
        #发送数据
        s.send(msg.encode())
        # 接收服务器反馈
        data =s.recv(1024).decode()
        # 对反馈进行判断
        if data =='OK':
            return 0
        elif data =='EXISTS':
            print('用户已存在')
            return 1
        else:
            return 1

def do_login(name, passwd, s, ld):

    msg ='L {} {}'.format(name ,passwd)
    if not msg:
        print(msg)
        s.send(msg.encode())
        data =s.recv(1024).decode()
        if data == 'OK':
            return name
        else:
            print('用户名或密码不正确')
            return 1



