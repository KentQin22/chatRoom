import sqlite3
import socket
import signal
import sys
import os
import server_login as sl

def main():
    ADDR = ('127.0.0.1', 9999)
    db = sqlite3.connect('customers.db')
    s=socket.socket()
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)
    #忽略子进程退出,防止僵尸产生
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    #等待客户端连接
    print('等待连接．．．')
    while True:
        try:
            #accept()是阻塞函数么？为什么这里没有阻塞？
            c, addr = s.accept()
        except KeyboardInterrupt:
            os._exit(0)
        except Exception:
            continue
        #创建子进程
        pid=os.fork()
        if pid<0:
            print('子进程创建失败')
            c.close()
        elif pid == 0:
            #对子进程来讲s是没有用的
            s.close()
            do_child(c,db)
        else:
            #对父进程来讲，ｃ是无用的，他只管连接
            c.close()
            continue


def do_child(c,db):
    while True:
        print('正在等客户端发送命令')
        data=c.recv(1024).decode()
        print('接到请求:',data)
        print(data[0])
        if data[0]=='R':
            sl.server_register(c,db,data)
        elif data[0]=='L':
            sl.server_login(c,db,data)
        elif data[0]=='C':
            print("聊天函数")
        elif data[0] == 'Q':
            print("退出聊天")



if __name__ == '__main__':
    main()