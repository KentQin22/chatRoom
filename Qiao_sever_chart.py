# -*- coding:utf-8 -*-
"""
    Author : 向臣，乔茂垠，张玥

    chatroom server
    udp协议

    数据库两张表
        userinfo
        +--------+-------------+------+-----+---------+----------------+
        | Field  | Type        | Null | Key | Default | Extra          |
        +--------+-------------+------+-----+---------+----------------+
        | id     | int(11)     | NO   | UNI | NULL    | auto_increment |
        | name   | varchar(30) | NO   | PRI | NULL    |                |
        | passwd | varchar(11) | NO   |     | NULL    |                |
        +--------+-------------+------+-----+---------+----------------+

        useronline
        +-------------+-------------+------+-----+---------+----------------+
        | Field       | Type        | Null | Key | Default | Extra          |
        +-------------+-------------+------+-----+---------+----------------+
        | id          | int(11)     | NO   | PRI | NULL    | auto_increment |
        | username    | varchar(30) | NO   | MUL | NULL    |                |
        | passwd      | varchar(30) | NO   |     | NULL    |                |
        | addressip   | varchar(20) | NO   |     | NULL    |                |
        | addressport | int(11)     | NO   |     | NULL    |                |
        +-------------+-------------+------+-----+---------+----------------+

        useronline username字段名 作为外键值 关联 userinfo 的name字段名

    新用户注册成功插入userinfo表

    登录后用户插入useronline表,退出后userinfo中删除该条记录,userinfo为在线表

    收到消息即发送给每一位在线用户

    实现注册 登录（检测重复登录） 实时群聊 返回登录列表，返回注册用户列表


"""
import socket
import sys
import time
import pymysql


# 此为数据库封装,处理数据库操作类
class DatabaseComfirm:
    # 用户注册数据库操作，userinfo添加用户信息
    def __init__(self, s, db, cursor, sql):
        self.s = s
        self.db = db
        self.cursor = cursor
        self.sql = sql

    # 执行数据库注册操作
    def mysqldb_register(self, usernames, passwds, addr):
        # 执行sql命令
        try:
            self.cursor.execute(self.sql)
            data = self.cursor.fetchone()
            if data is None:
                # 将用户信息插入数据库
                sql = "insert into userinfo(name,passwd) values('%s','%s')" % (usernames, passwds)
                print('看一下读到这儿没')
                try:
                    self.cursor.execute(sql)
                    self.db.commit()
                    self.s.sendto(b'OK', addr)
                    print('插入数据成功')
                    self.cursor.close()
                    self.db.close()
                    return
                except Exception as e:
                    print(e)
                    self.db.rollback()
                    self.cursor.close()
                    self.db.close()
                    self.s.sendto(b'fall', addr)
                    return
            else:
                self.cursor.close()
                self.db.close()
                self.s.sendto(b'user exists', addr)
        except Exception as e:
            print('sql操作有问题', e)
            self.cursor.close()
            self.db.close()
            self.s.sendto('fall'.encode(), addr)

    #检测是否重复登录
    def mysqldb_checklogin(self):

        try:
            self.cursor.execute(self.sql)
            data=self.cursor.fetchone()
            self.cursor.close()
            self.db.close()
            print('是否已有账号登录?',data)
            if data is None:
                return True
            else:
                return False
        except Exception as e:
            print(e)
            print('查询失败，请重新检测')
            self.cursor.close()
            self.db.close()




    # 执行数据库登录操作
    def mysqldb_login(self, usernames, passwds, addr, host, port):
        try:
            # 检测数据库中username 和passwds 是否存在且一致
            self.cursor.execute(self.sql)
            data = self.cursor.fetchone()
            print('sql data', data)

            #检测用户名密码是否正确
            if data is None:
                self.s.sendto(b'fall', addr)
                return

            # 检测用户是否已经登录
            # sql = "select * from useronline where username=usernames"
            db = pymysql.connect(
                host='localhost',
                user='root',
                passwd='123456',
                db='user',
                charset='utf8'
            )
            cursor = db.cursor()

            # 查找useronline表里是否存在username
            sql ="""select * from useronline where username='%s'"""%usernames

            #创建数据库操作对象
            checkRepeat = DatabaseComfirm(self.s,db,cursor,sql)

            #调用检测重复登录函数，返回布尔值
            isRepeat=checkRepeat.mysqldb_checklogin()

            if isRepeat == False:
                self.s.sendto(b'islogin', addr)
            else:
                self.s.sendto(b'OK', addr)
                print('欢迎%s进入聊天室' % usernames)

                # #将该用户加用户在线数据库, 同时 useronline 应该与 userinfo 外键值关联 ,用户退出聊天室在线表中删除该用户
                sql = """insert into useronline(username,passwd,addressip,addressport) values('%s','%s','%s','%d')""" % (usernames, passwds, host, port)

                try:
                    # 插入在线用户数据库
                    self.cursor.execute(sql)
                    print('在线用户插入数据成功')
                    self.db.commit()
                except Exception as e:
                    self.db.rollback()
                    print(e)
                    print('在线用户未能插入数据库')
            self.cursor.close()
            self.db.close()
        except Exception as e:
            print(e)
            print('验证失败')
            self.s.sendto(b'fall', addr)

    # 执行数据库退出操作
    def mysqldb_quit(self):
        try:
            self.cursor.execute(self.sql)
            self.db.commit()
            print('useronlien已经删除推出客户端')
        except Exception as e:
            print(e)
            print('从在线表中删除推出客户端失败')

        self.cursor.close()
        self.db.close()

    # 执行数据库聊天操作
    def mysqldb_chat(self, client_data):
        # 将消息转发给每一个在线客户端
        try:
            self.cursor.execute(self.sql)
            data = self.cursor.fetchall()
            print('fetchmany取出的在线用户', data)
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S')
            for i in data:
                self.s.sendto(("%s %s %s" % (nowtime, username, client_data)).encode(), i)
        except Exception as e:
            print(e)
            print('消息转发失败')
        self.cursor.close()
        self.db.close()

    #执行数据库查找用户名操作
    def mysqldb_serach(self):
        try:
            self.cursor.execute(self.sql)
            data = self.cursor.fetchone()[0]
            self.db.commit()
            print(data)
            self.cursor.close()
            self.db.close()
            return data
        except Exception as e:
            print(e)
            print('该用户不存在')
            self.cursor.close()
            self.db.close()

    # 返回注册用户信息表
    def mysqldb_regiser_user(self):
        # 链接数据库验证
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        sql = """select * from userinfo"""

        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            print('返回注册用户信息列表失败')
        cursor.close()
        db.close()

    # 返回在线用户信息表
    def mysqldb_online_user(self):
        # 链接数据库验证
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        sql = """select * from useronline"""

        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            return data
        except Exception as e:
            print(e)
            print('返回在线用户信息列表失败')
        cursor.close()
        db.close()



