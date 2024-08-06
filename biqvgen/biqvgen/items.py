import scrapy  # type: ignore


class GetListItem(scrapy.Item):
    book_id = scrapy.Field()  #  小说id
    book_cover = scrapy.Field()  # 封面
    book_name = scrapy.Field()  #  小说名
    book_author = scrapy.Field()  # 作者
    book_category = scrapy.Field()  # 分类
    write_status = scrapy.Field()  # 连载状态
    updated_time = scrapy.Field()  # 更新时间
    intro = scrapy.Field()  # 简介

    is_extra = scrapy.Field()  # 是否获取额外信息
    is_chapter = scrapy.Field()  # 是否获取章节信息
    abnormal = scrapy.Field()  # 是否异常信息
    file_path = scrapy.Field()  # 文件路径
