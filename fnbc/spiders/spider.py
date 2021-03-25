import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FnbcItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FnbcSpider(scrapy.Spider):
	name = 'fnbc'
	start_urls = ['https://fnbc.us/category/newsworthy/']

	def parse(self, response):
		post_links = response.xpath('//section[@id="archives-4"]//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_archiv)

	def parse_archiv(self, response):
		post_links = response.xpath('//h3//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

	def parse_post(self, response):
		date = response.xpath('//time/@datetime').get()
		title = response.xpath('//h2/text()').get()
		content = response.xpath('//div[@class="mk-single-content clearfix"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FnbcItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
