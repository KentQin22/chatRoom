import tkinter

root = tkinter.Tk()
root.title("Test")
root.geometry("600x400+800+400")
root.resizable(0, 0)

FONT_STYLE1 = ("黑体", "12")
FONT_COLOR1 = "#AAAAAA"


server_frame = tkinter.Frame(root, width=60, height=10)
server_scroll = tkinter.Scrollbar(server_frame)
server_scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)
server_text = tkinter.Text(server_frame, width=10, height=10)
server_text["yscrollcommand"] = server_scroll.set
server_scroll["command"] = server_text.yview
server_frame.place(x=10, y=50)
server_text.pack()

t2 = tkinter.Text(root, width=10, height=5)
t2.pack(side="bottom")


def insert():
    server_text["state"] = "normal"
    server_text.insert(tkinter.END, t2.get("0.0", "end") + "\n")
    t2.delete(0.0, "end")
    server_text["state"] = "disable"

img = tkinter.PhotoImage(file="icons/upload_small.png")
btn = tkinter.Button(root,  image=img, command=insert)  # relief=tkinter.FLAT,
btn.pack(side="right")

root.mainloop()
