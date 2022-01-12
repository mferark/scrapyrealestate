# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyrealestateItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    rooms = scrapy.Field()
    m2 = scrapy.Field()
    floor = scrapy.Field()
    post_time = scrapy.Field()
    href = scrapy.Field()
