import datetime

BOT_NAME = "biqugen"
SPIDER_MODULES = ["biqugen.spiders"]
NEWSPIDER_MODULE = "biqugen.spiders"
ROBOTSTXT_OBEY = False  # 不遵守robots协议
ITEM_PIPELINES = {
    # "biqugen.pipelines.GetListPipeline": 300,
    "biqugen.pipelines.GetChapterPipeline": 300,
}
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
CONCURRENT_REQUESTS = 256
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

# 日志设置
FEED_EXPORT_ENCODING = "gbk"
LOG_LEVEL = "WARNING"  # 仅显示警告信息
to_day = datetime.datetime.now()
# log_file_path = "log/scrapy_{}_{}_{} {}_{}.log".format(
#     to_day.year, to_day.month, to_day.day, to_day.hour, to_day.minute
# )
log_file_path = "log/scrapy_{}_{}_{}.log".format(to_day.year, to_day.month, to_day.day)
LOG_FILE = log_file_path
