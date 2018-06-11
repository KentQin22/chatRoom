"""
作者: 王健吉
最后更新日期: 2018.6.2
使用: 聊天室的客户端图形界面
说明: Login_Window登录界面, Regist_Window注册子界面 
     Chat_Window聊天主界面, Down_Window下载界面, Up_Window上载界面, Manage_Window管理员才能用的管人
封装思想: 每个窗口类都应该接收其所对应的特定方法, 这是为了在外部功能块中导入本模块, 可以直接将描述好的外部函数传入模块就可以运行
声明Login_Windows对象: lw = Login_Windown(login_action, regist_action)
                       login_action是会创建chat_window对象的方法
                       regist_action是会创建Regist_Window对象的方法, 之后在由regist_window对象创建chat_window对象
声明Chat_window对象: cw = Chat_Window(down_file, up_file, remove_user, recv_msg, send_msg)
                      down_file是下载文件方法
                      up_file是上传文件方法
                      remove_user是管理人员的踢人方法
                      recv_msg是接收用户聊天信息的方法
                      send_msg是发送本地用户聊天到服务器的方法
"""

# 自定义模块
import weather
# 系统模块
import sys
import json
import time
import tkinter
from tkinter import messagebox


__all__ = ["AUTHORITY", "USER_LIST", "USERNAME", 
    "msg_box_err", "msg_box_info", 
    "Login_Window", "Regist_Window",
    "Chat_Window", 
    "Down_Window", "Up_Window", "Manage_Window"
]

FONT_STYLE1 = ("黑体", "12")
FONT_COLOR1 = "#AAAAAA"

AUTHORITY = True   # 设置用户权限的全局变量, None表示无权限, 有则为True
USER_LIST = list()   # 用户列表, 用于接收服务器返回的以登录用户
USERNAME = str()   # 当前用户的名称

USER_LIST = ["AAA", "BBB", "CCC", "DDD", "EEE"]   # 用户列表, 这里有内容是用于测试

def msg_box_err(title:"消息标题", message:"错哪了"):
    """弹出错误信息提示框"""
    title = str(title)
    message = str(message)
    tkinter.messagebox.showerror(title=title, message=message)


def msg_box_info(title:"消息标题", message:"说点啥"):
    """弹出提示信息"""
    title = str(title)
    message = str(message)
    tkinter.messagebox.showinfo(title=title, message=message)


