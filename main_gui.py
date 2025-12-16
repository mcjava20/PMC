import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import subprocess
import threading

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft启动器")
        self.root.geometry("800x700")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10), padding=5)
        self.style.configure("TLabel", font=("微软雅黑", 12))
        self.style.configure("Title.TLabel", font=("微软雅黑", 16, "bold"))
        self.style.configure("Subtitle.TLabel", font=("微软雅黑", 14, "bold"))
        
        # 获取cmcl.exe路径
        import sys
        import os
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            self.exe_dir = os.path.dirname(sys.executable)
        else:
            # 未打包的情况
            self.exe_dir = os.getcwd()
        self.cmcl_path = os.path.join(self.exe_dir, "cmcl.exe")
        
        # 检查cmcl.exe是否存在
        if not os.path.exists(self.cmcl_path):
            messagebox.showerror("错误", f"未找到cmcl.exe文件，请确保它在 {os.getcwd()} 目录下")
            self.root.destroy()
            return
        
        # 创建日志区域
        self.create_log_widget()
        
        # 创建主界面
        self.create_main_interface()
        
        # 启动时执行的命令
        self.log_message("正在初始化启动器...")
        self.execute_command(self.cmcl_path, show_output=True)
        self.log_message("启动器初始化完成")
        
    def log_message(self, message):
        """在日志区域显示消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        
    def select_download_source(self):
        """弹出选择对话框让用户选择下载源"""
        import tkinter.simpledialog
        
        while True:
            source = tkinter.simpledialog.askstring(
                "选择下载源", 
                "[0]官方\n[1]BMCLAPI\n首次下载请选择下载源(默认为1，存储为配置 downloadSource)："
            )
            
            if source is None:
                # 用户取消选择
                return None
            
            source = source.strip()
            if source == "" or source == "1":
                # 默认或选择BMCLAPI
                return 1
            elif source == "0":
                # 选择官方
                return 0
            else:
                # 输入无效，提示用户重新输入
                tkinter.messagebox.showwarning("输入无效", "请输入0或1选择下载源")
                
    def read_config(self):
        """读取cmcl.json配置文件"""
        import json
        import os
        import sys
        
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            config_path = os.path.join(self.exe_dir, "cmcl.json")
        else:
            # 未打包的情况
            config_path = os.path.join(os.getcwd(), "cmcl.json")
        
        if not os.path.exists(config_path):
            # 如果配置文件不存在，创建默认配置
            default_config = {
                "language": "zh",
                "downloadSource": 1,
                "accounts": []
            }
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
        
        # 读取现有配置
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # 确保配置包含所有必要字段
        if "language" not in config:
            config["language"] = "zh"
        if "downloadSource" not in config:
            config["downloadSource"] = 1
        if "accounts" not in config:
            config["accounts"] = []
            
        return config
        
    def save_config(self, config):
        """保存配置到cmcl.json"""
        import json
        import os
        import sys
        
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            config_path = os.path.join(self.exe_dir, "cmcl.json")
        else:
            # 未打包的情况
            config_path = os.path.join(os.getcwd(), "cmcl.json")
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        self.log_message(f"配置文件已保存到: {config_path}")
        
    def update_download_source(self, source):
        """更新下载源配置"""
        config = self.read_config()
        config["downloadSource"] = source
        self.save_config(config)
        self.log_message(f"下载源已更新为: {'官方' if source == 0 else 'BMCLAPI'}")
        
    def execute_command(self, command, show_output=False, wait_for_completion=True):
        """执行系统命令"""
        import time
        import queue
        import threading
        
        def run_cmd():
            start_time = time.time()
            self.log_message(f"【命令执行开始】")
            self.log_message(f"  命令内容: {command}")
            self.log_message(f"  显示输出: {show_output}")
            self.log_message(f"  等待完成: {wait_for_completion}")
            
            try:
                self.log_message(f"  开始执行命令...")
                process = subprocess.Popen(
                    command, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding='gbk'  # 使用GBK编码处理中文
                )
                
                self.log_message(f"  命令进程已启动，PID: {process.pid}")
                
                # 创建输出队列
                output_queue = queue.Queue()
                
                # 输出读取线程
                def read_output():
                    try:
                        while True:
                            line = process.stdout.readline()
                            if not line:
                                break
                            output_queue.put(line)
                    except Exception as e:
                        self.log_message(f"【输出读取线程错误】: {e}")
                
                # 启动输出读取线程
                output_thread = threading.Thread(target=read_output, name=f"OutputThread-{process.pid}")
                output_thread.daemon = True
                output_thread.start()
                
                if wait_for_completion:
                    self.log_message(f"  正在获取命令输出...")
                    
                    # 根据show_output决定是收集输出还是显示输出
                    if show_output:
                        output_lines = []
                    else:
                        stdout_content = []
                    
                    while True:
                        try:
                            # 从队列获取输出（超时0.1秒）
                            line = output_queue.get(timeout=0.1)
                            stripped_line = line.strip()
                            
                            if show_output:
                                output_lines.append(stripped_line)
                                self.log_message(f"    {stripped_line}")
                            else:
                                stdout_content.append(stripped_line)
                        except queue.Empty:
                            if process.poll() is not None:  # 进程结束
                                break
                            else:
                                # 继续循环等待输出
                                continue
                        except Exception as e:
                            self.log_message(f"【输出处理错误】: {e}")
                            import traceback
                            traceback_lines = traceback.format_exc().splitlines()
                            self.log_message(f"  堆栈跟踪:")
                            for line in traceback_lines:
                                self.log_message(f"    {line}")
                            break
                
                # 等待进程结束
                exit_code = process.wait()
                end_time = time.time()
                
                # 等待输出线程结束
                output_thread.join(timeout=1.0)
                
                # 处理剩余输出
                while not output_queue.empty():
                    line = output_queue.get_nowait()
                    stripped_line = line.strip()
                    if show_output:
                        output_lines.append(stripped_line)
                        self.log_message(f"    {stripped_line}")
                    else:
                        stdout_content.append(stripped_line)
                
                self.log_message(f"  命令执行完成")
                self.log_message(f"  进程退出码: {exit_code}")
                self.log_message(f"  执行时间: {end_time - start_time:.2f} 秒")
                
                if show_output:
                    self.log_message(f"  输出行数: {len(output_lines)}")
                else:
                    if stdout_content:
                        self.log_message(f"  标准输出 (共{len(stdout_content)}行):")
                        for line in stdout_content[:10]:  # 只显示前10行
                            self.log_message(f"    {line}")
                        if len(stdout_content) > 10:
                            self.log_message(f"    ... 省略 {len(stdout_content) - 10} 行")
                
                # 检查退出码，如果失败且需要等待完成，则抛出异常
                if exit_code != 0 and wait_for_completion:
                    raise subprocess.CalledProcessError(
                        returncode=exit_code,
                        cmd=command,
                        stdout='\n'.join(output_lines if show_output else stdout_content),
                        stderr=''
                    )
                
            except subprocess.CalledProcessError as e:
                end_time = time.time()
                self.log_message(f"【命令执行失败】")
                self.log_message(f"  错误类型: CalledProcessError")
                self.log_message(f"  退出码: {e.returncode}")
                self.log_message(f"  执行时间: {end_time - start_time:.2f} 秒")
                
                if e.stdout:
                    stdout_lines = e.stdout.strip().splitlines()
                    self.log_message(f"  标准输出:")
                    for line in stdout_lines:
                        self.log_message(f"    {line}")
                
                if e.stderr:
                    stderr_lines = e.stderr.strip().splitlines()
                    self.log_message(f"  标准错误:")
                    for line in stderr_lines:
                        self.log_message(f"    {line}")
                
                self.log_message(f"  完整错误信息: {e}")
            except FileNotFoundError as e:
                end_time = time.time()
                self.log_message(f"【命令执行失败】")
                self.log_message(f"  错误类型: FileNotFoundError")
                self.log_message(f"  执行时间: {end_time - start_time:.2f} 秒")
                self.log_message(f"  错误信息: {e}")
                self.log_message(f"  可能原因: 命令不存在或路径错误")
            except PermissionError as e:
                end_time = time.time()
                self.log_message(f"【命令执行失败】")
                self.log_message(f"  错误类型: PermissionError")
                self.log_message(f"  执行时间: {end_time - start_time:.2f} 秒")
                self.log_message(f"  错误信息: {e}")
                self.log_message(f"  可能原因: 权限不足")
            except Exception as e:
                end_time = time.time()
                self.log_message(f"【命令执行失败】")
                self.log_message(f"  错误类型: {type(e).__name__}")
                self.log_message(f"  执行时间: {end_time - start_time:.2f} 秒")
                self.log_message(f"  错误信息: {e}")
                
                # 打印完整的堆栈跟踪
                import traceback
                traceback_lines = traceback.format_exc().splitlines()
                self.log_message(f"  堆栈跟踪:")
                for line in traceback_lines:
                    self.log_message(f"    {line}")
        
        # 在新线程中执行命令，避免界面冻结
        self.log_message(f"【线程创建】创建新线程执行命令")
        thread = threading.Thread(target=run_cmd, name=f"CmdThread-{command[:20]}")
        thread.daemon = True
        thread.start()
        self.log_message(f"  线程ID: {thread.ident}")
        self.log_message(f"  线程名称: {thread.name}")
        
    def create_log_widget(self):
        """创建日志显示区域"""
        log_frame = ttk.Frame(self.root)
        log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        log_label = ttk.Label(log_frame, text="日志输出", style="Subtitle.TLabel")
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=10, 
            font=("Consolas", 10),
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
    def create_main_interface(self):
        """创建主界面"""
        # 创建标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(pady=10, padx=10, fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="Minecraft 启动器", style="Title.TLabel")
        title_label.pack()
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill=tk.BOTH)
        
        # 创建按钮网格
        buttons = [
            ("启动游戏", self.launch_game),
            ("列出版本", self.list_versions),
            ("选择版本", self.select_version),
            ("显示帮助", self.show_help),
            ("安装版本", self.install_version),
            ("退出", self.exit_launcher),
            ("账号操作", self.account_operations),
            ("更改启动器配置", self.change_config),
            ("模组搜索", self.search_mods),
            ("整合包搜索", self.search_modpacks)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, width=20)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky=tk.EW)
        
        # 让按钮框架自适应大小
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
    
    def launch_game(self):
        """启动游戏"""
        # 检查账户状态
        config = self.read_config()
        
        # 检查是否有账户
        if not config.get("accounts") or len(config.get("accounts", [])) == 0:
            tk.messagebox.showerror("错误", "没有找到账户，请先登录账户")
            return
        
        # 检查是否有选中的账户
        has_selected_account = any(account.get("selected", False) for account in config.get("accounts", []))
        if not has_selected_account:
            tk.messagebox.showerror("错误", "没有选中的账户，请先选择账户")
            return
        
        # 检查是否已经配置了下载源
        if "downloadSource" not in config:
            # 选择下载源
            source = self.select_download_source()
            if source is None:
                return  # 用户取消选择
            
            # 更新下载源配置
            self.update_download_source(source)
        
        # 获取版本号并启动游戏
        version = simpledialog.askstring("启动游戏", "请输入版本号：")
        if version:
            self.execute_command(f"{self.cmcl_path} {version}")
    
    def list_versions(self):
        """列出版本"""
        self.execute_command(f"{self.cmcl_path} --list", show_output=True)
    
    def select_version(self):
        """选择版本"""
        # 检查是否已经配置了下载源
        config = self.read_config()
        if "downloadSource" not in config:
            # 选择下载源
            source = self.select_download_source()
            if source is None:
                return  # 用户取消选择
            
            # 更新下载源配置
            self.update_download_source(source)
        
        # 创建选择版本窗口
        version_window = tk.Toplevel(self.root)
        version_window.title("选择版本")
        version_window.geometry("600x600")
        version_window.resizable(False, False)
        
        # 创建标题
        title_label = ttk.Label(version_window, text="选择版本", style="Subtitle.TLabel")
        title_label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(version_window)
        button_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(button_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建画布
        canvas = tk.Canvas(button_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=canvas.yview)
        
        # 创建内部框架
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)
        
        # 绑定滚动事件
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        inner_frame.bind("<Configure>", configure_scroll_region)
        
        # 创建按钮
        buttons = [
            ("显示所有可安装版本", lambda: self.execute_command(f"{self.cmcl_path} install --show=all", show_output=True)),
            ("显示所有正式版", lambda: self.execute_command(f"{self.cmcl_path} install --show=r", show_output=True)),
            ("显示2020-2021快照版本", lambda: self.execute_command(f"{self.cmcl_path} install --show=s --time=2020-05-09/2021-10-23", show_output=True)),
            ("查看版本信息", self.view_version_info),
            ("删除版本", self.delete_version),
            ("重命名版本", self.rename_version),
            ("补全资源", self.complete_version),
            ("安装Fabric", self.install_fabric),
            ("安装Forge", self.install_forge),
            ("安装LiteLoader", self.install_liteloader),
            ("安装OptiFine", self.install_optifine),
            ("安装Quilt", self.install_quilt),
            ("设置版本隔离", self.set_version_isolate),
            ("取消设置版本隔离", self.unset_version_isolate),
            ("打印启动命令", self.print_start_command),
            ("导出启动脚本", self.export_start_script),
            ("导出PowerShell脚本", self.export_start_script_ps),
            ("关闭", version_window.destroy)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(inner_frame, text=text, command=command, width=35)
            btn.pack(pady=8, fill=tk.X, padx=10)
        
        # 配置画布大小
        canvas.config(width=580, height=500)
    
    def view_version_info(self):
        """查看版本信息"""
        version = simpledialog.askstring("查看版本信息", "请输入版本号：")
        if version:
            self.execute_command(f"{self.cmcl_path} version {version} --info", show_output=True)
    
    def delete_version(self):
        """删除版本"""
        if tk.messagebox.askyesno("删除版本", "确定要删除已选择的版本吗？"):
            self.execute_command(f"{self.cmcl_path} version -d", show_output=True)
    
    def rename_version(self):
        """重命名版本"""
        new_name = simpledialog.askstring("重命名版本", "请输入新名称：")
        if new_name:
            self.execute_command(f"{self.cmcl_path} version --rename={new_name}", show_output=True)
    
    def complete_version(self):
        """补全资源"""
        version = simpledialog.askstring("补全资源", "请输入版本号（留空则补全已选择版本）：")
        option = simpledialog.askstring("补全资源", "请输入补全类型（留空则补全所有，assets/libraries/natives）：")
        if option and option not in ["assets", "libraries", "natives"]:
            tk.messagebox.showerror("错误", "无效的补全类型，请输入assets、libraries或natives")
            return
        
        cmd = f"{self.cmcl_path} version"
        if version:
            cmd += f" {version}"
        if option:
            cmd += f" --complete={option}"
        else:
            cmd += " --complete"
        
        self.execute_command(cmd, show_output=True)
    
    def install_fabric(self):
        """安装Fabric"""
        version = simpledialog.askstring("安装Fabric", "请输入版本号：")
        if not version:
            return
        
        fabric_version = simpledialog.askstring("安装Fabric", "请输入Fabric版本（留空则自动选择）：")
        install_api = tk.messagebox.askyesno("安装Fabric", "是否安装Fabric API？")
        
        cmd = f"{self.cmcl_path} version {version} --fabric"
        if fabric_version:
            cmd += f"={fabric_version}"
        if install_api:
            api_version = simpledialog.askstring("安装Fabric API", "请输入Fabric API版本（留空则自动选择）：")
            if api_version:
                cmd += f" --api={api_version}"
            else:
                cmd += " --api"
        
        self.execute_command(cmd, show_output=True)
    
    def install_forge(self):
        """安装Forge"""
        version = simpledialog.askstring("安装Forge", "请输入版本号：")
        if not version:
            return
        
        forge_version = simpledialog.askstring("安装Forge", "请输入Forge版本（留空则自动选择）：")
        
        cmd = f"{self.cmcl_path} version {version} --forge"
        if forge_version:
            cmd += f"={forge_version}"
        
        self.execute_command(cmd, show_output=True)
    
    def install_liteloader(self):
        """安装LiteLoader"""
        version = simpledialog.askstring("安装LiteLoader", "请输入版本号：")
        if not version:
            return
        
        liteloader_version = simpledialog.askstring("安装LiteLoader", "请输入LiteLoader版本（留空则自动选择）：")
        
        cmd = f"{self.cmcl_path} version {version} --liteloader"
        if liteloader_version:
            cmd += f"={liteloader_version}"
        
        self.execute_command(cmd, show_output=True)
    
    def install_optifine(self):
        """安装OptiFine"""
        version = simpledialog.askstring("安装OptiFine", "请输入版本号：")
        if not version:
            return
        
        optifine_version = simpledialog.askstring("安装OptiFine", "请输入OptiFine版本（留空则自动选择）：")
        
        cmd = f"{self.cmcl_path} version {version} --optifine"
        if optifine_version:
            cmd += f"={optifine_version}"
        
        self.execute_command(cmd, show_output=True)
    
    def install_quilt(self):
        """安装Quilt"""
        version = simpledialog.askstring("安装Quilt", "请输入版本号：")
        if not version:
            return
        
        quilt_version = simpledialog.askstring("安装Quilt", "请输入Quilt版本（留空则自动选择）：")
        
        cmd = f"{self.cmcl_path} version {version} --quilt"
        if quilt_version:
            cmd += f"={quilt_version}"
        
        self.execute_command(cmd, show_output=True)
    
    def set_version_isolate(self):
        """设置版本隔离"""
        self.execute_command(f"{self.cmcl_path} version --isolate", show_output=True)
    
    def unset_version_isolate(self):
        """取消设置版本隔离"""
        self.execute_command(f"{self.cmcl_path} version --unset-isolate", show_output=True)
    
    def print_start_command(self):
        """打印启动命令"""
        self.execute_command(f"{self.cmcl_path} version -p", show_output=True)
    
    def export_start_script(self):
        """导出启动脚本"""
        script_file = simpledialog.askstring("导出启动脚本", "请输入脚本文件名（如：start.bat）：")
        if script_file:
            self.execute_command(f"{self.cmcl_path} version --export-script={script_file}", show_output=True)
    
    def export_start_script_ps(self):
        """导出PowerShell启动脚本"""
        script_file = simpledialog.askstring("导出PowerShell脚本", "请输入脚本文件名（如：start.ps1）：")
        if script_file:
            self.execute_command(f"{self.cmcl_path} version --export-script-ps={script_file}", show_output=True)
    
    def show_help(self):
        """显示帮助"""
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助信息")
        help_window.geometry("600x500")
        
        help_text = scrolledtext.ScrolledText(help_window, font=("Consolas", 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 读取cmcl的帮助信息
        try:
            result = subprocess.run(f"{self.cmcl_path} -h", shell=True, capture_output=True, text=True, encoding='gbk')
            help_text.insert(tk.END, result.stdout)
        except Exception as e:
            help_text.insert(tk.END, f"获取帮助信息失败: {e}")
        
        help_text.config(state=tk.DISABLED)
        
        # 添加关闭按钮
        close_btn = ttk.Button(help_window, text="关闭", command=help_window.destroy)
        close_btn.pack(pady=10)
    
    def install_version(self):
        """安装版本"""
        # 检查是否已经配置了下载源
        config = self.read_config()
        if "downloadSource" not in config:
            # 选择下载源
            source = self.select_download_source()
            if source is None:
                return  # 用户取消选择
            
            # 更新下载源配置
            self.update_download_source(source)
        
        # 获取版本号并安装
        version = simpledialog.askstring("安装版本", "请输入版本号：")
        if version:
            self.execute_command(f"{self.cmcl_path} install {version}", show_output=True)
    
    def exit_launcher(self):
        """退出启动器"""
        if messagebox.askyesno("退出", "确定要退出吗？"):
            self.root.destroy()
    
    def account_operations(self):
        """账号操作"""
        # 创建账号操作窗口
        account_window = tk.Toplevel(self.root)
        account_window.title("账号操作")
        account_window.geometry("600x500")
        
        # 先显示账号列表
        self.execute_command(f"{self.cmcl_path} account --list", show_output=True)
        
        # 创建标题
        title_label = ttk.Label(account_window, text="账号操作", style="Subtitle.TLabel")
        title_label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(account_window)
        button_frame.pack(pady=10)
        
        # 创建按钮
        buttons = [
            ("删除账号", self.delete_account),
            ("选择账号", self.select_account),
            ("登录离线账号", self.login_offline),
            ("登录微软账户", self.login_microsoft),
            ("外置登录", self.login_authlib),
            ("登录mojang账号", self.login_mojang),
            ("关闭", account_window.destroy)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=30)
            btn.pack(pady=8, fill=tk.X)
    
    def delete_account(self):
        """删除账号"""
        account = simpledialog.askstring("删除账号", "请输入账号序号：")
        if account:
            self.execute_command(f"{self.cmcl_path} account --delete={account}", show_output=True)
    
    def select_account(self):
        """选择账号"""
        account = simpledialog.askstring("切换账号", "请输入账号序号：")
        if account:
            self.execute_command(f"{self.cmcl_path} account -s{account}", show_output=True)
    
    def login_offline(self):
        """登录离线账号"""
        account = simpledialog.askstring("登录离线账号", "请输入账号名：")
        if account:
            self.execute_command(f"{self.cmcl_path} account --login=offline --name={account}", show_output=True)
    
    def login_microsoft(self):
        """登录微软账户"""
        messagebox.showinfo("登录微软账户", "即将打开微软登录页面...")
        self.execute_command(f"{self.cmcl_path} account --login=microsoft", show_output=True)
    
    def login_authlib(self):
        """外置登录"""
        address = simpledialog.askstring("外置登录", "请输入服务器地址：")
        if address:
            self.execute_command(f"{self.cmcl_path} account --login=authlib --address={address}", show_output=True)
    
    def login_mojang(self):
        """登录mojang账号"""
        self.execute_command("start https://vdse.bdstatic.com/192d9a98d782d9c74c96f09db9378d93.mp4", show_output=False, wait_for_completion=False)
        # 显示ASCII艺术图形
        ascii_art = [
            " ....................„-~~'''''''~~--„„_",
            "..............„-~''-,::::::::::::::::::: ''-„",
            "..........,~''::::::::',:::::::::::::::: ::::|',",
            ".....::::::,-~'''¯¯¯''''~~--~'''¯''',:",
            ".........'|:::::|: : : : : : : : : : : ::: : |,'",
            "........|:::::|: : :-~~---: : : -----: |",
            ".......(¯''~-': : : :'¯°: ',: :|: :°-: :|",
            ".....'....''~-,|: : : : : : ~---': : : :,'",
            "...............|,: : : : : :-~~--: : ::/",
            "......,-''\\':\\: :'~„„_: : : : : _,-'",
            "__„-';;;;;\\:''-,: : : :'~---~''/|",
            ";;;;;/;;;;;;\\: :\\: : :____/: :',__",
            ";;;;;;;;;;;;;;',. .''-,:|:::::::|. . |;;;;''-„__",
            ";;;;;;,;;;;;;;;;\\. . .''|::::::::|. .,';;;;;;;;;;''-„",
            ";;;;;;;|;;;;;;;;;;;\\. . .\\:::::,'. ./|;;;;;;;;;;;;|",
            ";;;;;;;\\;;;;;;;;;;;',: : :|¯¯|. . .|;;;;;;;;;,';;|",
            ";;;;;;;;;',;;;;;;;;;;;\\. . |:::|. . .'',;;;;;;;;|;;/",
            ";;;;;;;;;;\\;;;;;;;;;;;\\. .|:::|. . . |;;;;;;;;|/",
            ";;;;;;;;;;;;,;;;;;;;;;;|. .\\:/\\. . . .|;;;;;;;;|"
        ]
        for line in ascii_art:
            self.log_message(line)
        
    
    def change_config(self):
        """更改启动器配置"""
        self.execute_command(f"{self.cmcl_path} config -v", show_output=True)
    
    def search_mods(self):
        """模组搜索"""
        self.execute_command("start https://www.mcmod.cn/", show_output=False, wait_for_completion=False)
        self.log_message("已打开模组搜索页面")
    
    def search_modpacks(self):
        """整合包搜索"""
        self.execute_command("start https://www.mcmod.cn/modpack.html", show_output=False, wait_for_completion=False)
        self.log_message("已打开整合包搜索页面")

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLauncher(root)
    root.mainloop()
