import scrapy  # type: ignore
from biqugen.db import get_not_crawled_novel_id_list
from biqugen.utils import console
import logging, re
from biqugen.items import GetChapterItem


class GetChapterSpider(scrapy.Spider):
    name = "get-chapter"
    allowed_domains = ["m.biqugen.net"]
    base_url = "https://m.biqugen.net"
    start_urls = []
    ids = get_not_crawled_novel_id_list(1)
    for id in ids:
        start_urls.append(f"https://m.biqugen.net/book/{id}")  # 开始爬取的url

    def parse(self, response):
        novel_id = int(response.url.split("book/")[-1].split("/")[0])
        info = response.css("td.info")
        if not info:
            # 写入异常信息
            logging.error(f"{novel_id} 异常:{response.url}")
            return
        novel_name = response.css("div.bookinfo h1::text").get()
        #  获取小说目录page
        mulu_node = response.css("div.lb_mulu div.input-group").get()
        if not mulu_node:
            logging.warning(f"{novel_id} 仅一页目录:{response.url}")
            return
        mulu_page = (
            int(
                response.css("div.lb_mulu select.form-control option:last-child::text")
                .get()
                .split("第")[-1]
                .split("页")[0]
            )
            + 1
        )
        for i in range(1, mulu_page):
            url = f"https://m.biqugen.net/book/{novel_id}/index_{i}.html"
            yield scrapy.Request(
                url,
                callback=self.parse_chapter,
                meta={"novel_id": novel_id, "novel_name": novel_name},
                dont_filter=True,
            )

    # 获取小说章节
    def parse_chapter(self, response):
        novel_id = response.meta["novel_id"]
        novel_name = response.meta["novel_name"]
        last9 = response.css("ul.last9").getall()
        chapter_node_list = scrapy.Selector(text=last9.pop()).css("li a").getall()
        for chapter in chapter_node_list:
            chapter_id = re.search(r'href="(.*?).html"', chapter).group(1)
            chapter_name = re.search(r">(.*?)</a>", chapter).group(1)
            item = GetChapterItem(
                novel_id=novel_id,
                chapter_id=chapter_id,
                chapter_name=chapter_name,
                novel_name=novel_name,
            )
            url = f"{self.base_url}/book/{novel_id}/{chapter_id}.html"
            yield scrapy.Request(
                url,
                callback=self.parse_content,
                meta={"item": item},
                dont_filter=True,
            )
        # if is_last:
        # yield item
        # console.log("🚀 ~ chapter_url:", chapter_url)
        # console.log("🚀 ~ chapter_name:", chapter_name)
        # yield scrapy.Request(chapter_url, callback=self.parse_content, meta={"item": item})
        # item["content"] = content

    # 获取小说内容
    def parse_content(self, response):
        chapter_content = ""
        item = response.meta["item"]
        contents = response.css("div#nr1 *::text").getall()
        for content in contents:
            chapter_content += f"{content}\n"
        item["chapter_content"] = chapter_content
        yield item
