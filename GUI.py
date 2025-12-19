import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import time
from createVM import VBoxManager
from deployK0s import K0sDeployer

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("K0s 邊緣節點自動部署工具")
        self.root.geometry("600x500")

        # 設定 UI 元件
        self.create_widgets()

    def update_log(self, message):
        """這就是傳給邏輯層的 callback 函式"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_deploy(self):
        vm_name = self.vm_name_entry.get()
        base_name = self.base_vm_entry.get()
        
        # 在執行緒中跑，才不會卡住 GUI
        threading.Thread(target=self.worker, args=(vm_name, base_name)).start()

    def worker(self, vm_name, base_name):
        self.deploy_btn.config(state="disabled")
        # 直接呼叫物件的方法，它內部會跑 subprocess
        
        # 1. 建立並啟動 VM
        vbox = VBoxManager(log_callback=self.update_log)
        if not vbox.create_and_start_vm(vm_name, base_name):
            return

        # 2. 獲取 IP 
        self.update_log("🔍 正在獲取 VM IP 位址...")
        time.sleep(15)  # 等待系統啟動網路
        vm_ip = self.vbox.get_ip_logic(vm_name) 

        if vm_ip:
            # 3. 部署 K0s
            deployer = K0sDeployer(log_callback=self.update_log)
            if deployer.connect(vm_ip, "your_username", "your_password"):
                deployer.execute_k0s_install()
                self.update_log("🚀 K0s 邊緣節點部署完全成功！")
            else:
                self.update_log("❌ 無法透過 SSH 連線至 VM。")  
        else:
            self.update_log("❌ 無法獲取 VM 的 IP 位址。")

        self.deploy_btn.config(state="normal")

    def create_widgets(self):
        # --- 輸入區域 ---
        input_frame = ttk.LabelFrame(self.root, text="部署配置", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="VM 名稱:").grid(row=0, column=0, sticky="w")
        self.vm_name_entry = ttk.Entry(input_frame)
        self.vm_name_entry.insert(0, "K0s-Edge-Node-1")
        self.vm_name_entry.grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(input_frame, text="基礎模板:").grid(row=1, column=0, sticky="w")
        self.base_vm_entry = ttk.Entry(input_frame)
        self.base_vm_entry.insert(0, "Ubuntu_Base")
        self.base_vm_entry.grid(row=1, column=1, sticky="ew", padx=5)

        # --- 控制按鈕 ---
        btn_frame = ttk.Frame(self.root, padding=10)
        btn_frame.pack(fill="x")

        self.deploy_btn = ttk.Button(btn_frame, text="開始自動部署", command=self.start_deployment_thread)
        self.deploy_btn.pack(side="left", padx=5)

        self.status_label = ttk.Label(btn_frame, text="狀態: 準備就緒", foreground="blue")
        self.status_label.pack(side="right", padx=5)

        # --- 日誌顯示區域 ---
        log_frame = ttk.LabelFrame(self.root, text="部署日誌", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = tk.Text(log_frame, height=15, state="disabled", background="#f0f0f0")
        self.log_text.pack(fill="both", expand=True)

    def log(self, message):
        """將訊息插入日誌視窗"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def start_deployment_thread(self):
        """啟動執行緒，避免 GUI 凍結"""
        self.deploy_btn.config(state="disabled")
        thread = threading.Thread(target=self.run_deployment_process)
        thread.start()

    def run_deployment_process(self):
        vm_name = self.vm_name_entry.get()
        base_name = self.base_vm_entry.get()

        try:
            # 步驟 1: 克隆並啟動 VM
            self.status_label.config(text="狀態: 正在建立 VM...", foreground="orange")
            self.log(f"正在從 {base_name} 克隆 {vm_name}...")
            subprocess.run(["VBoxManage", "clonevm", base_name, "--name", vm_name, "--register"], check=True)
            self.log("VM 克隆成功 (模擬)...") 
            
            self.log(f"正在啟動 {vm_name} (Headless)...")
            subprocess.run(["VBoxManage", "startvm", vm_name, "--type", "headless"], check=True)
            
            # 步驟 2: 輪詢 IP
            self.status_label.config(text="狀態: 等待 IP 分配...", foreground="orange")
            vm_ip = None
            for i in range(10):
                self.log(f"嘗試獲取 IP ({i+1}/10)...")
                vm_ip = self.get_ip_logic(vm_name) 
                time.sleep(2)
                if i == 2: vm_ip = "192.168.56.101" # 模擬獲取成功
                if vm_ip: break
            
            if not vm_ip:
                raise Exception("無法獲取 VM IP 位址")

            self.log(f"成功連線至 IP: {vm_ip}")

            # 步驟 3: SSH 部署 K0s
            self.status_label.config(text="狀態: 正在部署 K0s...", foreground="green")
            self.log("正在執行 K0s 安裝指令...")
            time.sleep(3) # 模擬 SSH 執行時間
            
            self.log("✅ K0s 叢集部署完成！")
            self.log("🚀 Pulsar 邊緣代理程式已啟動。")
            self.status_label.config(text="狀態: 部署成功", foreground="blue")
            messagebox.showinfo("完成", f"VM {vm_name} 部署完成！\nIP: {vm_ip}")

        except Exception as e:
            self.log(f"❌ 錯誤: {str(e)}")
            self.status_label.config(text="狀態: 部署失敗", foreground="red")
        finally:
            self.deploy_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()