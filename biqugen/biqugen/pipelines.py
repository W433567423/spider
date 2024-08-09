# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqugen.utils import console, FrameProgress,ChapterFrameProgress
from biqugen.db import (
    bulk_insert_to_mysql,
    get_novel_id_list_from_db,
    bulk_insert_chapters_to_mysql,
)
from rich.progress import BarColumn, TextColumn, MofNCompleteColumn, TimeRemainingColumn




class GetListPipeline:
    novel_list = []  # 小说列表
    abnormal_list = []  # 异常id
    remote_list = []

    task_id = None
    list_progress = FrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        TextColumn("{task.completed}本"),
    )
    #  处理item
    def process_item(self, item, spider):
        if self.task_id is None:
            self.list_progress.start()
            self.task_id = self.list_progress.add_task(
                "正在爬取小说详情", start=False, completed=1
            )
        else:
            self.list_progress.start()
            self.list_progress.update(self.task_id, advance=1)
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
        self.list_progress.stop()

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
    chapter_tasks=[]

    chapter_progress = ChapterFrameProgress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TextColumn('{task.completed}/{task.total}章'),
        "[cyan]⏳",
        TimeRemainingColumn()
        )


    #  处理item
    def process_item(self, item, spider):
        # 从task列表中寻找是否有该任务
        index=-1
        for i,task in enumerate(self.chapter_tasks):
            if task["novel_id"]==item["novel_id"]:
                index=i
                break
        if index==-1:
            self.chapter_progress.start()
            task_id= self.chapter_progress.add_task(
                f"爬取小说《{item["novel_name"]}》", completed=1
            )
            task={"novel_id":item["novel_id"],"task_id":task_id,"chapter_list":[item],"total_chapter":item["total_chapter"]}
            self.chapter_tasks.append(task)
        else:
            if self.chapter_tasks[index]["total_chapter"]!=item["total_chapter"]:
                self.chapter_tasks[index]["total_chapter"]=item["total_chapter"]
            # 取出task_id
            task_id=self.chapter_tasks[index]["task_id"]
            self.chapter_progress.update(task_id, advance=1,total=item["total_chapter"])
            self.chapter_tasks[index]["chapter_list"].append(item)
            if( len(self.chapter_tasks[index]["chapter_list"])==self.chapter_tasks[index]["total_chapter"]):
                self.chapter_progress.stop_task(task_id)
                # 保存到数据库
                self.chapter_progress.update(task_id,completed=self.chapter_tasks[index]["total_chapter"])
                bulk_insert_chapters_to_mysql(self.chapter_tasks[index]["chapter_list"])
                self.chapter_tasks.pop(index)


    # 开启爬虫
    def open_spider(self, spider):
        console.log("开始爬取")
        pass

    # 关闭爬虫
    def close_spider(self, spider):
        self.chapter_progress.stop()
        # 保存到数据库
        for task in self.chapter_tasks:
            bulk_insert_chapters_to_mysql(task["chapter_list"])
        console.log("存储结束")
        pass