class Login_Window():

    global AUTHORITY
    global USERNAME

    def __init__(self, login_action, regist_action, connfd):   # 需要传入登录方法
        self.login_screen = tkinter.Tk()
        self.user = tkinter.StringVar()   # 用户名变量
        self.passwd = tkinter.StringVar()   # 用户密码变量
        self.login_action = login_action   # 外部定义用户登录方法
        self.regist_action = regist_action   # 外部定义用户注册方法
        self.connfd=connfd #套接字

    def run_window(self):
        self.login_screen.title("登入")
        self.login_screen.geometry('400x250+800+400')
        self.login_screen.resizable(0, 0)
        # 添加控件
        self.label_entry()
        self.button()
        self.check_button()
        # self.image_icon()
        self.login_screen.mainloop()

    def label_entry(self):
        l1 = tkinter.Label(self.login_screen, text="用户名：")
        l2 = tkinter.Label(self.login_screen, text="密  码：")
        user_entry = tkinter.Entry(self.login_screen, textvariable=self.user)
        passwd_entry = tkinter.Entry(
            self.login_screen, textvariable=self.passwd, show='*')
        l1.place(x=95, y=50)
        l2.place(x=95, y=100)
        user_entry.place(x=150, y=50)
        passwd_entry.place(x=150, y=100)

    def button(self):
        btn_login = tkinter.Button(
            self.login_screen, text="登入", width=6, command=self._login_action)
        btn_regist = tkinter.Button(
            self.login_screen, text="注册", width=6, command=self._regist_action)
        btn_login.place(x=95, y=160)
        btn_regist.place(x=250, y=160)

    def check_button(self):
        self.ck_var = tkinter.IntVar()
        try:
            with open("data/user_info.json", "r") as file:
                data = json.loads(file)
            self.ck_var.set(data["remeber_me"])
        except:
            self.ck_var.set(False)
        ck_btn = tkinter.Checkbutton(self.login_screen, text="记住我", variable=self.ck_var, onvalue=True, offvalue=False)
        ck_btn["command"] = self.set_data_authoruty_none
        ck_btn.place(x=145, y=130)

    def image_icon(self):
        img = tkinter.PhotoImage(file="icons/login_icon.png")
        canvas = tkinter.Canvas(self.login_screen, bg='blue', width=300, height=150, )
        canvas.create_image(150, 75, anchor='center', image=img)
        canvas.pack(side="bottom")

    def set_data_authoruty_none(self):
        """可以用该方法改变用户权限, 将authority设置为None, 若果有权限, 调用下一个方法"""
        data = {
            "remeber_me": self.ck_var.get(),
            "user": self.user.get(),
            "passwd": self.passwd.get(),
            "authority": AUTHORITY,
            "city": None
        }
        with open("data/user_info.json", 'w') as file:
            json.dump(data, file)

    def set_data_authoruty_true(self):
        """可以用该方法改变用户权限, 将authority设置为True"""
        AUTHORITY = True
        data = {
            "remeber_me": self.ck_var.get(),
            "user": self.user.get(),
            "passwd": self.passwd.get(),
            "authority": AUTHORITY,
            "city": None
        }
        with open("data/user_info.json", 'w') as file:
            json.dump(data, file)

    def _login_action(self):
        """"点击登录按钮后的处理
            向服务器发送登录信息(用户self.user, 密码self.passwd), 并接收返回(所有用户列表, 本地用户authority)
            有权限的话应该将AUTHORITY变量转为True
            应该改变data/user_info.json中的权限数据, 输入用户authoity, 将为聊天窗口提供
        """
        if self.user.get() == "" or self.user.get() is None:
            msg_box_err("警告", "用户名不能为空!")
            return
        if self.passwd.get() == "" or self.passwd.get() is None:
            msg_box_err("警告", "密码不能为空!")
            return

        self.login_action(self.user.get(), self.passwd.get(), self.connfd, self)    # 调用传入的login_action方法
            
    def _regist_action(self):
        self.login_screen.withdraw()
        regist_screen = Regist_Window(self.regist_action, self.connfd)
        regist_screen.run_window()
        return regist_screen   # 会返回注册窗口对象


# 登录方法
def login_action(uname:"用户名", passwd:"密码", login_window:"登录窗对象"):
    global USERNAME
    global AUTHORITY
    global USER_LIST
    """
    传入用户名, 密码
    Login_Window._login_action的具体实现
    登入成功返回True, 失败返回FALSE
    向服务器发送登录请求, 并确认是否接收到, 成功服务器要返回用户列表和本地用户的权限
    USER_LIST用于存储转换为list的登录用户
    AUTHORITY用于存储返回的用户权限, 无则为None, 有则为True
    成功后请创建chat_Window对象, 关闭登录窗对象, 并让全局变量USERNAME=uname
    """
    login_window.withdraw()
    pass


