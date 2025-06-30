# config.py 
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 【第一步：临时注释掉这一行】
    # SECRET_KEY = os.environ.get('SECRET_KEY')

    # 【第二步：新增这一行进行测试，我们使用一个纯粹的、无歧义的字符串】
    SECRET_KEY = 'a-super-secret-key-that-must-work-123'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
