import scrapy  # type: ignore


class GetChapterSpider(scrapy.Spider):
    name = "get-chapter"
    allowed_domains = ["biqvgen.net"]
    start_urls = ["https://biqvgen.net"]

    def parse(self, response):
        pass
