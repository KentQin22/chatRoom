"""
可能要用一个ListBox显示发生的活动
用canvas显示一个友好的图片
用按钮标注结束服务, 开始服务.

"""
import tkinter


class Server_Window():

    def __init__(self):
        self.main_screen = tkinter.Tk()

    def run_window(self):
        self.main_screen.title("chat server")
        self.main_screen.geometry("400x250+800+400")
        self.main_screen.resizable(0, 0)
        self.main_screen.mainloop()

