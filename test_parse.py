from docker_tool.registry import DockerRegistryClient

# 测试镜像名称解析
def test_parse_image_name():
    # 华为云SWR镜像地址
    image_name = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/milvusdb/milvus:v2.6.9"
    
    # 创建Registry客户端
    client = DockerRegistryClient()
    
    try:
        # 解析镜像名称
        registry, repository, tag = client._parse_image_name(image_name)
        
        print(f"Image name: {image_name}")
        print(f"Parsed registry: {registry}")
        print(f"Parsed repository: {repository}")
        print(f"Parsed tag: {tag}")
        
        # 验证解析结果
        assert registry == "swr.cn-north-4.myhuaweicloud.com", f"Expected registry 'swr.cn-north-4.myhuaweicloud.com', got '{registry}'"
        assert repository == "ddn-k8s/docker.io/milvusdb/milvus", f"Expected repository 'ddn-k8s/docker.io/milvusdb/milvus', got '{repository}'"
        assert tag == "v2.6.9", f"Expected tag 'v2.6.9', got '{tag}'"
        
        print("✓ Image name parsed correctly!")
        return True
    except Exception as e:
        print(f"✗ Error parsing image name: {e}")
        return False

if __name__ == "__main__":
    test_parse_image_name()