class Regist_Window():

    global USERNAME

    def __init__(self, regist_action, connfd):   # 需要传入注册方法
        self.regist_screen = tkinter.Toplevel()
        self.regist_action = regist_action   # 外部定义的注册方法
        self.user = tkinter.StringVar()   # 用户名
        self.passwd = tkinter.StringVar()   # 用户密码
        self.connfd=connfd

    def run_window(self):
        self.regist_screen.title("向服务器提出注册")
        self.regist_screen.geometry('400x250+800+400')
        self.regist_screen.resizable(0, 0)
        # 添加控件
        self.label_entry()
        self.button()

        self.regist_screen.mainloop()

    def label_entry(self):
        l1 = tkinter.Label(self.regist_screen, text="用户名：")
        l2 = tkinter.Label(self.regist_screen, text="密  码：")
        user_entry = tkinter.Entry(self.regist_screen, textvariable=self.user)
        passwd_entry = tkinter.Entry(
            self.regist_screen, textvariable=self.passwd, show='*')
        l1.place(x=95, y=50)
        l2.place(x=95, y=100)
        user_entry.place(x=150, y=50)
        passwd_entry.place(x=150, y=100)

    def button(self):
        btn_regist_screen = tkinter.Button(
            self.regist_screen, text="注册并登入", width=12, command=self._regist_action)
        btn_regist = tkinter.Button(
            self.regist_screen, text="退出", width=6, command=self._quit)
        btn_regist_screen.place(x=95, y=160)
        btn_regist.place(x=250, y=160)

    def _regist_action(self):
        """注册并登入功能
            需要将用户名self.user, 密码self.passwd上传至服务器, 当服务器返回准许命令后, 然后转入聊天界面
            同时需要服务器返回已登录的用户列表
        """
        user = self.user.get()
        passwd = self.passwd.get()
        if user == "" or user is None:
            msg_box_err("警告", "用户名不能为空!")
            return
        if passwd == "" or passwd is None:
            msg_box_err("警告", "密码不能为空!")
            return
        self.regist_action( user, passwd, self.connfd, self)
        
    def _quit(self):
        sys.exit(0)


# 在外定义的注册方法, 需要传入注册类中
def regist_action(uname, passwd, regist_window:"注册窗对象"):
    global USERNAME
    global USER_LIST
    """注册功能, Regist_Window._regist_action方法将调用他
        向服务器发送用户名和密码
        成功返回True, 失败返回FALSE
        要将已经登录的用户返回, 转换为list, 传给USER_LIST变量
        登录成功请创建chat_window对象, 并让全局变量USERNAME=uname
    """
    #隐藏窗口
    regist_window.withdraw()
    pass


