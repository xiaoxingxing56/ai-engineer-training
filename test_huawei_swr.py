from docker_tool.registry import DockerRegistryClient

# 测试华为云SWR镜像拉取
def test_pull_huawei_swr_image():
    print("Testing Huawei SWR image pull...")
    
    # 华为云SWR镜像地址
    image_name = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/milvusdb/milvus:v2.6.9"
    
    # 创建Registry客户端
    client = DockerRegistryClient()
    
    try:
        # 尝试获取镜像manifest
        print(f"Getting manifest for {image_name}...")
        manifest = client.get_manifest(image_name)
        print(f"Successfully got manifest! Manifest type: {manifest.get('mediaType')}")
        print(f"Image has {len(manifest.get('layers', []))} layers")
        
        # 打印manifest内容（前500字符）
        import json
        manifest_str = json.dumps(manifest, indent=2)
        print(f"Manifest preview: {manifest_str[:500]}...")
        
        return True
    except Exception as e:
        print(f"Error pulling image: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pull_huawei_swr_image()