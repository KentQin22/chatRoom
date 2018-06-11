'''
Author:　秦浩
data:2018-6-9
describe:本模块包含连个函数，分别是注册模块和登录模块；
    登录模块：server_login(套接字,数据库对象,传入信息)；
    注册模块：server_register(套接字,数据库对象,传入信息)；
'''


import sqlite3

def server_register(c,db,data):
    '''用户注册'''
    print('正在注册中...')
    l=data.split(' ')
    name=l[1]
    passwd=l[2]
    cursor=db.cursor()
    sql="select * from login where name='%s' "%name
    cursor.execute(sql)
    r=cursor.fetchone()
    print(r)
    if r != None:
        c.send('EXISTS'.encode())
        return
    sql="insert into login values(null, '%s', '%s')"%(name,passwd)
    print(sql)
    try:
        cursor.execute(sql)
        #提交到数据库
        db.commit()
        c.send('OK'.encode())
    except:
        c.send('FALL'.encode())
        db.rollback()
        return
    else:
        print('注册成功')


def server_login(c,db,data):
    '''用户登录'''
    print('登录操作')
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    try:
        sql = "select * from login where name='%s'and password='%s' " % (name, passwd)
        cursor.execute(sql)
        r = cursor.fetchone()
    except:
        print('登录出现错误')
    if r == None:
        c.send('FALL'.encode())
    else:
        c.send('OK'.encode())
    cursor.close()