# 主聊天界面 
class Chat_Window():

    global AUTHORITY
    global USER_LIST

    def __init__(self, down_file:"下载方法", up_file:"上传方法", remove_user:"踢人方法", recv_msg:"收消息", send_msg:"传消息"):
        self.chat_screen = tkinter.Tk()
        self.down_file = down_file   # 导入的外部下载方法
        self.up_file = up_file   # 导入的外部上传方法
        self.remove_user = remove_user   # 导入的踢人方法
        self.recv_msg = recv_msg   # 导入的接收用户聊天消息的方法
        self.send_msg = send_msg  # 导入的发送用户聊天消息的方法
        self.to_send = str()   # 用来向服务器发送本地用户内容的容器
        self.to_show = str()   # 用来接收服务器聊天内容的容器

    def run_window(self):
        self.chat_screen.title("和大家说说话吧 --chat room")
        self.chat_screen.geometry("800x600+600+250")
        self.chat_screen.resizable(0, 0)
        # 添加控件
        self.chat_text()
        self.list_online()
        self.weather_label()
        self.user_label()
        self.button()

        self.chat_screen.mainloop()

    def chat_text(self):
        # 绑定拖动按钮的接收框
        server_frame = tkinter.Frame(self.chat_screen, width=10, height=30)
        server_scroll = tkinter.Scrollbar(server_frame)
        server_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.server_text = tkinter.Text(server_frame, width=78, height=30, state="disable")
        self.server_text["yscrollcommand"] = server_scroll.set
        server_scroll["command"] = self.server_text.yview
        server_frame.place(x=10, y=50)
        self.server_text.pack()
        # 绑定拖动按钮的输入框
        client_frame = tkinter.Frame(self.chat_screen, width=10, height=10)
        client_scroll = tkinter.Scrollbar(client_frame)
        client_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.client_text = tkinter.Text(client_frame, width=78, height=10) 
        self.client_text["yscrollcommand"] = client_scroll.set
        client_scroll["command"] = self.client_text.yview
        client_frame.place(x=10, y=460)
        self.client_text.pack()

    def list_online(self):
        user_frame = tkinter.Frame(self.chat_screen, width=30, height=-20)
        user_scroll = tkinter.Scrollbar(user_frame)
        user_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.user_list = tkinter.Listbox(user_frame, width=28, height=20)   # 在线用户
        self.user_list["yscrollcommand"] = user_scroll.set
        user_scroll["command"] = self.user_list.yview
        user_frame.place(x=580, y=50)
        self.user_list.pack()

        for info in USER_LIST:
            self.user_list.insert(tkinter.END, info)

    def button(self):
        send_btn = tkinter.Button(self.chat_screen, text="发送", width=6)
        can_manage = self.deal_authority()
        manage_btn = tkinter.Button(self.chat_screen, text="管理聊天人员", width=28, state=can_manage)
        send_btn.place(x=600, y=555)
        manage_btn.place(x=580, y=415)

        # down_img = tkinter.PhotoImage(file="./icons/download_small.png")
        # up_img = tkinter.PhotoImage(file="icons/upload_small.png")
        file_down = tkinter.Button(self.chat_screen, text="下载文件")
        file_up = tkinter.Button(self.chat_screen, text="上载文件")
        file_down.place(x=10, y=10)
        file_up.place(x=80, y=10)

        wea_btn = tkinter.Button(self.chat_screen, text="↻", command=self.refresh_weather)
        wea_btn.place(x=755, y=7)

        send_btn["command"] = self.msg_show
        manage_btn["command"] = self.manage_user_window

        file_down["command"] = self.download_file_window
        file_up["command"] = self.upload_file_window

    def weather_label(self):
        value_str = str()
        wea_dic = dict()
        self.weastr = tkinter.StringVar()
        with open("data/user_info.json", "r") as file:
            data = json.loads(file.read())
        if not data["city"]:
            city = "成都"
        else:
            city = data["city"]
        try:
            wea_obj = weather.Weather(city)
            wea_dic = wea_obj.get_weather()
        except:
            value_str = "网络出错, 天气无法显示."
        wea_lab = tkinter.Label(self.chat_screen, textvariable=self.weastr, width=88, height=1, bg="white", anchor="w")
        if wea_dic is None:
            value_str = "网络出错, 天气无法显示."
        else:
            for x in wea_dic.items():
                if x[0] in ("今日天气", "平均温度", "最高温度", "最低温度", "PM2.5", "空气质量", "风力"):
                    value_str += str(x[0]) + ": " + str(x[1]) + " "
        self.weastr.set(value_str)
        wea_lab.place(x=155, y=10)

    def user_label(self):
        usrstr = tkinter.StringVar()
        usrstr.set("当前用户: " + str(USERNAME))
        user_label = tkinter.Label(self.chat_screen, textvariable=usrstr, width=10, bg="yellow", anchor="w")
        user_label.place(x=580, y=445)
    
    def refresh_weather(self):
        value_str = str()
        wea_dic = dict()
        with open("data/user_info.json", "r") as file:
            data = json.loads(file.read())
        if not data["city"]:
            city = "成都"
        else:
            city = data["city"]
        try:
            wea_obj = weather.Weather(city)
            wea_dic = wea_obj.get_weather()
        except:
            value_str = "网络出错, 天气无法显示."
        if wea_dic is None:
            value_str = "网络出错, 天气无法显示."
        else:
            for x in wea_dic.items():
                if x[0] in ("今日天气", "平均温度", "最高温度", "最低温度", "PM2.5", "空气质量", "风力"):
                    value_str += str(x[0]) + ": " + str(x[1]) + " "
        self.weastr.set(value_str)

    # 调用下载文件子窗口
    def download_file_window(self):
        """可添加对下载的一些功能"""
        down_obj = Down_Window(down_file, ['a', 'b', 'c'])   # 创建下载窗口对象并传入下载的具体方法
        down_obj.run_window()

    # 调用上传文件子窗口
    def upload_file_window(self):
        """可添加对上传的一些功能"""
        up_obj = Up_Window(up_file)
        up_obj.run_window()

    # 调用管理用户子窗口
    def manage_user_window(self):
        """调用管理用户的子窗口, 写在内部方便传参"""
        man_obj = Manage_Window(remove_user, self.user_list)
        man_obj.run_window()

    def deal_authority(self, authority=AUTHORITY):
        """当AUTHORITY全局变量为True时, 管理员权限将被开启"""
        if authority is None:
            try:
                with open("data/user_info.json", "r") as file:
                    data = json.loads(file)
                if data["authority"] is not None:
                    can_manage = "normal"
                else:
                    can_manage = "disabled"
            except:
                can_manage = "disabled"
            return can_manage
        elif authority is True:
            return "normal"
        else:
            raise ValueError("authrity 取值错误")

    def msg_show(self):
        """
        将本地聊天输入栏中的内容发送给服务器, 本地发送数据给服务器时调用这个方法
        """
        self.to_send = self.client_text.get("0.0", "end") + "\n"   # 获取输入框内容, 即本地聊天内容, 保存在self.to_send
        self.send_msg(self.to_send)   # 将内容发送给服务器, 具体函数第一在下
        self.server_text["state"] = "normal"
        self.server_text.insert(tkinter.END, self.to_send)
        self.client_text.delete(0.0, "end")
        self.server_text["state"] = "disable"

    def insert_msg(self):
        """
        将用户聊天内容插入聊天框, 从服务器收消息时调用这个方法
        """
        self.to_show = self.recv_msg()   # 接收从recv_msg接收到的消息, 保存在self.to_show
        self.server_text["state"] = "normal"
        self.server_text.insert(tkinter.END, self.to_show + "\n")
        self.server_text["state"] = "disable"


