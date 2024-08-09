import pymysql  # type: ignore
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


class FrameProgress(Progress):
    def get_renderables(self):
        yield Panel(
            self.make_tasks_table(self.tasks),
            expand=True,
            border_style="green",
            style="black",
            safe_box=True,
        )


class ChapterFrameProgress(Progress):
    def get_renderables(self):
        yield Panel(
            self.make_tasks_table(self.tasks),
            expand=True,
            border_style="green",
            style="black",
            safe_box=True,
            title="小说爬取进度(分布式)",
        )
