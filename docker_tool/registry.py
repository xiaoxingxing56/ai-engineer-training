import requests
import json
import os
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

class DockerRegistryClient:
    def __init__(self, registry_url: str = "registry-1.docker.io"):
        self.registry_url = registry_url
        self.base_url = f"https://{registry_url}/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.docker.distribution.manifest.v2+json,application/vnd.docker.distribution.manifest.list.v2+json"
        })
        
    def _get_auth_token(self, registry: str, repository: str, scope: str = "pull") -> Optional[str]:
        """获取认证Token"""
        # 首先尝试直接访问registry获取认证信息
        test_url = f"https://{registry}/v2/{repository}/manifests/latest"
        response = self.session.get(test_url, allow_redirects=False)
        
        # 处理401响应，获取认证地址
        if response.status_code == 401:
            auth_header = response.headers.get("WWW-Authenticate", "")
            if "Bearer" in auth_header:
                # 解析认证地址和service
                import re
                realm_match = re.search(r"realm=\"([^\"]+)\"", auth_header)
                service_match = re.search(r"service=\"([^\"]+)\"", auth_header)
                
                if realm_match:
                    auth_url = realm_match.group(1)
                    service = service_match.group(1) if service_match else registry
                    
                    # 请求认证token
                    params = {
                        "service": service,
                        "scope": f"repository:{repository}:{scope}"
                    }
                    
                    auth_response = self.session.get(auth_url, params=params)
                    if auth_response.status_code == 200:
                        return auth_response.json().get("token")
        return None
    
    def _parse_image_name(self, image_name: str) -> Tuple[str, str, str]:
        """解析镜像名称，返回 (registry, repository, tag)"""
        parts = image_name.split("/")
        
        # 处理默认registry情况
        if len(parts) == 1 or "." not in parts[0] and ":" not in parts[0]:
            registry = "registry-1.docker.io"
            repo_tag = image_name
        else:
            registry = parts[0]
            repo_tag = "/".join(parts[1:])
        
        # 处理标签情况
        if ":" in repo_tag:
            repository, tag = repo_tag.split(":", 1)
        else:
            repository, tag = repo_tag, "latest"
        
        # 处理官方镜像（library/）
        if len(repository.split("/")) == 1 and registry == "registry-1.docker.io":
            repository = f"library/{repository}"
        
        return registry, repository, tag
    
    def get_manifest(self, image_name: str) -> Dict:
        """获取镜像的Manifest"""
        registry, repository, tag = self._parse_image_name(image_name)
        
        # 获取认证Token
        token = self._get_auth_token(registry, repository)
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # 获取Manifest
        manifest_url = f"https://{registry}/v2/{repository}/manifests/{tag}"
        response = self.session.get(manifest_url)
        response.raise_for_status()
        
        return response.json()
    
    def pull_layer(self, image_name: str, digest: str, output_path: str) -> str:
        """拉取单个镜像层"""
        registry, repository, _ = self._parse_image_name(image_name)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 获取层数据
        layer_url = f"https://{registry}/v2/{repository}/blobs/{digest}"
        response = self.session.get(layer_url, stream=True)
        response.raise_for_status()
        
        # 计算文件大小
        total_size = int(response.headers.get("content-length", 0))
        
        # 写入文件
        with open(output_path, "wb") as f:
            with tqdm(total=total_size, unit="B", unit_scale=True, desc=f"Pulling layer {digest[:12]}") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        return output_path
    
    def pull_image(self, image_name: str, output_dir: str) -> str:
        """拉取完整镜像"""
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取Manifest
        manifest = self.get_manifest(image_name)
        
        # 保存Manifest
        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        
        # 拉取所有层
        layers_dir = os.path.join(output_dir, "layers")
        os.makedirs(layers_dir, exist_ok=True)
        
        layer_files = []
        for layer in manifest.get("layers", []):
            digest = layer["digest"]
            layer_filename = digest.split(":")[1] + ".tar.gz"
            layer_path = os.path.join(layers_dir, layer_filename)
            
            if not os.path.exists(layer_path):
                self.pull_layer(image_name, digest, layer_path)
            
            layer_files.append(layer_path)
        
        # 保存配置
        config_digest = manifest["config"]["digest"]
        config_path = os.path.join(output_dir, "config.json")
        
        if not os.path.exists(config_path):
            self.pull_layer(image_name, config_digest, config_path)
        
        return output_dir
    
    def get_image_config(self, image_name: str) -> Dict:
        """获取镜像配置"""
        manifest = self.get_manifest(image_name)
        config_digest = manifest["config"]["digest"]
        
        registry, repository, _ = self._parse_image_name(image_name)
        config_url = f"https://{registry}/v2/{repository}/blobs/{config_digest}"
        
        response = self.session.get(config_url)
        response.raise_for_status()
        
        return response.json()