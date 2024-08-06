# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BiqvgenPipeline:
    def process_item(self, item, spider):
        # intro
        #  .replace("\xa0", "").replace("\u3000", "")
        item["intro"] = item["intro"].replace("\xa0", "").replace("\u3000", "")
        print(item)
        return item
