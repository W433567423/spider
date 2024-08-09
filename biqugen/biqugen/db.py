from biqugen.utils import conn, console
import logging
import time


#  reset novels表
def reset_novels_table():
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()
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
            updated_time VARCHAR(255) COMMENT '小说更新时间',
            intro TEXT COMMENT '小说简介',
            is_chapter BOOLEAN DEFAULT FALSE COMMENT '是否已爬取章节',
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
            );
        """
    )
    conn.commit()
    cursor.close()
    console.log("novels表已重置")


# reset chapters表
def reset_chapters_table():
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS chapters;")
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS chapters(
            chapter_id INT PRIMARY KEY COMMENT '笔趣阁章节id',
            novel_id INT COMMENT '小说id',
            novel_name VARCHAR(255) COMMENT '小说名',
            chapter_name VARCHAR(255) COMMENT '章节名',
            chapter_order INT COMMENT '章节顺序',
            chapter_content LONGTEXT COMMENT '章节内容'
            );
        """
    )
    cursor.execute(
        """
            UPDATE novels SET is_chapter = FALSE;
        """
    )
    conn.commit()
    cursor.close()
    console.log("chapters表已重置")


#  从数据库获取小说id列表
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


# 从数据库获取chapter_id列表
def get_chapter_id_list_from_db(novel_id):
    chapter_id_list = []
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute(f"SELECT chapter_id FROM chapters WHERE novel_id = {novel_id}")
    remote_list = cursor.fetchall()
    for chapter_id in remote_list:
        chapter_id_list.append(chapter_id[0])
    cursor.close()
    return chapter_id_list


# 获取没有爬取章节的小说id列表
def get_not_crawled_novel_id_list(limit=0):
    sql = "SELECT novel_id FROM novels WHERE is_chapter = FALSE AND abnormal = FALSE ORDER BY novel_id ASC"
    if limit != 0:
        sql += f" LIMIT {limit}"
    novel_id_list = []
    global conn
    conn.ping(reconnect=True)
    cursor = conn.cursor()
    cursor.execute(sql)
    remote_list = cursor.fetchall()
    for novel_id in remote_list:
        novel_id_list.append(novel_id[0])
    cursor.close()
    return novel_id_list


# 批量插入到数据库
def bulk_insert_to_mysql(remote_list, novel_list, abnormal_list):
    new_list = []
    for item in novel_list:
        if item["novel_id"] not in remote_list:
            new_list.append(item)
    if len(new_list) == 0 and len(abnormal_list) == 0:
        return
    else:
        global conn
        conn.ping(reconnect=True)
        cursor = conn.cursor()  # 创建游标
        sql = "INSERT INTO novels(novel_id,novel_name,novel_cover,novel_author,novel_category,write_status,updated_time,intro) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.executemany(
            sql,
            [
                (
                    item["novel_id"],
                    item["novel_name"],
                    item["novel_cover"],
                    item["novel_author"],
                    item["novel_category"],
                    item["write_status"],
                    item["updated_time"],
                    item["intro"],
                )
                for item in new_list
            ],
        )
        if len(abnormal_list) != 0:
            # logging.warning(f"更新异常列表:{len(abnormal_list)}")
            cursor.executemany(
                "UPDATE novels SET abnormal = TRUE WHERE novel_id = %s",
                [(item,) for item in abnormal_list],
            )
        conn.commit()
        cursor.close()


# 批量插入章节到数据库
def bulk_insert_chapters_to_mysql(chapter_list):
    if len(chapter_list) == 0:
        logging.warning("没有新数据")
        return
    else:
        global conn
        conn.ping(reconnect=True)
        cursor = conn.cursor()  # 创建游标
        sql = "INSERT INTO chapters(chapter_id,novel_id,novel_name,chapter_name,chapter_order,chapter_content) VALUES(%s,%s,%s,%s,%s,%s)"
        cursor.executemany(
            sql,
            [
                (
                    item["chapter_id"],
                    item["novel_id"],
                    item["novel_name"],
                    item["chapter_name"],
                    item["chapter_order"],
                    item["chapter_content"],
                )
                for item in chapter_list
            ],
        )
        cursor.execute(
            "UPDATE novels SET is_chapter = TRUE WHERE novel_id = %s",
            chapter_list[0]["novel_id"],
        )
        conn.commit()
        cursor.close()
        # 打印当前时间
        now=(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(
            f"{now}《{chapter_list[0]["novel_name"]}》存储成功,章节数量：{len(chapter_list)}"
        )
