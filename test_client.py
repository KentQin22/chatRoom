import tkinter
import socket
import sys
import getpass
from ui_chat_client import Login_Window
import client_login as cl

def main():
    ADDR = ('127.0.0.1', 9999)
    # 创建套接字
    s = socket.socket()
    s.connect(ADDR)
    # 调用登录注册界面
    ld = Login_Window(cl.do_login, cl.do_register, s)
    ld.run_window()




if __name__ == '__main__':
    main()