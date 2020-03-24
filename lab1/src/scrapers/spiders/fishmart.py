# -*- coding: utf-8 -*-
from scrapy.http.response import Response
import scrapy


class FishmartSpider(scrapy.Spider):
    name = 'fishmart'
    allowed_domains = ['http://www.fishing-mart.com.ua/']
    start_urls = ['http://www.fishing-mart.com.ua/57-Fishing-mart-maxovie-udochki?id_category=57&n=24']

    def parse(self, response: Response):
        products = response.xpath("//li[contains(@class, 'ajax_block_product')]")[:20]
        for product in products:
            yield {
                'description': product.xpath(".//a[contains(@class, 'product-name')]/text()")[0].get(),
                'price': product.xpath(".//span[contains(@class, 'product-price')]/text()")[0].get(),
                'img': product.xpath(".//a[contains(@class, 'product_img_link')]/img/@src")[0].get()
            }
