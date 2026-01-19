from typing import Optional, Dict
from .ssh_client import SSHClient

class DockerDeployer:
    def __init__(self, ssh_client: SSHClient):
        self.ssh_client = ssh_client
    
    def load_image(self, remote_image_path: str) -> bool:
        """在远程服务器上加载Docker镜像"""
        command = f"docker load -i {remote_image_path}"
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        if exit_status == 0:
            print(f"Successfully loaded image from {remote_image_path}")
            print(stdout)
            return True
        else:
            print(f"Failed to load image: {stderr}")
            return False
    
    def run_container(self, image_name: str, container_name: Optional[str] = None, 
                     ports: Optional[Dict[str, str]] = None, 
                     volumes: Optional[Dict[str, str]] = None, 
                     env: Optional[Dict[str, str]] = None, 
                     detach: bool = True) -> bool:
        """在远程服务器上运行Docker容器"""
        # 构建Docker run命令
        cmd_parts = ["docker", "run"]
        
        # 添加容器名称
        if container_name:
            cmd_parts.extend(["--name", container_name])
        
        # 添加端口映射
        if ports:
            for host_port, container_port in ports.items():
                cmd_parts.extend(["-p", f"{host_port}:{container_port}"])
        
        # 添加卷挂载
        if volumes:
            for host_path, container_path in volumes.items():
                cmd_parts.extend(["-v", f"{host_path}:{container_path}"])
        
        # 添加环境变量
        if env:
            for key, value in env.items():
                cmd_parts.extend(["-e", f"{key}={value}"])
        
        # 添加detach选项
        if detach:
            cmd_parts.append("-d")
        
        # 添加镜像名称
        cmd_parts.append(image_name)
        
        # 执行命令
        command = " ".join(cmd_parts)
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        if exit_status == 0:
            print(f"Successfully started container from {image_name}")
            print(stdout)
            return True
        else:
            print(f"Failed to start container: {stderr}")
            return False
    
    def check_image_exists(self, image_name: str) -> bool:
        """检查镜像是否已存在于远程服务器"""
        command = f"docker images -q {image_name}"
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        return exit_status == 0 and stdout.strip() != ""
    
    def remove_remote_image_file(self, remote_image_path: str) -> bool:
        """删除远程服务器上的镜像文件"""
        command = f"rm -f {remote_image_path}"
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        if exit_status == 0:
            print(f"Successfully removed remote image file: {remote_image_path}")
            return True
        else:
            print(f"Failed to remove remote image file: {stderr}")
            return False
    
    def deploy_image(self, remote_image_path: str, image_name: str, 
                    run_container: bool = False, 
                    container_config: Optional[Dict] = None) -> bool:
        """完整部署流程：加载镜像 -> 可选运行容器 -> 清理临时文件"""
        # 1. 检查镜像是否已存在
        if self.check_image_exists(image_name):
            print(f"Image {image_name} already exists on the server, skipping load.")
        else:
            # 2. 加载镜像
            if not self.load_image(remote_image_path):
                return False
        
        # 3. 可选运行容器
        if run_container:
            container_config = container_config or {}
            if not self.run_container(image_name, **container_config):
                return False
        
        # 4. 清理临时文件
        self.remove_remote_image_file(remote_image_path)
        
        return True
    
    def get_docker_info(self) -> Dict:
        """获取Docker信息"""
        command = "docker info --format '{{json .}}'"
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        if exit_status == 0:
            import json
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                print("Failed to parse docker info output")
        else:
            print(f"Failed to get docker info: {stderr}")
        
        return {}
    
    def list_images(self) -> list:
        """列出远程服务器上的Docker镜像"""
        command = "docker images --format '{{json .}}'"
        exit_status, stdout, stderr = self.ssh_client.execute_command(command)
        
        if exit_status == 0:
            import json
            images = []
            for line in stdout.strip().split("\n"):
                if line.strip():
                    images.append(json.loads(line))
            return images
        else:
            print(f"Failed to list images: {stderr}")
            return []