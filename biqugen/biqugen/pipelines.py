# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqugen.utils import console, FrameProgress
from biqugen.db import (
    bulk_insert_to_mysql,
    get_novel_id_list_from_db,
    bulk_insert_chapters_to_mysql,
)
from rich.progress import BarColumn, TextColumn

list_progress = FrameProgress(
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
            list_progress.start()
            self.task_id = list_progress.add_task(
                "正在爬取小说详情", start=False, completed=1
            )
        else:
            list_progress.start()
            list_progress.update(self.task_id, advance=1)
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
        list_progress.stop()

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
    chapter_list = []  # 章节列表
    novel_id = None
    task_id = None

    chapter_progress = FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        TextColumn("{task.completed}章"),
    )   


    #  处理item
    def process_item(self, item, spider):
        if self.novel_id is None:
            self.chapter_progress.start()
            self.task_id = self.chapter_progress.add_task(
                f"爬取小说《{item["novel_name"]}》", start=False, completed=1
            )
            self.novel_id = item["novel_id"]
        elif self.novel_id != item["novel_id"]:
            self.chapter_progress.stop()
            # 保存到数据库
            bulk_insert_chapters_to_mysql(self.chapter_list, self.novel_id)
            console.log(f"开始存储小说{self.novel_id}章节数据:{len(self.chapter_list)}")
            self.novel_id = item["novel_id"]
            self.chapter_list.clear()
            self.chapter_progress.start()
            self.task_id = self.chapter_progress.add_task(
                f"爬取小说《{item["novel_name"]}》", start=False, completed=1
            )
        else:
            self.chapter_progress.update(self.task_id, advance=1)
        item["chapter_content"] = item["chapter_content"].replace("\xa0", "")
        self.chapter_list.append(item)

    # 开启爬虫
    def open_spider(self, spider):
        console.log("开始爬取")
        pass

    # 关闭爬虫
    def close_spider(self, spider):
        self.chapter_progress.stop()
        console.log(f"爬取结束,开始存储剩余数据{len(self.chapter_list)}")
        bulk_insert_chapters_to_mysql(self.chapter_list, self.novel_id)
        console.log("存储结束")
        pass
