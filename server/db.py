'''
Author:　秦浩
key technology: sqlite3
data:2018-6-9
describe:本模块用于数据的创建,共1个数据库２张表，一张用来存放用户的昵称和密码，第二张用来存放文件，供用户上传下载使用；

    数据库两张表
        userinfo

        login
        +--------+-----------+------+-----+---------+--------------+
        | Field  | Type      | Null | Key | Default | Extra        |
        +--------+-------------+------+-----+---------+------------+
        | id     | int(11)  | NO   | UNI | NULL    | auto_increment|
        | name   | char(15) | NO   | PRI | NULL    |               |
        | passwd | char(15) | NO   |     | NULL    |               |
        +--------+-------------+------+-----+---------+------------+
'''

import sqlite3

def main():
    db = sqlite3.connect('userinfo.db')
    c=db.cursor()
    sql='''CREATE TABLE login(
    id INTEGER primary key,
    name char(15),
    paswd char(15)
    )'''
    c.execute(sql)
    db.commit()
    # sql2 = "insert into login values(null, '初始管理员', '123');"
    # c.execute(sql2)
    # db.commit()
    db.close()
    print("数据库创建成功")

if __name__ == '__main__':
    main()