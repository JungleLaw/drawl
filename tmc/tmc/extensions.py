import logging
from scrapy import signals
import undetected_chromedriver as uc
import time

logger = logging.getLogger(__name__)

class UndetectedChromeDriverExtension:
    def __init__(self, crawler):
        self.crawler = crawler
        # 将 driver 实例附加到 crawler 对象上，以便中间件访问
        self.crawler.driver = None
        # 连接 Scrapy 信号
        crawler.signals.connect(self.engine_started, signal=signals.engine_started)
        crawler.signals.connect(self.engine_stopped, signal=signals.engine_stopped)
        logger.info("UndetectedChromeDriverExtension initialized.")

    @classmethod
    def from_crawler(cls, crawler):
        # 创建扩展实例
        ext = cls(crawler)
        return ext

    def engine_started(self):
        logger.info("Scrapy engine started. Initializing undetected_chromedriver...")
        try:
            # --- 初始化 WebDriver ---
            # 你可以在这里配置 options, e.g., headless (但不适用于需要手动验证的场景)
            options = uc.ChromeOptions()
            # options.add_argument('--headless') # 首次需要验证，不能用 headless
            # 可以添加其他你需要的 undetected_chromedriver 参数
            self.crawler.driver = uc.Chrome(options=options, use_subprocess=True) # use_subprocess=True 可能更稳定
            logger.info("undetected_chromedriver instance created.")

            # --- 人工验证步骤 ---
            # 导航到需要验证的初始页面（例如登录页或首页）
            # start_url = self.crawler.settings.get('INITIAL_VERIFICATION_URL', 'https://example.com/login') # 从 settings.py 读取初始 URL
            # if start_url:
            #      logger.info(f"Navigating to initial verification URL: {start_url}")
            #      self.crawler.driver.get(start_url)
            #      # 在这里暂停，等待人工操作
            #      input("!!!!!!\nPlease complete the website verification/login in the browser window, then press Enter in this console to continue scraping...\n!!!!!!")
            #      logger.info("Manual verification assumed complete. Proceeding with crawl.")
            # else:
            #      logger.warning("INITIAL_VERIFICATION_URL not set in settings. Skipping initial navigation for verification.")
        except Exception as e:
            logger.error(f"Failed to initialize undetected_chromedriver or perform initial navigation: {e}", exc_info=True)
            # 如果初始化失败，可以考虑关闭爬虫
            self.crawler.engine.close_spider(self.crawler.spider, reason='webdriver_init_failed')

    def engine_stopped(self):
        logger.info("Scrapy engine stopped. Closing undetected_chromedriver...")
        if self.crawler.driver:
            try:
                self.crawler.driver.quit()
                logger.info("undetected_chromedriver instance closed.")
            except Exception as e:
                logger.error(f"Error closing undetected_chromedriver: {e}", exc_info=True)
        # 清理引用（虽然可能不是严格必需，但是好习惯）
        self.crawler.driver = None