import scrapy  # type: ignore


class GetListItem(scrapy.Item):
    novel_id = scrapy.Field()  #  小说id
    novel_cover = scrapy.Field()  # 封面
    novel_name = scrapy.Field()  #  小说名
    novel_author = scrapy.Field()  # 作者
    novel_category = scrapy.Field()  # 分类
    write_status = scrapy.Field()  # 连载状态
    updated_time = scrapy.Field()  # 更新时间
    intro = scrapy.Field()  # 简介

    abnormal = scrapy.Field()  # 是否异常
    content = scrapy.Field()  # 内容


class GetChapterItem(scrapy.Item):
    novel_id = scrapy.Field()  # 小说id
    novel_name = scrapy.Field()  # 小说名
    chapter_id = scrapy.Field()  # 章节id
    chapter_name = scrapy.Field()  # 章节名
    chapter_content = scrapy.Field()  # 章节内容
    chapter_order = scrapy.Field()  # 章节顺序

    task_id = scrapy.Field()  # 任务id
    total_chapter = scrapy.Field()  # 总章节数
    is_end = scrapy.Field()  # 是否最后一页
