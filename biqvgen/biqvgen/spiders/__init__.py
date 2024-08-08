# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import os
from biqvgen.db import reset_novels_table
from biqvgen.utils import console

# 创建log文件夹
if not os.path.exists("log"):
    os.makedirs("log")
else:
    # 清理log文件
    for file in os.listdir("log"):
        os.remove(f"log/{file}")

# 重置数据库
# reset_novels_table()
