# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqvgen.utils import console, FrameProgress
from rich.progress import BarColumn, TextColumn
from biqvgen.db import (
    bulk_insert_to_mysql,
    get_novel_id_list_from_db,
    reset_novels_table,
)

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
        # novel["info"]='（新书《狂妻拽上天：帝少，高调宠！》已发）“这辈子，你只能是我的！”第一帝少墨昕宸一句话，锁定了尹恩希一生。用尹恩希的话总结她的狼性老公，那就是腹黑！霸道！占有欲极强！“不许看别的男人！不许撩女人！不许被人欺负！”听着墨昕宸霸道独裁的话，尹恩希翻了个白眼，她功夫一流，谁找死地来欺负她？\xa0\xa0\xa0\xa0'
        #   '直到后来尹恩希被“欺负”得四肢酸软，才忍不住爆粗，说好的高冷禁欲呢？欺负她最多的就是他好不好？！\xa0\xa0\xa0\xa0'
        #   '［本文1v1，巨甜酥爽宠文！］'

        # 将novel["info"]合法化，取出乱七八糟的字符
        novel["intro"] = "".join(
            [
                i
                for i in novel["intro"]
                if i.isalnum() or i in ["。", "！", "，", "？", "："]
            ]
        )

        self.novel_list.append(novel)
        if len(self.novel_list) == 1000:
            # 保存到数据库
            bulk_insert_to_mysql(
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

    # 关闭爬虫
    def close_spider(self, spider):
        with progress:
            progress.stop()
        console.log(f"正在保存数据{len(self.novel_list)}")
        # 保存到数据库
        bulk_insert_to_mysql(
            self.remote_list,
            self.novel_list,
            self.abnormal_ids,
        )
        console.log("爬取结束")

    # console.log("🚀 ~ self.novel_list, spider:", len(self.novel_list))
    # console.log(self.novel_list[:1])
