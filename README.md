# Docker镜像拉取与部署工具

用于在没有Docker环境的Windows上拉取Docker镜像，并传输到Linux服务器进行部署。

## 功能特性

- ✅ 在没有Docker环境的Windows上拉取Docker镜像
- ✅ 支持Docker Hub和私有Registry
- ✅ 将镜像打包为标准Docker TAR格式
- ✅ 通过SSH传输镜像到Linux服务器
- ✅ 自动在Linux服务器上加载和部署镜像
- ✅ 支持通过密码或SSH密钥认证
- ✅ 提供命令行界面，操作简单

## 安装方法

### 1. 安装Python

确保你的Windows系统已安装Python 3.6或更高版本。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行工具

直接运行main.py文件：

```bash
python main.py --help
```

或者通过setup.py安装：

```bash
pip install .
docker-tool --help
```

## 使用方法

### 1. 拉取镜像到本地

```bash
python main.py pull nginx:latest
```

### 2. 将镜像打包为TAR文件

```bash
python main.py pack ./images/nginx_latest nginx:latest
```

### 3. 拉取并部署到Linux服务器

```bash
python main.py deploy nginx:latest 192.168.1.100 --username root --password your_password
```

### 4. 上传本地TAR文件到服务器并部署

```bash
python main.py upload ./tar_images/nginx_latest.tar.gz 192.168.1.100 nginx:latest --username root --key-file ~/.ssh/id_rsa
```

## 命令说明

### pull

拉取Docker镜像到本地：

```
Usage: main.py pull [OPTIONS] IMAGE_NAME

  拉取Docker镜像到本地

Options:
  -o, --output-dir TEXT  输出目录
  --help                 Show this message and exit.
```

### pack

将拉取的镜像打包为TAR文件：

```
Usage: main.py pack [OPTIONS] IMAGE_DIR IMAGE_NAME

  将拉取的镜像打包为TAR文件

Options:
  -o, --output-dir TEXT  输出目录
  --help                 Show this message and exit.
```

### deploy

拉取镜像，传输到Linux服务器并部署：

```
Usage: main.py deploy [OPTIONS] IMAGE_NAME HOSTNAME

  拉取镜像，传输到Linux服务器并部署

Options:
  -p, --port INTEGER       SSH端口
  -u, --username TEXT      SSH用户名
  -P, --password TEXT      SSH密码
  -k, --key-file TEXT      SSH私钥文件路径
  --remote-dir TEXT        远程服务器临时目录
  --run                    是否运行容器
  --help                   Show this message and exit.
```

### upload

上传本地TAR镜像到Linux服务器并部署：

```
Usage: main.py upload [OPTIONS] TAR_PATH HOSTNAME IMAGE_NAME

  上传本地TAR镜像到Linux服务器并部署

Options:
  -p, --port INTEGER       SSH端口
  -u, --username TEXT      SSH用户名
  -P, --password TEXT      SSH密码
  -k, --key-file TEXT      SSH私钥文件路径
  --remote-dir TEXT        远程服务器临时目录
  --run                    是否运行容器
  --help                   Show this message and exit.
```

## 示例

### 拉取并部署Nginx镜像到Linux服务器

```bash
python main.py deploy nginx:latest 192.168.1.100 --username root --password 123456 --run
```

### 使用SSH密钥拉取并部署Redis镜像

```bash
python main.py deploy redis:latest 192.168.1.200 --username ubuntu --key-file C:\Users\yourname\.ssh\id_rsa
```

## 注意事项

1. 确保你的Windows系统可以访问Docker Hub或私有Registry
2. 确保Linux服务器已安装Docker
3. 确保Linux服务器的SSH服务正在运行
4. 使用SSH密钥认证时，确保私钥文件有正确的权限
5. 拉取大型镜像可能需要较长时间，请耐心等待

## 项目结构

```
docker-tool/
├── docker_tool/
│   ├── __init__.py          # 包初始化文件
│   ├── registry.py          # Docker Registry API客户端
│   ├── image_packer.py      # 镜像打包功能
│   ├── ssh_client.py        # SSH客户端，用于文件传输和命令执行
│   └── deployer.py          # Docker部署器
├── main.py                  # 主程序入口
├── requirements.txt         # 依赖列表
├── setup.py                 # 安装配置
└── README.md                # 项目说明
```

## 技术原理

1. **镜像拉取**：通过Docker Registry API直接拉取镜像的Manifest和各层文件
2. **镜像打包**：将拉取的文件重新组织为标准Docker TAR格式
3. **文件传输**：使用SSH/SCP协议将镜像文件传输到Linux服务器
4. **镜像部署**：通过SSH在Linux服务器上执行`docker load`和`docker run`命令

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
