# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqvgen.utils import console, FrameProgress
from rich.progress import BarColumn, TextColumn
from biqvgen.db import bulk_insert_to_mysql, get_novel_id_list_from_db
import os

progress = FrameProgress(
    "[progress.description]{task.description}",
    BarColumn(),
    TextColumn("{task.completed}本"),
    # transient=True,
)


class BiqvgenPipeline:
    novel_list = []  # 小说列表
    abnormal_ids = []  # 异常id
    remote_list = []

    task_id = None

    #  处理item
    def process_item(self, item, spider):
        if self.task_id is None:
            progress.start()
            self.task_id = progress.add_task("正在爬取小说详情", start=False)
        else:
            progress.start()
            progress.update(self.task_id, advance=1)
        if item.get("abnormal"):
            self.abnormal_ids.append(item["novel_id"])
            return
        novel = {
            "novel_id": item["novel_id"],
            "novel_name": item["novel_name"],
            "novel_cover": item["novel_cover"],
            "novel_author": item["novel_author"],
            "novel_category": item["novel_category"],
            "write_status": item["write_status"],
            "updated_time": item["updated_time"],
            "intro": item["intro"],
        }
        novel["intro"] = item["intro"].replace("\xa0", "").replace("\u3000", "")
        self.novel_list.append(novel)
        if len(self.novel_list) == 1000:
            # 保存到数据库
            bulk_insert_to_mysql(
                self.logger.error,
                self.remote_list,
                self.novel_list,
                self.abnormal_ids,
            )
            del self.novel_list[:]
            del self.novel_list[:]

    # 开启爬虫
    def open_spider(self, spider):
        console.log("开始爬取")
        self.remote_list = get_novel_id_list_from_db()
        # 创建log文件夹
        if not os.path.exists("log"):
            os.makedirs("log")

    # 关闭爬虫
    def close_spider(self, spider):
        with progress:
            progress.stop()
        console.log("爬取结束,开始保存到数据库")

        # 保存到数据库
        bulk_insert_to_mysql(
            self.logger.error,
            self.remote_list,
            self.novel_list,
            self.abnormal_ids,
        )
        # console.log("🚀 ~ self.novel_list, spider:", len(self.novel_list))
        # console.log(self.novel_list[:1])
