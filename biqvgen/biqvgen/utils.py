import pymysql
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()

# 连接数据库
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1234TTtt*",
    port=3306,
    database="novels_spider",
    charset="utf8",
)
