import click
import os
import tempfile
from docker_tool.registry import DockerRegistryClient
from docker_tool.image_packer import DockerImagePacker
from docker_tool.ssh_client import SSHClient
from docker_tool.deployer import DockerDeployer

@click.group()
def cli():
    """Docker镜像拉取与部署工具
    
    用于在没有Docker环境的Windows上拉取Docker镜像，并传输到Linux服务器进行部署。
    """
    pass

@cli.command()
@click.argument('image_name')
@click.option('--output-dir', '-o', default='./images', help='输出目录')
def pull(image_name, output_dir):
    """拉取Docker镜像到本地"""
    print(f"Pulling image: {image_name}")
    
    # 创建Registry客户端
    client = DockerRegistryClient()
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 拉取镜像
    image_dir = os.path.join(output_dir, image_name.replace('/', '_').replace(':', '_'))
    client.pull_image(image_name, image_dir)
    
    print(f"Successfully pulled image to {image_dir}")

@cli.command()
@click.argument('image_dir')
@click.argument('image_name')
@click.option('--output-dir', '-o', default='./tar_images', help='输出目录')
def pack(image_dir, image_name, output_dir):
    """将拉取的镜像打包为TAR文件"""
    print(f"Packing image: {image_name}")
    
    # 创建打包器
    packer = DockerImagePacker()
    
    # 打包镜像
    tar_path = packer.pack_image(image_name, image_dir, output_dir)
    
    print(f"Successfully packed image to {tar_path}")

@cli.command()
@click.argument('image_name')
@click.argument('hostname')
@click.option('--port', '-p', default=22, help='SSH端口')
@click.option('--username', '-u', default='root', help='SSH用户名')
@click.option('--password', '-P', help='SSH密码')
@click.option('--key-file', '-k', help='SSH私钥文件路径')
@click.option('--remote-dir', default='/tmp', help='远程服务器临时目录')
@click.option('--run', is_flag=True, help='是否运行容器')
def deploy(image_name, hostname, port, username, password, key_file, remote_dir, run):
    """拉取镜像，传输到Linux服务器并部署"""
    print(f"Deploying image: {image_name} to {hostname}")
    
    # 1. 拉取镜像到临时目录
    print("Step 1: Pulling image...")
    with tempfile.TemporaryDirectory() as temp_dir:
        client = DockerRegistryClient()
        image_dir = os.path.join(temp_dir, image_name.replace('/', '_').replace(':', '_'))
        client.pull_image(image_name, image_dir)
        
        # 2. 打包镜像为TAR
        print("Step 2: Packing image...")
        packer = DockerImagePacker()
        tar_path = packer.pack_image(image_name, image_dir, temp_dir)
        
        # 3. 传输到远程服务器
        print("Step 3: Transferring image to remote server...")
        ssh_client = SSHClient(hostname, port, username)
        if not ssh_client.connect(password, key_file):
            print("Failed to connect to remote server")
            return
        
        remote_image_path = ssh_client.upload_image(tar_path, remote_dir)
        if not remote_image_path:
            ssh_client.disconnect()
            return
        
        # 4. 部署镜像
        print("Step 4: Deploying image on remote server...")
        deployer = DockerDeployer(ssh_client)
        deployer.deploy_image(remote_image_path, image_name, run)
        
        # 5. 断开连接
        ssh_client.disconnect()
    
    print(f"Successfully deployed image: {image_name} to {hostname}")

@cli.command()
@click.argument('tar_path')
@click.argument('hostname')
@click.argument('image_name')
@click.option('--port', '-p', default=22, help='SSH端口')
@click.option('--username', '-u', default='root', help='SSH用户名')
@click.option('--password', '-P', help='SSH密码')
@click.option('--key-file', '-k', help='SSH私钥文件路径')
@click.option('--remote-dir', default='/tmp', help='远程服务器临时目录')
@click.option('--run', is_flag=True, help='是否运行容器')
def upload(tar_path, hostname, image_name, port, username, password, key_file, remote_dir, run):
    """上传本地TAR镜像到Linux服务器并部署"""
    print(f"Uploading image: {tar_path} to {hostname}")
    
    # 1. 检查本地文件是否存在
    if not os.path.exists(tar_path):
        print(f"File not found: {tar_path}")
        return
    
    # 2. 传输到远程服务器
    ssh_client = SSHClient(hostname, port, username)
    if not ssh_client.connect(password, key_file):
        print("Failed to connect to remote server")
        return
    
    remote_image_path = ssh_client.upload_image(tar_path, remote_dir)
    if not remote_image_path:
        ssh_client.disconnect()
        return
    
    # 3. 部署镜像
    deployer = DockerDeployer(ssh_client)
    deployer.deploy_image(remote_image_path, image_name, run)
    
    # 4. 断开连接
    ssh_client.disconnect()
    
    print(f"Successfully uploaded and deployed image: {tar_path} to {hostname}")

if __name__ == '__main__':
    cli()