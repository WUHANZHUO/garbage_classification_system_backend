# 垃圾分类系统-后端

第一次运行本系统前，需要做如下修改：

1. my_app/recognition路径下新建uploads文件夹。

2. my_app/recognition路径下新建model文件夹，并将模型文件（garbage_classifier_resnet18.pth）放入其中。

3. 安装requirements.txt中所需依赖。

4. 配置.env文件

	```
	# .env file
	# 数据库连接配置
	# 格式: mysql+pymysql://<用户名>:<密码>@<主机地址>:<端口>/<数据库名>
	DATABASE_URI="mysql+pymysql://x:xxxx@127.0.0.1:3306/garbage_classification_system"
	
	# Flask 和 JWT 使用的密钥，请务必修改为一个复杂的随机字符串
	SECRET_KEY="wuwuwu555password"
	```

	
