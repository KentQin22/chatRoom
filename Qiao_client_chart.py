# -*- coding:utf-8 -*-
"""
    Author : 向臣，乔茂垠，张玥

    chatroom server
    udp协议,多进程

    注册:注册成功插入数据库，用户名不能重名，密码不能有空格

    登陆成功后发送接收聊条消息

    父进程接收消息
    子进程发送消息

    退出：
    子进程退出发消息告知服务端，服务端返回消息告知父进程

    注册登录退出 ： username=#quit

    #$为请求类型和数据
    向服务端发送请求及消息格式
    请求类型 + #$ + 数据
    发送群聊信息： M#$data
    服务端通过 split('#$') 分割出 请求类型 和 真实数据

"""
import socket
import os
import getpass
import signal
import sys
import re

#此为处理客户端聊天类
class ClientChatOption:
    def __init__(self,s,addr):
        self.s=s
        self.addr=addr

    #客户端发送接收消息
    def do_chat(self):
        #创建多进程，主进程循环接收服务端消息，子进程发送消息
        pid=os.fork()

        if pid<0:
            print('创建子进程失败')
            return
        elif pid==0:
            #在子进程中处理发送消息
            while True:
                usermsg=input('发送消息:')
                if not usermsg:
                    print('确认退出聊天室 Y/N')
                    isquit=input('')
                    if isquit=='Y':
                        #确认退出，退出函数进入一级页面，关闭子进程
                        #通知服务端，服务端返回消息通知父进程
                        self.s.sendto(b'#Quit#$',self.addr)
                        sys.exit('客户端子进程退出')

                    else:
                        continue
                self.s.sendto(('#M#$'+usermsg).encode(),self.addr)
        else:
            #在父进程中处理聊天室消息
            while True:
                data,addr=self.s.recvfrom(2048)
                if data.decode()=='#Quit':
                    #子进程已退出，父进程退出聊天室函数进入以及界面循环
                    #sys.exit('父进程退出')
                    return
                print('接收到群聊消息：',data.decode())



#此为处理客户端注册登录类
class ClientLoginOption:
    def __init__(self,s,addr):
        self.s=s
        #客户端地址
        self.addr=addr

    #用户注册函数
    def user_register(self):
        while True:
            # 输入用户名 密码 （此处确认密码进行验证,如果两次密码输入不一致则重新输入）
            username = input('请输入用户名:')
            if not username:
                print('回车键及退出')
                return
            passwd = getpass.getpass('请输入密码:')
            comfirmpsw = getpass.getpass('请确认密码:')
            # 认证密码，密码不能包含空格
            comfirm_passwd=re.findall('[" "]+',passwd)
            print(comfirm_passwd)
            if len(comfirm_passwd) != 0:
                print('密码不能包含空格')
                continue
            if passwd != comfirmpsw:
                print('两次密码不一致，请重新输入')
                continue

            # 向服务端发送注册请求
            self.s.sendto(('R#$%s#$%s' % (username, passwd)).encode(), self.addr)

            # 收到服务端反馈消息，确认注册是否成功
            register_comfirm, addr = self.s.recvfrom(1024)
            register_comfirm = register_comfirm.decode()

            # 成功则直接调用登录函数
            if register_comfirm == 'OK':
                print('注册成功')
                break

            # 否则重新注册，此处用循环
            elif register_comfirm == 'user exists':
                print('用户名已经存在')
                continue
            else:
                print('注册失败，请重试')
                break


    #用户登录事件
    def user_login(self):
        while True:
            username=input('请输入用户名:')
            if not username:
                return
            password=getpass.getpass('请输入密码:')

            #发送给服务端验证
            self.s.sendto(('L#$%s#$%s'%(username,password)).encode(),self.addr)

            #接收消息，如果错误返回消息，如果正确进入聊天室
            data,addr=self.s.recvfrom(1024)
            data=data.decode()
            if data=='OK':
                print('登陆成功')
                #用户退出过后直接退出登录函数进入一级界面
                return
            elif data=='islogin':
                print('此用户已经登录，请勿重复登录')
            else:
                print('用户名输入有误1')

def main():
    #服务端地址
    HOST='127.0.0.1'
    PORT=9999
    ADDR=(HOST,PORT)

    #创建套接字
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)

    #处理僵尸进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    #创建客户端注册登录对象
    clo=ClientLoginOption(s,ADDR)

    # 创建客户端聊天信息对象
    cco = ClientChatOption(s, ADDR)


    while True:
        print('1注册  2登录 3退出')
        client_option=input('请选择:')

        #注册
        if client_option=='1':
            clo.user_register()
        #登录
        elif client_option=='2':
            clo.user_login()
            # 开始群聊
            cco.do_chat()
        #退出
        elif client_option=='3':
            print('客户端退出')
            os._exit(0)
            s.close()
            return
        else:
            print('输入操作有误，请重新选择')


if __name__=='__main__':
    main()
