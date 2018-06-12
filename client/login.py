'''
Author:　秦浩
key technology: TCP协议
data:2018-6-9
describe:本模块为客户端注册登录界面：
    start_login(套接字)
'''

#导入登录注册界面
from ui_chat_client import Chat_Window,msg_box_info,Login_Window
#导入上传文件，下载文件界面
from file_Down_Up import down_file, up_file
#导入管理员模块
from manager import remove_user
#导入聊天模块
from chat import recv_msg, send_msg



def _do_register(name, passwd, s):
    '''得到用户注册名和密码 '''
    # 建立数据包
    print("正在注册")
    msg ='R {} {}'.format(name ,passwd)
    if msg != '':
        print("用户信息输入完毕,取值成功信息为：",msg)
        #发送数据
        s.send(msg.encode())
        # 接收服务器反馈
        data =s.recv(1024).decode()
        # 对反馈进行判断
        if data =='OK':
            #创建聊天界面对象
            chatWindow=Chat_Window(down_file, up_file, remove_user, recv_msg, send_msg)
            #运行聊天窗口
            chatWindow.run_window()

            return 0
        elif data =='EXISTS':
            # print('用户已存在')
            msg_box_info("提示","用户已存在！")
            return 1
        else:
            return 1

def _do_login(name, passwd, s):
    '''得到用户登录名字和密码'''
    print("正在登录")
    msg ='L {} {}'.format(name ,passwd)
    print("用户信息输入完毕,取值成功，信息为：",msg)
    if msg != '':
        print(msg)
        s.send(msg.encode())
        data =s.recv(1024).decode()
        if data == 'OK':
            return name
        else:
            print('用户名或密码不正确')
            return 1

def start_login(socket):
    '''显示登录注册界面'''
    ld = Login_Window(_do_login, _do_register, socket)
    ld.run_window()