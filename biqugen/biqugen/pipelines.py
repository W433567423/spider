# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqugen.utils import console, FrameProgress
from biqugen.db import (
    bulk_insert_to_mysql,
    get_novel_id_list_from_db,
    reset_novels_table,
)
from rich.progress import BarColumn, TextColumn
import logging

progress = FrameProgress(
    "[progress.description]{task.description}",
    BarColumn(),
    TextColumn("{task.completed}本"),
)


class GetListPipeline:
    novel_list = []  # 小说列表
    abnormal_list = []  # 异常id
    remote_list = []

    task_id = None

    #  处理item
    def process_item(self, item, spider):
        if self.task_id is None:
            progress.start()
            self.task_id = progress.add_task(
                "正在爬取小说详情", start=False, completed=1
            )
        else:
            progress.start()
            progress.update(self.task_id, advance=1)
        # 清洗数据
        item["intro"] = item["intro"].replace("\xa0", "")
        if item.get("abnormal"):
            self.abnormal_list.append(item)
            return
        self.novel_list.append(item)
        if len(self.novel_list) == 1000:
            # 保存到数据库
            bulk_insert_to_mysql(
                self.remote_list,
                self.novel_list,
                self.abnormal_list,
            )
            self.novel_list.clear()
            self.abnormal_list.clear()

    # 开启爬虫
    def open_spider(self, spider):
        console.log("开始爬取")
        self.remote_list = get_novel_id_list_from_db()

    # 关闭爬虫
    def close_spider(self, spider):
        progress.stop()

        # 保存到数据库
        bulk_insert_to_mysql(
            self.remote_list,
            self.novel_list,
            self.abnormal_list,
        )
        self.novel_list.clear()
        self.abnormal_list.clear()

        console.log("爬取结束")


class GetChapterPipeline:
    #  处理item
    def process_item(self, item, spider):
        console.log("🚀 ~ item:", item)
        pass

    # 开启爬虫
    def open_spider(self, spider):
        pass

    # 关闭爬虫
    def close_spider(self, spider):
        pass
