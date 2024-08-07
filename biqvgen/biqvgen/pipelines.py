# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqvgen.utils import conn, console, FrameProgress
from rich.progress import BarColumn, TextColumn
import os

progress = FrameProgress(
    "[progress.description]{task.description}",
    BarColumn(),
    TextColumn("{task.completed}本"),
    # transient=True,
)


class BiqvgenPipeline:
    novel_list = []  # 小说列表
    task_id = None

    #  处理item
    def process_item(self, item, spider):

        if item.get("abnormal"):
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
        # with progress:
        progress.start()
        progress.update(self.task_id, advance=1)
        # if len(self.novel_list) == 1000:
        #     self.bulk_insert_to_mysql(self.novel_list, spider)
        #     del self.novel_list[:]

    # 开启爬虫
    def open_spider(self, spider):
        console.log("开始爬取")
        # # 创建数据库
        # global conn
        # conn.ping(reconnect=True)
        # cursor = conn.cursor()  # 创建游标
        # # 创建数据表
        # cursor.execute("DROP TABLE IF EXISTS novels;")
        # cursor.execute(
        #     """
        #         CREATE TABLE IF NOT EXISTS novels(
        #         novel_id INT PRIMARY KEY COMMENT '笔趣阁小说id',
        #         novel_name VARCHAR(255) COMMENT '小说名' not null,
        #         novel_cover VARCHAR(255) COMMENT '小说封面',
        #         novel_author VARCHAR(255) COMMENT '小说作者',
        #         novel_category VARCHAR(255) COMMENT '小说分类',
        #         write_status VARCHAR(255) COMMENT '小说连载状态',
        #         updated_time VARCHAR(255) COMMENT '小说发布时间',
        #         intro TEXT COMMENT '小说简介',
        #         is_extra BOOLEAN DEFAULT FALSE COMMENT '是否已添加额外信息(连载情况、人气、评分等)',
        #         is_chapter BOOLEAN DEFAULT FALSE COMMENT '是否已添加章节信息',
        #         abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
        #         file_path VARCHAR(255) COMMENT '小说文件路径'
        #         );
        #     """
        # )
        # conn.commit()
        # cursor.close()
        # 创建log文件夹
        if not os.path.exists("log"):
            os.makedirs("log")
        with progress:
            self.task_id = progress.add_task("正在爬取小说详情", start=False)

    # 关闭爬虫
    def close_spider(self, spider):
        with progress:
            progress.stop()
        console.log("爬取结束,开始保存到数据库")

        remote_list = get_novel_id_list_from_db()
        # 保存到数据库
        self.bulk_insert_to_mysql(self.novel_list, remote_list)
        # console.log("🚀 ~ self.novel_list, spider:", len(self.novel_list))
        # console.log(self.novel_list[:1])

    # 批量插入到数据库
    def bulk_insert_to_mysql(self, data, remote_list):
        new_list = []
        for item in data:
            if item["novel_id"] not in remote_list:
                new_list.append(item)
        if len(new_list) == 0:
            console.log("没有新数据")
            return
        else:
            global conn
            conn.ping(reconnect=True)
            cursor = conn.cursor()  # 创建游标
            sql = """
                INSERT INTO novels(novel_id,novel_name,novel_cover,novel_author,novel_category,write_status,updated_time,intro)
                VALUES(%(novel_id)s,%(novel_name)s,%(novel_cover)s,%(novel_author)s,%(novel_category)s,%(write_status)s,%(updated_time)s,%(intro)s)
                """
            try:
                # insert前去重
                cursor.executemany(sql, new_list)
            except Exception as e:
                console.error(f"批量插入失败:{e}")
            conn.commit()
            cursor.close()


def get_novel_id_list_from_db():
    novel_id_list = []
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute("SELECT novel_id FROM novels")
    remote_list = cursor.fetchall()
    for novel_id in remote_list:
        novel_id_list.append(novel_id[0])
    cursor.close()
    return novel_id_list
