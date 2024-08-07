from biqvgen.utils import conn, console


# 批量插入到数据库
def bulk_insert_to_mysql(error, remote_list, novel_list, abnormal_ids):
    new_list = []
    for item in novel_list:
        if item["novel_id"] not in remote_list:
            new_list.append(item)
    if len(new_list) == 0 and len(abnormal_ids) == 0:
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
            error(f"批量插入失败:{e}")
        # error(f"更新异常列表:{len(abnormal_ids)}")
        for novel_id in abnormal_ids:
            cursor.execute(
                f"UPDATE novels SET abnormal = TRUE WHERE novel_id = {novel_id}"
            )
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
    console.log("novels表已重置")
