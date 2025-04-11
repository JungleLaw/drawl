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

    def start_requests(self):
        logger.info("TmccSpider start_requests")

        for url in self.start_urls:
            logger.info(f"Yielding request for {url} using Selenium")

            # Load the JSON file
            with open("./temu.json", "r") as file:
                temu_data = json.load(file)

            meta = {
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
                'temu': temu_data,  # 将 JSON 数据传递给请求
            }
            yield scrapy.Request(
                url,
                callback=self.parse_page,
                meta=meta,
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

        dynamic_content = response.css(
            '#some-element-that-loads-via-js::text').getall()
        logger.info(f"Dynamic content found: {dynamic_content}")

        # 提取你需要的其他数据...
        yield {
            'url': response.url,
            'title': title,
            'dynamic_data': dynamic_content,
            # ... 其他字段
        }

    # def parse_static(self, response):
    #     # 处理普通请求返回的响应
    #     logger.info(f"Parsing static page: {response.url}")
    #     # ... 提取数据
