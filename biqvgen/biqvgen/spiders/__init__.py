# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import os
from biqvgen.db import reset_novels_table

# 创建log文件夹
if not os.path.exists("log"):
    os.makedirs("log")

# 重置数据库
# reset_novels_table()
