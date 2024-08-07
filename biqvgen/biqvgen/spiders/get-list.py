import scrapy  # type: ignore
from biqvgen.items import GetListItem


class GetListSpider(scrapy.Spider):
    name = "get-list"  # 爬虫名称
    allowed_domains = ["biqugen.net"]  # 允许的域名
    page = 680  # 当前页数
    start_urls = ["https://m.biqugen.net/full/1.html"]  # 开始爬取的url
    base_url = "https://m.biqugen.net/full/{}.html"  # 下一页的url

    def parse(self, response):
        list = response.css("ul.s_m li.list-item")
        for item in list:
            # 提取url
            url = item.css("a::attr(href)").get()
            #  提取novel_id
            novel_id = int(url.split("book/")[-1].split("/")[0])
            item = GetListItem(novel_id=novel_id)
            yield scrapy.Request(url, callback=self.parse_detail, meta={"item": item})
        # 下一页
        next_page = "".join(response.css("table.page-book a::text").getall())
        if "下一页" in next_page:
            self.page += 1
            next_url = self.base_url.format(self.page)
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            print("没有下一页了")
            return

    def parse_detail(self, response):
        item = response.meta["item"]
        # 提取信息
        item["novel_cover"] = response.css("div.bookinfo img::attr(src)").get()
        item["novel_name"] = response.css("td.info h1::text").get()
        item["novel_author"] = response.css("td.info p")[0].css("a::text").get()
        item["novel_category"] = response.css("td.info p")[1].css("a::text").get()
        item["write_status"] = (
            response.css("td.info p")[2].get().split("<p>")[-1].split("</p>")[0]
        )
        item["updated_time"] = (
            response.css("td.info p")[3].get().split("更新：")[-1].split("</p>")[0]
        )
        item["intro"] = response.css("div.intro::text").get().strip()
        return item
