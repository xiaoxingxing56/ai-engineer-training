import tarfile
import json
import os
import shutil
from typing import Dict, List
from tqdm import tqdm

class DockerImagePacker:
    def __init__(self):
        pass
    
    def create_docker_tar(self, image_dir: str, output_tar_path: str) -> str:
        """将拉取的镜像文件打包为标准Docker TAR文件"""
        # 检查必要文件是否存在
        manifest_path = os.path.join(image_dir, "manifest.json")
        config_path = os.path.join(image_dir, "config.json")
        layers_dir = os.path.join(image_dir, "layers")
        
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        if not os.path.exists(layers_dir):
            raise FileNotFoundError(f"Layers directory not found: {layers_dir}")
        
        # 读取原始manifest
        with open(manifest_path, "r") as f:
            original_manifest = json.load(f)
        
        # 读取配置文件
        with open(config_path, "r") as f:
            config_data = json.load(f)
        
        # 获取配置文件的哈希值
        config_digest = original_manifest["config"]["digest"]
        config_hash = config_digest.split(":")[1]
        
        # 准备Docker TAR结构
        with tarfile.open(output_tar_path, "w:gz") as tar:
            # 1. 写入配置文件
            config_name = f"{config_hash}.json"
            tar.add(config_path, arcname=config_name)
            
            # 2. 写入所有层文件
            layer_hashes = []
            for layer in original_manifest.get("layers", []):
                layer_digest = layer["digest"]
                layer_hash = layer_digest.split(":")[1]
                layer_hashes.append(layer_hash)
                
                layer_filename = f"{layer_hash}.tar.gz"
                layer_path = os.path.join(layers_dir, layer_digest.split(":")[1] + ".tar.gz")
                
                if os.path.exists(layer_path):
                    tar.add(layer_path, arcname=layer_filename)
                else:
                    raise FileNotFoundError(f"Layer file not found: {layer_path}")
            
            # 3. 创建并写入manifest.json
            docker_manifest = [{
                "Config": config_name,
                "RepoTags": [],  # 后续可以从image name中解析添加
                "Layers": [f"{h}.tar.gz" for h in layer_hashes]
            }]
            
            # 写入manifest.json
            manifest_content = json.dumps(docker_manifest, indent=2).encode("utf-8")
            manifest_info = tarfile.TarInfo(name="manifest.json")
            manifest_info.size = len(manifest_content)
            tar.addfile(manifest_info, fileobj=BytesIO(manifest_content))
        
        return output_tar_path
    
    def pack_image(self, image_name: str, image_dir: str, output_dir: str) -> str:
        """打包镜像并添加RepoTags信息"""
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成输出文件名
        output_filename = f"{image_name.replace('/', '_').replace(':', '_')}.tar.gz"
        output_tar_path = os.path.join(output_dir, output_filename)
        
        # 先创建基本TAR
        self.create_docker_tar(image_dir, output_tar_path)
        
        # 临时目录用于修改manifest
        temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # 解压TAR到临时目录
            with tarfile.open(output_tar_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # 修改manifest.json，添加RepoTags
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            # 添加RepoTags
            if isinstance(manifest, list) and manifest:
                manifest[0]["RepoTags"] = [image_name]
            
            # 写回manifest.json
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
            
            # 重新打包TAR
            os.remove(output_tar_path)
            with tarfile.open(output_tar_path, "w:gz") as tar:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        tar.add(file_path, arcname=arcname)
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir)
        
        return output_tar_path
    
    def unpack_image(self, tar_path: str, output_dir: str) -> str:
        """解压Docker TAR文件到指定目录"""
        os.makedirs(output_dir, exist_ok=True)
        
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(output_dir)
        
        return output_dir

# 为了解决bytesIO的问题，需要导入
from io import BytesIO