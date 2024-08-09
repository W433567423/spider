from scrapy.cmdline import execute  # type: ignore
import time
from biqugen.utils import console
from biqugen.db import get_not_crawled_novel_id_list

# execute(["scrapy", "crawl", "get-list"])

if __name__ == "__main__":
    # 每执行完一次，5s后执行下一次
    flag = True
    while flag:
        next = get_not_crawled_novel_id_list(1)
        if not next:
            console.log("所有小说爬取完毕")
            flag = False
        else:
            execute(["scrapy", "crawl", "get-chapter"])
            time.sleep(5)
