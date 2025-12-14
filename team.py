import tkinter as tk
from tkinter import ttk
import time 
def setLabText(text):
    lab.config(text=text)
def start():
    setLabText("開始測試(Start Deployment)")
    for i in range(1, 101):
        progress.set(i)
        window.update_idletasks()
        time.sleep(0.05)
    setLabText("完成(Complete Deployment)")
def testssh():
    setLabText("測試 (Test Connecting SSH)")
    setLabText("成功連線(SSH connect Successful)")
def browsessh():
    filedialog = X  #這邊寫SSH Public Key的檔案(查網路我也不太熟)
    filepath = filedialog.askopenfilename(title="Select SSH Public Key File (選擇公鑰檔案)", filetypes=[("Text Files", "*.pem;*.pub")])
    if filepath:
        label.config("選擇的公鑰檔案：", filepath)
    else:
        label.config(text="未選擇檔案")
def change():
    if On['text'] == "On (啟動)":
        On.config(text="Off (關閉)")
        setLabText("Virtual Box On(虛擬機已啟動)")
    else:
        On.config(text="On(啟動)")
        setLabText("Virtual Box Off(虛擬機已關閉)")
window = tk.Tk()
window.title("Edge Computing System(邊緣運算系統)")
window.geometry("800x600+940+50")
window.config(bg="#ddf556")
frame = tk.Frame(window, bg="#EB5F5F", width=750, height=200)
frame.pack(pady=20)
progress= tk.IntVar()
progressbar = ttk.Progressbar(frame, variable=progress, maximum=100, length=300)
progressbar.pack(pady=20)
lab = tk.Label(window, text="State of Edge Computing System (邊緣運算系統狀態)", width=50, height=2, bg="#e0f7fa")
lab.pack(pady=20)
label = tk.Label(window, text="No select SSH Public Key File(未選擇公鑰檔案)", width=50, height=2, bg="#e0f7fa")
label.pack(pady=10)
deploy = tk.Button(window, text="Start Deployment(開始部署)",width=50, height=2, command=start)
deploy.pack(pady=10)
test= tk.Button(window, text="Test SSH connecting (測試 SSH 連線)",width=50, height=2, command=testssh)
test.pack(pady=10)
key = tk.Button(window, text="Select SSH Public Key File(選擇公鑰檔案)",width=50, height=2, command=browsessh)
key.pack(pady=10)
On = tk.Button(window, text="On VM(啟動)",width=20, height=2, command=change)
On.pack(pady=10)
exit = tk.Button(window, text="Exit(退出)", width=20, height=2, command=window.quit)
exit.pack(pady=10)
window.mainloop()

