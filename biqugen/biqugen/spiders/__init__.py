import os
from biqugen.db import reset_novels_table, reset_chapters_table

# 创建log文件夹
if not os.path.exists("log"):
    os.makedirs("log")
else:
    # 清理log文件
    for file in os.listdir("log"):
        os.remove(f"log/{file}")

# 重置数据库
# reset_novels_table()
# reset_chapters_table()
