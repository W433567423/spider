from biqvgen.utils import conn, console
import logging


# 批量插入到数据库
def bulk_insert_to_mysql(remote_list, novel_list, abnormal_list):
    new_list = []
    for item in novel_list:
        if item["novel_id"] not in remote_list:
            new_list.append(item)
    if len(new_list) == 0 and len(abnormal_list) == 0:
        logging.warning("没有新数据")
        return
    else:
        # logging.warning(f"爬取结束,开始保存到数据库:{len(new_list)}")
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
        #     for item in new_list:
        #         try:
        #             cursor.execute(
        #                 f"""
        #                     INSERT INTO novels(novel_id,novel_name,novel_cover,novel_author,novel_category,write_status,updated_time,intro)
        #                     VALUES({item["novel_id"]},{item["novel_name"]},{item["novel_cover"]},{item["novel_author"]},{item["novel_category"]},{item["write_status"]},{item["updated_time"]},{item["intro"]})
        # """
        #             )
        #         except Exception as e:
        #             logging.error(f"批量插入失败:{e}")
        #             logging.error(
        #                 f"""
        #                     INSERT INTO novels(novel_id,novel_name,novel_cover,novel_author,novel_category,write_status,updated_time,intro)
        #                     VALUES({item["novel_id"]},{item["novel_name"]},{item["novel_cover"]},{item["novel_author"]},{item["novel_category"]},{item["write_status"]},{item["updated_time"]},{item["intro"]})
        # """
        #             )
        if len(abnormal_list) != 0:
            # logging.warning(f"更新异常列表:{len(abnormal_list)}")
            cursor.executemany(
                "UPDATE novels SET abnormal = TRUE WHERE novel_id = %s",
                [(item,) for item in abnormal_list],
            )
        logging.warning("保存到数据库成功")
        conn.commit()
        cursor.close()


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
            abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
            content LONGTEXT COMMENT '小说内容'
            );
        """
    )
    conn.commit()
    cursor.close()
    console.log("novels表已重置")
