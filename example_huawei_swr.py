#!/usr/bin/env python3
"""
使用示例：拉取华为云SWR镜像

这个脚本展示了如何使用修改后的DockerRegistryClient拉取华为云SWR仓库中的镜像。
"""

from docker_tool.registry import DockerRegistryClient
from docker_tool.image_packer import DockerImagePacker

def pull_huawei_swr_image():
    """拉取华为云SWR镜像并打包"""
    # 华为云SWR镜像地址
    image_name = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/milvusdb/milvus:v2.6.9"
    
    # 输出目录
    output_dir = "./images"
    tar_output_dir = "./tar_images"
    
    print(f"=== 拉取华为云SWR镜像: {image_name} ===")
    
    # 1. 创建Registry客户端
    client = DockerRegistryClient()
    
    # 2. 拉取镜像到本地
    print("\n1. 正在拉取镜像...")
    image_dir = os.path.join(output_dir, image_name.replace('/', '_').replace(':', '_'))
    client.pull_image(image_name, image_dir)
    print(f"✓ 镜像拉取完成，保存到: {image_dir}")
    
    # 3. 打包镜像为TAR文件
    print("\n2. 正在打包镜像为TAR文件...")
    packer = DockerImagePacker()
    tar_path = packer.pack_image(image_name, image_dir, tar_output_dir)
    print(f"✓ 镜像打包完成，TAR文件: {tar_path}")
    
    # 4. 显示结果
    print(f"\n=== 拉取完成 ===")
    print(f"镜像名称: {image_name}")
    print(f"本地目录: {image_dir}")
    print(f"TAR文件: {tar_path}")
    print("\n接下来可以使用以下命令将TAR文件传输到Linux服务器:")
    print(f"scp {tar_path} root@your-server-ip:/tmp/")
    print("然后在Linux服务器上执行:")
    print(f"docker load -i /tmp/{os.path.basename(tar_path)}")
    
    return tar_path

if __name__ == "__main__":
    import os
    # 确保输出目录存在
    os.makedirs("./images", exist_ok=True)
    os.makedirs("./tar_images", exist_ok=True)
    
    pull_huawei_swr_image()