# 此为处理发送聊天室消息类
class DoChat:
    def __init__(self, s):
        self.s = s

    #处理聊天函数
    def do_chat(self, client_data, addr):
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        # 查找出在线所有用户
        sql = """select addressip,addressport from useronline"""

        # 查找发送该消息的用户的用户名
        username = self.search_user_name(addr)
        print('发送消息的用户：',username)

        # 创建数据库操作对象
        dochat = DatabaseComfirm(self.s, db, cursor, sql)

        # 执行数据库聊天函数
        dochat.mysqldb_chat(client_data, username)

    #处理查找发送消息的用户名函数
    def search_user_name(self, addr):
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        # 查找出发送该条信息的用户名
        print(addr[0], addr[1])
        sql = """select username from useronline where addressip='%s'and addressport='%d'""" % (addr[0], addr[1])

        # 创建数据库操作对象
        dosearch = DatabaseComfirm(self.s, db, cursor, sql)

        # 执行数据库聊天函数，返回用户名
        data=dosearch.mysqldb_serach()
        #再一次返回用户名
        return data



# 此为处理客户端注册，登录,退出类
class DoLogin:
    def __init__(self, s):
        self.s = s

    # 处理用户注册事件
    def client_register(self, data, addr):
        # 获取客户端注册的 用户名   密码
        usernames = data[1]
        passwds = data[2]

        # 连接数据库验证
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        sql = "select name from userinfo where name='%s'" % usernames

        # 创建数据库认证对象
        db_register = DatabaseComfirm(self.s, db, cursor, sql)

        # 执行数据库注册操作函数
        db_register.mysqldb_register(usernames, passwds, addr)

    # 处理用户登录
    def client_login(self, data, addr):
        usernames = data[1]
        passwds = data[2]
        host = addr[0]
        port = addr[1]
        print(usernames, passwds)
        # 链接数据库验证
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()
        sql = """select name,passwd from userinfo where name='%s' and passwd='%s'""" % (usernames, passwds)

        # 创建数据库认证对象
        db_login = DatabaseComfirm(self.s, db, cursor, sql)

        # 执行数据库登录操作函数
        db_login.mysqldb_login(usernames, passwds, addr, host, port)

    # 处理用户退出
    def client_quit(self, client_addr):
        # 发送消息告知客户端父进程已经出客户端
        self.s.sendto(b'#Quit', client_addr)

        # 从在线表中删除该用户
        # 链接数据库验证
        db = pymysql.connect(
            host='localhost',
            user='root',
            passwd='123456',
            db='user',
            charset='utf8'
        )
        cursor = db.cursor()

        sql = """delete from useronline where addressip='%s' and addressport='%d'""" % (client_addr[0], client_addr[1])

        # 创建数据库认证对象
        db_quit = DatabaseComfirm(self.s, db, cursor, sql)

        # 执行数据库退出操作函数
        db_quit.mysqldb_quit()


def main():
    # 创建数据包套接字  绑定服务端地址     重启端口
    HOST = '0.0.0.0'
    PORT = 9999
    ADDR = (HOST, PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ADDR)

    # 创建客户端登录注册对象
    dl = DoLogin(s)

    # 创建处理客户端聊天对象
    dc = DoChat(s)

    # 循环接收客户端消息
    while True:
        try:
            receive_data, client_addr = s.recvfrom(1024)
            receive_data = receive_data.decode().split('#$')

            # 客户端发起注册器请求
            if receive_data[0] == 'R':
                # 注册事件处理
                dl.client_register(receive_data, client_addr)

            # 客户端发起登录请求
            elif receive_data[0] == 'L':
                dl.client_login(receive_data, client_addr)

            # 该客户端已经退出，返回消息通知其父进程退出聊天室
            elif receive_data[0] == '#Quit':
                dl.client_quit(client_addr)

            # 接受客户端发送聊天信息，转发给每一位聊天用户
            elif receive_data[0] == '#M':
                dc.do_chat(receive_data[1], client_addr)
        except KeyboardInterrupt:
            sys.exit('程序退出')


if __name__ == '__main__':
    main()