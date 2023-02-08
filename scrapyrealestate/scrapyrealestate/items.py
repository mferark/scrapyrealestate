# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ScrapyrealestateItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    price = scrapy.Field()
    m2 = scrapy.Field()
    rooms = scrapy.Field()
    floor = scrapy.Field()
    town = scrapy.Field()
    neighbour = scrapy.Field()
    street = scrapy.Field()
    number = scrapy.Field()
    type = scrapy.Field()
    title = scrapy.Field()
    href = scrapy.Field()
    site = scrapy.Field()
    post_time = scrapy.Field()