# 接收所有用户的聊天信息
def recv_msg():
    """用于接收服务器发回的聊天消息,
        每一名用户向服务器发送了聊天消息, 服务器都应该将内容发送出来, 该方法就是接收
        出错用msg_box_err方式提醒
        返回格式化的各个用户的聊天内容
    """
    return str("消息")

# 发送本地用户消息给服务器
def send_msg(value):
    """
    在Chat_window.msg_show方法中使用, 前者是获取本地的输入
    而本方法就是将获取的内容发送出去
    如果接收到服务器发回错误, 得调用msg_bos_err方式提醒
    """
    pass


# 下载子窗口
class Down_Window():

    def __init__(self, down_file:"外部定义的下载文件的方法", file_list:"服务器传来的文件名列表"):
        self.down_screen = tkinter.Toplevel()
        self.down_file = down_file   # 外部定义的下载方法
        self.file_list = file_list

    def run_window(self):
        self.down_screen.title("文件下载")
        self.down_screen.geometry("270x250+850+500")
        self.down_screen.resizable(0, 0)
        # 添加控件
        self.list_file()
        self.button()

        self.down_screen.mainloop()

    def list_file(self):
        list_frame = tkinter.Frame(self.down_screen, width=20, height=10)
        list_scroll = tkinter.Scrollbar(list_frame)
        list_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.list_box = tkinter.Listbox(list_frame, width=20, height=12)
        self.list_box["yscrollcommand"] = list_scroll.set
        list_scroll["command"] = self.list_box.yview

        list_frame.place(x=20, y=10)
        self.list_box.pack()

        for info in self.file_list:
            self.list_box.insert(tkinter.END, info)

    def button(self):
        btn1 = tkinter.Button(self.down_screen, text="下载", width=6)
        btn2 = tkinter.Button(self.down_screen, text="返回", width=6)
        btn1.place(x=200, y=10)
        btn2.place(x=200, y=50)

        btn1["command"] = self.down_file_name
        btn2["command"] = self._quit

    def down_file_name(self):
        value = self.list_box.get(self.list_box.curselection())   # 根据当前选择index获取内容
        self.down_file(value)   # 下载文件功能, 这是由外部定义并传入

    def _quit(self):
        self.down_screen.withdraw()


# 外部定义下载方法
def down_file(value):
    """向服务器传送文件名, 然后让服务器下载, 返回错误使用msg_box_err提醒"""
    pass


