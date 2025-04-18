# myproject/middlewares.py
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import certifi
import os
from selenium.webdriver.common.action_chains import ActionChains as AC

# 配置SSL证书路径
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()
# 获取 middleware 的 logger
logger = logging.getLogger(__name__)


class SeleniumUndetectedMiddleware:
    """
    Scrapy Downloader Middleware using Selenium with undetected-chromedriver.
    """
    def __init__(self, crawler):
        # 可以在这里初始化 driver pool，但更简单且不易出错的方式是
        # 每个请求创建一个新的 driver 实例，用完即关。
        # 对于需要高性能的场景，可以考虑驱动池管理。
        logger.info("SeleniumUndetectedMiddleware initialized")
        # 可选: 配置 Chrome Options
        # self.chrome_options = uc.ChromeOptions()
        # self.chrome_options.add_argument('--headless') # 需要 uc 支持 headless 稳定
        # self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        # self.chrome_options.add_argument('--window-size=1920,1080')
        # 更多选项...
        self.crawler = crawler

    # 可选: 使用 from_crawler 类方法可以访问 Scrapy 设置
    @classmethod
    def from_crawler(cls, crawler):
        # 创建中间件实例
        mw = cls(crawler)
        return mw

    def process_request(self, request, spider):
        # +++ Add these lines for debugging +++
        logger.info(f"Middleware received request FOR: {request.url}")
        logger.info(f"Middleware received request META: {request.meta}")
        use_selenium_flag = request.meta.get('use_selenium')
        logger.info(f"Value of 'use_selenium' in meta: {use_selenium_flag}")
        # ++++++++++++++++++++++++++++++++++++++

        # 判断请求是否需要 Selenium 处理 (通过 meta 标记)
        if not request.meta.get('use_selenium'):
            logger.info("Request does not require Selenium, passing through.")
            return None  # 返回 None，让 Scrapy 继续处理该请求

        # 检查 driver 是否已由 Extension 初始化
        driver = getattr(self.crawler, 'driver', None)
        if not driver:
            logger.error("WebDriver instance not found on crawler object. Extension might have failed.")
            # 可以考虑返回一个失败的响应或引发异常
            return None # 或者根据需要处理
        logger.info(f"Processing request with Selenium: {request.url}")


        logger.info(f"Getting URL: {request.url}")
        driver.get(request.url)
        time.sleep(10) # 可以根据需要调整或移除
        import random
        # 随机等待时间，避免被检测到
        driver.implicitly_wait(random.randint(120, 220))

        logger.info("Crawling home category...")
        # 解析首页分类信息
        # 这里可以使用 Scrapy 的选择器来提取数据
        # 例如，使用 XPath 或 CSS 选择器来提取分类链接和名称
        # 返回分类数据供后续处理
        try:
            # --- 关键: 每次请求创建一个新的 uc 实例 ---
            # 注意: 这里的 driver 初始化和后续操作是 *同步阻塞* 的！
            # 这会阻塞 Scrapy 的异步事件循环，影响性能。
            # 在生产环境中，应使用 deferToThread 或与 asyncio 集成
            # 来异步执行这部分阻塞代码，避免阻塞 Scrapy reactor。
            # 为了示例简单，这里直接使用阻塞方式。
            # --- 根据 meta 执行等待或操作 ---
            crawl_home = request.meta.get('crawl_home')
            wait_time = request.meta.get('selenium_wait_time', 10)
            wait_until_selector = request.meta.get('selenium_wait_until')
            temu = request.meta.get('temu')
            logger.info(f"temu: {temu}")
            scroll_down = request.meta.get('selenium_scroll_down')  # 示例：向下滚动次数
            scroll_up = request.meta.get('selenium_scroll_up')  # 示例：向上滚动次数
            click_selector = request.meta.get('selenium_click')  # 示例: 点击元素
            if crawl_home:
                if wait_until_selector:
                    logger.info(f"Waiting for element temu.home_elements.category_trigger")
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located(
                            (By.XPATH, temu['home_elements']['category_trigger']))
                    )
                    driver.execute_script("window.scrollTo(0, 0);")
                    logger.info("Element found.")
                    category_trigger_element = driver.find_element(By.XPATH, temu['home_elements']['category_trigger'])
                    # 模拟鼠标悬停
                    action = AC(driver)
                    action.click(category_trigger_element).perform()
                    # 等待元素加载
                    # driver.implicitly_wait(random.randint(5, 10))
                    WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located(
                            (By.XPATH, temu['home_elements']['wait_list']))
                    )
                    logger.info(f"starting to find category list elements {temu['home_elements']['category_list']}")
                    category_list_elements = driver.find_elements(By.XPATH, temu['home_elements']['category_list'])
                    logger.info(f"Category list elements: {category_list_elements}")
                # 等待一小段时间确保 JS 执行完成 (或使用更精确的等待条件)
                time.sleep(3) # 可以根据需要调整或移除
                # 获取页面源码
                body = driver.page_source
                current_url = driver.current_url  # URL 可能已改变 (例如重定向后)
                logger.info(f"Page source retrieved. Current URL: {current_url}")
                # --- 必须关闭 driver ---
                logger.info("Quitting WebDriver...")
                # driver.quit()
                logger.info("WebDriver quit.")
                return HtmlResponse(
                    url=current_url,
                    body=body,
                    encoding='utf-8',
                    request=request  # 将原始请求附加到响应中，方便追踪
                )
            else :
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, temu['home_elements']['goods_list']))
                )
                logger.info("Element found.")
                # category_trigger_element = driver.find_element(By.XPATH, temu['home_elements']['category_trigger'])
                # # 模拟鼠标悬停
                # action = AC(driver)
                # action.click(category_trigger_element).perform()
                # 等待元素加载
                driver.implicitly_wait(random.randint(5, 10))
                # WebDriverWait(driver, wait_time).until(
                #     EC.presence_of_element_located(
                #         (By.XPATH, temu['home_elements']['goods_list']))
                # )
                logger.info(f"starting to find category list elements {temu['home_elements']['goods_list']}")
                category_list_item_elements = driver.find_elements(By.XPATH, temu['home_elements']['goods_list_item'])
                logger.info(f"Category list elements: {category_list_item_elements}")
                time.sleep(3) # 可以根据需要调整或移除
                # 获取页面源码
                body = driver.page_source
                current_url = driver.current_url  # URL 可能已改变 (例如重定向后)
                logger.info(f"Page source retrieved. Current URL: {current_url}")
                # 循环判断当前 url 是否重定向到验证页面，验证完后返回
                # while "verifyCode" in current_url:
                #     logger.info("Page contains 'verifyCode', waiting...")
                #     time.sleep(10)
                #     driver.get(request.url)  # 重新加载页面，尝试通过验证
                #     current_url = driver.current_url  # 更新 current_url
                #     body = driver.page_source  # 更新页面内容
                #     logger.info(f"Current URL after verification attempt: {current_url}")

                # --- 必须关闭 driver ---
                logger.info("Quitting WebDriver...")
                # driver.quit()
                logger.info("WebDriver quit.")

                # 返回 Scrapy 的 HtmlResponse 对象
                # Scrapy 会将这个 Response 发送给请求指定的回调函数
                return HtmlResponse(
                    url=current_url,
                    body=body,
                    encoding='utf-8',
                    request=request  # 将原始请求附加到响应中，方便追踪
                )
        except Exception as e:
            logger.error(
                f"SeleniumMiddleware error for {request.url}: {e}", exc_info=True)
            # 出错时也要确保关闭 driver
            if driver:
                logger.info("Quitting WebDriver due to exception...")
                # driver.quit()
                logger.info("WebDriver quit.")
            # 可以选择返回 None 让 Scrapy 重试，或返回一个空的 Response，或重新抛出异常
            return None  # 或者根据策略处理失败
