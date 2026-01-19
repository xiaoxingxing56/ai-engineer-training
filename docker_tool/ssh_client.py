import paramiko
import os
from typing import Optional, Tuple
from tqdm import tqdm

class SSHClient:
    def __init__(self, hostname: str, port: int = 22, username: str = "root"):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp = None
    
    def connect(self, password: Optional[str] = None, key_filename: Optional[str] = None) -> bool:
        """建立SSH连接"""
        try:
            self.client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=password,
                key_filename=key_filename
            )
            self.sftp = self.client.open_sftp()
            return True
        except Exception as e:
            print(f"Failed to connect to {self.hostname}: {e}")
            return False
    
    def disconnect(self):
        """关闭SSH连接"""
        if self.sftp:
            self.sftp.close()
        self.client.close()
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """使用SCP上传文件到远程服务器"""
        try:
            # 获取文件大小用于进度条
            file_size = os.path.getsize(local_path)
            
            # 创建进度条
            progress = tqdm(total=file_size, unit="B", unit_scale=True, desc=f"Uploading to {self.hostname}")
            
            # 回调函数更新进度
            def callback(transferred, total):
                progress.update(transferred - progress.n)
            
            # 上传文件
            self.sftp.put(local_path, remote_path, callback=callback)
            
            progress.close()
            return True
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return False
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """在远程服务器上执行命令"""
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            stdout_output = stdout.read().decode("utf-8")
            stderr_output = stderr.read().decode("utf-8")
            return exit_status, stdout_output, stderr_output
        except Exception as e:
            print(f"Failed to execute command: {e}")
            return -1, "", str(e)
    
    def ensure_directory(self, remote_dir: str) -> bool:
        """确保远程目录存在"""
        try:
            self.sftp.stat(remote_dir)
            return True
        except FileNotFoundError:
            # 目录不存在，创建它
            command = f"mkdir -p {remote_dir}"
            exit_status, _, _ = self.execute_command(command)
            return exit_status == 0
        except Exception as e:
            print(f"Failed to check/create directory: {e}")
            return False
    
    def upload_image(self, local_image_path: str, remote_dir: str = "/tmp") -> Optional[str]:
        """上传镜像文件到远程服务器，并返回远程路径"""
        # 确保远程目录存在
        if not self.ensure_directory(remote_dir):
            return None
        
        # 获取本地文件名
        local_filename = os.path.basename(local_image_path)
        
        # 构建远程路径
        remote_path = os.path.join(remote_dir, local_filename)
        
        # 上传文件
        if self.upload_file(local_image_path, remote_path):
            return remote_path
        return None