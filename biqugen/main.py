from scrapy.cmdline import execute  # type: ignore
import time
from biqugen.utils import console

# execute(["scrapy", "crawl", "get-list"])

if __name__ == "__main__":
    # 每执行完一次，5s后执行下一次
    while True:
        execute(["scrapy", "crawl", "get-chapter"])
        time.sleep(5)