# 上传子窗口
class Up_Window():

    def __init__(self, up_file:"具体的上传方法"):
        self.up_screen = tkinter.Toplevel()
        self.file_address = tkinter.StringVar()   # 输入的要上传的文件绝对路径
        self.up_file = up_file   # 外部定义的上传方法

    def run_window(self):
        self.up_screen.title("文件上载")
        self.up_screen.geometry("350x110+850+400")
        self.up_screen.resizable(0, 0)
        # 添加控件
        self.label_entry()
        self.button()

        self.up_screen.mainloop()

    def label_entry(self):
        l1 = tkinter.Label(self.up_screen, text="文件绝对路径: ")
        l1.place(x=10, y=10)
        en1 = tkinter.Entry(self.up_screen, textvariable=self.file_address, width=45)
        en1.place(x=10, y=40)

    def button(self):
        up_btn = tkinter.Button(self.up_screen, text="上载", width=6)
        quit_btn = tkinter.Button(self.up_screen, text="返回", width=6)
        up_btn.place(x=80, y=70)
        quit_btn.place(x=220, y=70)

        up_btn["command"] = self.up_file_name
        quit_btn["command"] = self._quit

    def up_file_name(self):
        """上传文件的方法, 输入的是一个文件的绝对路径"""
        value = self.file_address   # 获取输入的聚堆路径
        try:
            file = open(value, "rb")
            file.close()
        except IOError:
            msg_box_err("文件错误", "打开文件失败, 请核实文件路径.")
        else:
            self.up_file(value)   # 外部定义的相传文件的方法

    def _quit(self):
        self.up_screen.withdraw()


# 文件上传实现函数
def up_file(value):
    """
    value是上传文件本地绝对地址
    文件存在判断已经写了, 请完成上传
    将本地文件打开, 上传到服务器, 出错使用msg_box_err提醒
    """
    pass


# 用户管理子窗口
class Manage_Window():

    global USER_LIST

    def __init__(self, remove_user:"具体的踢人方法", user_list:"chat_window的用户列对象"):
        self.manage_screen = tkinter.Toplevel()
        self.remove_user = remove_user   # 外部定义的踢人方法
        self.user_list = user_list

    def run_window(self):
        self.manage_screen.title("人员管理")
        self.manage_screen.geometry("270x250+850+500")
        self.manage_screen.resizable(0, 0)
        # 添加控件
        self.list_user()
        self.button()

        self.manage_screen.mainloop()

    def list_user(self):
        list_frame = tkinter.Frame(self.manage_screen, width=20, height=15)
        list_scroll = tkinter.Scrollbar(list_frame)
        list_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.list_box = tkinter.Listbox(list_frame, width=20, height=12)
        self.list_box["yscrollcommand"] = list_scroll.set
        list_scroll["command"] = self.list_box.yview

        list_frame.place(x=20, y=10)
        self.list_box.pack()
        for info in USER_LIST:
            self.list_box.insert(tkinter.END, info)

    def button(self):
        btn1 = tkinter.Button(self.manage_screen, text="移除该人")
        btn2 = tkinter.Button(self.manage_screen, text="返回", width=7)
        btn1.place(x=200, y=10)
        btn2.place(x=200, y=50)

        btn1["command"] = self.remove_user_name
        btn2["command"] = self._quit

    def remove_user_name(self):
        """获取列表选中的值, 将是要通知服务器踢出的用户名"""
        value = self.list_box.get(self.list_box.curselection())   # 通过当前选择的index获取内容
        if value == USERNAME:
            sys.exit(0)
        self.remove_user(value)   # 踢人功能
        USER_LIST.remove(value)
        self.list_box.delete(0, tkinter.END)   # 用户管理子窗口
        self.user_list.delete(0, tkinter.END)    # 聊天主界面列表
        for info in USER_LIST:
            self.list_box.insert(tkinter.END, info)
            self.user_list.insert(tkinter.END, info)

    def _quit(self):
        self.manage_screen.withdraw()


# 用户管理实现函数
def remove_user(value):
    """踢人函数, 收到用户名, 通知服务器踢人"""
    pass


if __name__ == "__main__":

    # 以下是一些用来测试的示例

    # a = Login_Window(login_action, regist_action)
    # a.run_window()


    b = Chat_Window(down_file, up_file, remove_user, recv_msg, send_msg)
    b.run_window()
