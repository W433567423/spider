# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from biqvgen.utils import conn, console
from rich.progress import BarColumn, TimeRemainingColumn, MofNCompleteColumn


class BiqvgenPipeline:
    novel_list = []  # 小说列表

    #  处理item
    def process_item(self, item, spider):
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

        # if len(self.novel_list) == 1000:
        #     self.bulk_insert_to_mysql(self.novel_list, spider)
        #     del self.novel_list[:]

    # 开启爬虫
    def open_spider(self, spider):
        # 创建数据库
        global conn
        conn.ping(reconnect=True)
        cursor = conn.cursor()  # 创建游标
        # 创建数据表
        cursor.execute("DROP TABLE IF EXISTS novels;")
        cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS novels(
                novel_id INT PRIMARY KEY COMMENT '笔趣阁小说id',
                novel_name VARCHAR(255) COMMENT '小说名' not null,
                novel_cover VARCHAR(255) COMMENT '小说封面',
                novel_author VARCHAR(255) COMMENT '小说作者',
                novel_category VARCHAR(255) COMMENT '小说分类',
                write_status VARCHAR(255) COMMENT '小说连载状态',
                updated_time VARCHAR(255) COMMENT '小说发布时间',
                intro TEXT COMMENT '小说简介',
                is_extra BOOLEAN DEFAULT FALSE COMMENT '是否已添加额外信息(连载情况、人气、评分等)',
                is_chapter BOOLEAN DEFAULT FALSE COMMENT '是否已添加章节信息',
                abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
                file_path VARCHAR(255) COMMENT '小说文件路径'
                );
            """
        )
        conn.commit()
        cursor.close()
        # console.log("数据库初始化成功")
        pass

    # 关闭爬虫
    def close_spider(self, spider):
        # 保存到数据库
        # self.bulk_insert_to_mysql(self.novel_list, spider)
        console.log("🚀 ~ self.novel_list, spider:", len(self.novel_list))
        console.log(self.novel_list[:1])
        pass

    # 批量插入到数据库
    def bulk_insert_to_mysql(self, data, spider):
        console.log("开始批量插入到数据库")
        global conn
        conn.ping(reconnect=True)
        cursor = conn.cursor()  # 创建游标
        cursor.executemany(
            "INSERT INTO novels(novel_id, novel_name, novel_cover, novel_author, novel_category, write_status, updated_time, intro) VALUES(%(novel_id)s, %(novel_name)s, %(novel_cover)s, %(novel_author)s, %(novel_category)s, %(write_status)s, %(updated_time)s, %(intro)s);",
            (data),
        )
        conn.commit()
        cursor.close()
