import scrapy
import random
import time

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36"
]



class EstateSpiderSpider(scrapy.Spider):
    name = "estate_spider"
    allowed_domains = ["hepsiemlak.com"]
    start_urls = ["https://www.hepsiemlak.com/ankara-satilik?page=1"]

    def start_requests(self):
        base_url = 'https://www.hepsiemlak.com/ankara-satilik?page='
        for page in range(1, 101):
            headers = {
                'User-Agent': random.choice(USER_AGENTS)
            }
            yield scrapy.Request(url=f"{base_url}{page}", callback=self.parse, headers=headers)

    def parse(self, response):
        if response.status == 429:
            self.logger.warning("Received 429 response, retrying...")
            time.sleep(10)  # Wait longer before retrying
            yield scrapy.Request(url=response.url, callback=self.parse)
            return

        listing_links = response.xpath('//div[@class="listView"]/ul/li/article/div/div[2]/div/a/@href').extract()

        for link in listing_links:
            yield response.follow(link, self.parse_item)

        next_page = response.xpath('//a[@class="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

        time.sleep(15)

    def parse_item(self, response):
        time.sleep(10)
        ilan_bilgileri = {}

        ul_elements = response.xpath('//div[@class="spec-groups"]/ul')

        for ul in ul_elements:
            for li in ul.xpath('.//li'):
                label = li.xpath('.//span[@class="txt"]/text()').get()
                value_spans = li.xpath('.//span[not(@class="txt")]/text()').getall()
                if label and value_spans:
                    label = label.strip()
                    value = ' '.join([v.strip() for v in value_spans])
                    ilan_bilgileri[label] = value

        location_list = response.xpath('//ul[@class="short-property"]/li')
        if len(location_list) > 1:
            city = location_list[0].xpath("text()").get().strip()
            district = location_list[1].xpath("text()").get().strip()
            ilan_bilgileri["city"] = city
            ilan_bilgileri["district"] = district

        price_element = response.xpath('//p[@class="fz24-text price"]/text()').get().strip()
        ilan_bilgileri["price"] = price_element

        yield ilan_bilgileri
