import logging,re, scrapy  # type: ignore
from biqvgen.items import GetListItem
from biqvgen.utils import console



class GetListSpider(scrapy.Spider):
    name = "get-list"  # 爬虫名称
    allowed_domains = ["biqugen.net"]  # 允许的域名
    page =1 # 当前页数
    start_urls = ["https://m.biqugen.net/full/1.html"]  # 开始爬取的url
    base_url = "https://m.biqugen.net/full/{}.html"  # 下一页的url

    # 获取总页数，并开始爬取小说->list
    def parse(self, response):
        page_num = (
            int(
                response.css("div.page-book-turn::text")
                .get()
                .split("/")[1]
                .split("页")[0]
            )
        ) + 1
        for i in range(self.page, page_num):
            url = self.base_url.format(i)
            yield scrapy.Request(url, callback=self.parse_page)

    # 初步获取小说id、小说名、小说连接
    def parse_page(self, response):
        node_list = response.css("ul.s_m li.list-item")
        if len(node_list) == 0:
            console.log("🚀 ~ node_list:", node_list)
            logging.warning(f"该页无数据:{response.url}")
            return
        for node in node_list:
            url = node.css("a::attr(href)").get()
            novel_id = int(url.split("book/")[-1].split("/")[0])
            novel_name = node.css("a::text").get()
            item = GetListItem(novel_id=novel_id, novel_name=novel_name)
            yield scrapy.Request(url, callback=self.parse_detail, meta={"item": item})



    # 获取小说详细信息
    def parse_detail(self, response):
        item = response.meta["item"]
        # 提取信息
        info = response.css("td.info")
        if not info:
            # 写入异常信息
            item["abnormal"] = True
            logging.error(f"{item["novel_name"]} 异常:{response.url}")
            return
        item["novel_cover"] = response.css("div.bookinfo img::attr(src)").get()
        item["novel_author"] = response.css("td.info p")[0].css("a::text").get()
        item["novel_category"] = response.css("td.info p")[1].css("a::text").get()
        item["write_status"] = (
            response.css("td.info p")[2].get().split("状态：")[-1].split("</p>")[0]
        )
        item["updated_time"] = (
            response.css("td.info p")[3].get().split("更新：")[-1].split("</p>")[0]
        )
        item["intro"] = (
            response.css("div.intro::text").get().strip()
            if response.css("div.intro::text").get()
            else ""
        )
        
        yield item

        # item["chapter_list"] = []

        # #  获取小说目录page
        # mulu_node=response.css("div.lb_mulu div.input-group").get()
        # if not mulu_node:
        #     logging.warning(f"{item["novel_name"]} 仅一页目录:{response.url}")
        #     return
        # mulu_page=int(response.css("div.lb_mulu select.form-control option:last-child::text").get().split("第")[-1].split("页")[0])+1
        # for i in range(1,mulu_page):
        #     url = response.url+f"index_{i}.html"
        #     yield scrapy.Request(url, callback=self.parse_chapter, meta={"item": item})
        
    # 获取小说章节
    def parse_chapter(self, response):
        item = response.meta["item"]
        last9 = response.css("ul.last9").getall()
        if len(last9) !=2:
            logging.warning(f"{item["novel_name"]} 异常:{response.url}")
            return
        chapter_list=scrapy.Selector(text=last9.pop()).css("li a").getall()
        for chapter in chapter_list:
            chapter_id=re.search(r'href="(.*?).html"',chapter).group(1)
            chapter_name=re.search(r'>(.*?)</a>',chapter).group(1)
            chapter_title=chapter_name[chapter_name.index('.')+1:]
            chapter_order=int(chapter_name.split(".")[0])
            item["chapter_list"].append({
                "chapter_id":chapter_id,
                "chapter_title":chapter_title,
                "chapter_order":chapter_order
                })
        # if is_last:
        # yield item
            # console.log("🚀 ~ chapter_url:", chapter_url)
            # console.log("🚀 ~ chapter_name:", chapter_name)
            # yield scrapy.Request(chapter_url, callback=self.parse_content, meta={"item": item})
        # item["content"] = content
    
    # 获取小说内容
    def parse_content(self, response):
        item = response.meta["item"]
        content = response.css("div#nr1::text").get()
        console.log("🚀 ~ content:", content)
        # item["content"] = content
        # yield item
