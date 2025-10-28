# !/bin/bash
# 下载 python 包 *.whl 文件
# 前往 https://pypi.org/ 搜索需要的包，点击下载 *.whl 文件

# 移动到当前目录下


mv /tmp/*.whl  ./
# 下载完成后，将文件上传到服务器

# 执行以下命令安装
pip install *.whl

