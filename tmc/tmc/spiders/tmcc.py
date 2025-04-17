import scrapy
import logging
import json

logger = logging.getLogger(__name__)


class TmccSpider(scrapy.Spider):
    name = "tmcc"
    allowed_domains = ["www.temu.com"]
    start_urls = ["https://www.temu.com"]
    # allowed_domains = ["www.baidu.com"]
    # start_urls = ["https://www.baidu.com"]
    meta = None
    temu_data = None

    def start_requests(self):
        logger.info("TmccSpider start_requests")

        for url in self.start_urls:
            logger.info(f"Yielding request for {url} using Selenium")

            # Load the JSON file
            with open("./temu.json", "r") as file:
                self.temu_data = json.load(file)

            self.meta = {
                'use_selenium': True,  # 标记需要 Selenium 处理
                # --- 可选参数传递给 Middleware ---
                'selenium_wait_time': 60,  # 等待超时时间
                'selenium_wait_until': '//input[@class=\'s_ipt\']',  # 等待特定元素出现
                'selenium_scroll_up': 3,  # 向下滚动 3 次
                'selenium_scroll_down': 1,  # 向下滚动 3 次
                'selenium_scroll_delay': 1.5,  # 每次滚动后等待 1.5 秒
                # 'selenium_click': 'button.load-more', # 示例: 点击加载更多按钮
                # 'selenium_wait_after_click': 5, # 点击后等待 5 秒
                'chrome_version': 135,  # 可选，指定 Chrome 主版本
                'temu': self.temu_data,  # 将 JSON 数据传递给请求
                'crawl_home': True,  # 是否爬取首页
            }
            yield scrapy.Request(
                url,
                callback=self.parse_page,
                meta=self.meta,
            )
        # 也可以在这里添加不需要 Selenium 处理的普通请求
        # yield scrapy.Request('https://example.com/static-page', callback=self.parse_static)

    def parse_page(self, response):
        # 这个 response 是由 SeleniumUndetectedMiddleware 生成的 HtmlResponse
        # 它包含了由浏览器完全渲染后的 HTML 内容
        logger.info(f"Parsing page rendered by Selenium: {response.url}")

        # 现在可以使用 Scrapy 的选择器来提取数据
        title = response.css('title::text').get()
        logger.info(f"Page title: {title}")

        # dynamic_content = response.css(
        #     '#some-element-that-loads-via-js::text').getall()
        # logger.info(f"Dynamic content found: {dynamic_content}")
        body = response.body
        # Write the response body to a local file for inspection
        with open("response_body.html", "wb") as file:
            file.write(body)
        logger.info("Response body written to response_body.html")
        logger.info(f"Response body length: {len(body)}")
        logger.info(f"self.temu_data['home_elements']['category_list']={self.temu_data['home_elements']['category_list']}")
        # 使用 XPath 解析页面内容,返回的是一个列表，列表中每个元素都是一个 Selector 对象
        category_list_elements = response.xpath(self.temu_data['home_elements']['category_list'])
        logger.info(f"Category list elements found: {len(category_list_elements)}")
        self.meta['crawl_home'] = False
        # 从 category_list_elements 中提取数据
        for element in category_list_elements:
            logger.info(f"Category list element: {element}")
        #     # 你可以在这里解析每个元素，提取你需要的数据
        #     # 例如，使用正则表达式或进一步的 XPath/CSS 选择器来提取信息
        #     # 使用 CSS 或 XPath 提取元素的中包含的 a 标签
            # 提取 a 标签的 href 属性
            category_link = element.xpath('@href').get()
            logger.info(f"Category link: {category_link}")
            # logger.info(f"Category name: {category_name}, Category link: {category_link}")
            url = f"https://www.temu.com{category_link}"
            yield scrapy.Request(
                url,
                callback=self.parse_category,
                meta=self.meta,
            )
        #     # 你可以将提取的数据存储到字典中，或者进一步处理
        #     yield {
        #         'category_name': category_name,
        #         'category_link': category_link,
        #     }
        logger.info("Finished parsing page.")


    # def parse_static(self, response):
    #     # 处理普通请求返回的响应
    #     logger.info(f"Parsing static page: {response.url}")
    #     # ... 提取数据

    def parse_category(self, response):
        # 解析列表页
        logger.info(f"Parsing category page: {response.url}")
        # 提取列表数据
        # 现在可以使用 Scrapy 的选择器来提取数据
        title = response.css('title::text').get()
        logger.info(f"Page title: {title}")

        # dynamic_content = response.css(
        #     '#some-element-that-loads-via-js::text').getall()
        # logger.info(f"Dynamic content found: {dynamic_content}")
        body = response.body
        # 使用 XPath 解析页面内容,返回的是一个列表，列表中每个元素都是一个 Selector 对象
        goods_list_item_elements = response.xpath(self.temu_data['home_elements']['goods_list_item'])
        logger.info(f"Goods list item elements found: {len(goods_list_item_elements)}")
        logger.info("Finished parsing Goods list.")