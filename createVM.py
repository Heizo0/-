import subprocess
import time
import sys

def get_ip_logic(self, vm_name, timeout=60):
    """
    自動獲取指定 VM 的 IP 位址
    vm_name: 虛擬機名稱
    timeout: 最長等待秒數（因為 VM 開機需要時間）
    """
    self._log(f"🔎 正在等待 VM 分配 IP 位址 (限時 {timeout} 秒)...")
    
    start_time = time.time()
    
    # 這裡的 '1' 通常代表第二張網卡 (Host-Only)，'0' 通常是第一張 (NAT)
    # 我們需要 Host-Only 的 IP 才能從主機連線
    prop_path = "/VirtualBox/GuestInfo/Net/1/V4/IP" 
    
    while time.time() - start_time < timeout:
        try:
            # 執行 VBoxManage 查詢指令
            cmd = ["VBoxManage", "guestproperty", "get", vm_name, prop_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            output = result.stdout.strip()
            
            # 如果成功獲取，輸出會是 "Value: 192.168.56.x"
            if "Value:" in output and "No value set" not in output:
                ip = output.replace("Value: ", "").strip()
                if ip:
                    self._log(f"✨ 成功獲取 IP: {ip}")
                    return ip
                    
        except subprocess.CalledProcessError:
            # 指令執行失敗（可能 VM 還在啟動中）
            pass
            
        # 每隔 2 秒檢查一次，避免過度消耗 CPU
        time.sleep(2)
    
    self._log("❌ 獲取 IP 超時。請確認 Guest Additions 是否已在模板中安裝。")
    return None

class VBoxManager:
    def __init__(self, log_callback=None):
        # log_callback 是一個函數，用來把訊息傳回給 GUI
        self.log_callback = log_callback

    def _log(self, message):
        if self.log_callback:
            self.log_callback(message)
        print(message) # 同時在控制台印出

    def create_and_start_vm(self, vm_name, base_name):
        self._log(f"正在克隆 VM: {vm_name}...")
        
        # 實際執行 VBoxManage
        cmd = ["VBoxManage", "clonevm", base_name, "--name", vm_name, "--register"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            self._log("✅ 克隆成功！")
            # 啟動 VM
            self._log("正在啟動 VM...")
            subprocess.run(["VBoxManage", "startvm", vm_name, "--type", "headless"])
            return True
        else:
            self._log(f"❌ 錯誤: {result.stderr}")
            return False
        
class K0sVMBuilder:
    def __init__(self, vm_name, base_vm_name):
        self.vm_name = vm_name
        self.base_vm_name = base_vm_name

    def _run_cmd(self, cmd_list):
        """執行指令並捕捉錯誤"""
        try:
            result = subprocess.run(
                ["VBoxManage"] + cmd_list,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ 指令執行失敗: {' '.join(e.cmd)}")
            print(f"錯誤訊息: {e.stderr}")
            return None

    def build_and_start(self):
        print(f"🚀 開始部署 VM: {self.vm_name}...")

        # 1. 複製虛擬機 (從基礎模板複製)
        # --register: 自動將新 VM 註冊到 VirtualBox 清單中
        print("📦 正在從模板克隆虛擬機...")
        self._run_cmd(["clonevm", self.base_vm_name, "--name", self.vm_name, "--register"])

        # 2. 配置硬體資源 (K0s 建議)
        # --memory: 1024MB, --cpus: 1, --vram: 16MB
        print("⚙️ 正在配置硬體資源...")
        self._run_cmd(["modifyvm", self.vm_name, 
                       "--memory", "1024", 
                       "--cpus", "1", 
                       "--vram", "16",
                       "--nic1", "nat",            # 第一張網卡：對外上網
                       "--nic2", "hostonly",       # 第二張網卡：主機溝通
                       "--hostonlyadapter2", "VirtualBox Host-Only Ethernet Adapter"])

        # 3. 啟動虛擬機
        # --type headless: 不顯示視窗，在背景執行
        print("⚡ 正在啟動虛擬機 (Headless 模式)...")
        self._run_cmd(["startvm", self.vm_name, "--type", "headless"])

        print(f"✅ VM {self.vm_name} 已成功啟動！")

    def get_status(self):
        """檢查 VM 目前狀態"""
        output = self._run_cmd(["showvminfo", self.vm_name, "--machinereadable"])
        if output:
            for line in output.splitlines():
                if line.startswith('VMState='):
                    return line.split('=')[1].strip('"')
        return "unknown"

# --- 實際調用 ---
if __name__ == "__main__":
    # 請確保你有一個名為 "Ubuntu_Base" 的現成虛擬機
    builder = K0sVMBuilder(vm_name="Pulsar_Edge_Node_1", base_vm_name="Ubuntu_Base")
    
    builder.build_and_start()
    
    # 輪詢檢查狀態
    for _ in range(10):
        status = builder.get_status()
        print(f"📊 當前狀態: {status}")
        if status == "running":
            print("🌟 VM 已就緒，可以開始 SSH 部署 K0s。")
            break
        time.sleep(2)