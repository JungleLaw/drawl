# myproject/middlewares.py
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
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

    def __init__(self):
        # 可以在这里初始化 driver pool，但更简单且不易出错的方式是
        # 每个请求创建一个新的 driver 实例，用完即关。
        # 对于需要高性能的场景，可以考虑驱动池管理。
        logger.info("SeleniumUndetectedMiddleware initialized")
        # 可选: 配置 Chrome Options
        self.chrome_options = uc.ChromeOptions()
        # self.chrome_options.add_argument('--headless') # 需要 uc 支持 headless 稳定
        # self.chrome_options.add_argument('--no-sandbox')
        # self.chrome_options.add_argument('--disable-dev-shm-usage')
        # self.chrome_options.add_argument('--window-size=1920,1080')
        # 更多选项...

    # 可选: 使用 from_crawler 类方法可以访问 Scrapy 设置
    # @classmethod
    # def from_crawler(cls, crawler):
    #     middleware = cls()
    #     # 可以从 crawler.settings 获取配置
    #     return middleware

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

        logger.info(f"Processing request with Selenium: {request.url}")
        driver = None  # 初始化 driver 变量
        try:
            # --- 关键: 每次请求创建一个新的 uc 实例 ---
            # 注意: 这里的 driver 初始化和后续操作是 *同步阻塞* 的！
            # 这会阻塞 Scrapy 的异步事件循环，影响性能。
            # 在生产环境中，应使用 deferToThread 或与 asyncio 集成
            # 来异步执行这部分阻塞代码，避免阻塞 Scrapy reactor。
            # 为了示例简单，这里直接使用阻塞方式。
            logger.info("Initializing undetected_chromedriver...")
            driver = uc.Chrome(options=self.chrome_options, version_main=request.meta.get(
                'chrome_version'))  # 可以通过meta传递版本

            logger.info(f"Getting URL: {request.url}")
            driver.get(request.url)

            # --- 根据 meta 执行等待或操作 ---
            wait_time = request.meta.get('selenium_wait_time', 10)
            wait_until_selector = request.meta.get('selenium_wait_until')
            temu = request.meta.get('temu')
            logger.info(f"temu: {temu}")
            scroll_down = request.meta.get('selenium_scroll_down')  # 示例：向下滚动次数
            scroll_up = request.meta.get('selenium_scroll_up')  # 示例：向上滚动次数
            click_selector = request.meta.get('selenium_click')  # 示例: 点击元素

            if wait_until_selector:
                logger.info(f"Waiting for element: {temu.home_elements.main_content_list}")
                WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located(
                        (By.XPATH, temu['home_elements']['main_content_list']))
                )
                logger.info("Element found.")
                # search_input_element = driver.find_element(
                #     By.XPATH, wait_until_selector)
                # action = AC(driver)
                # action.move_to_element(search_input_element).perform()
                # time.sleep(1)  # 等待元素可见
                # search_input_element.send_keys("test")  # 示例: 输入搜索内容
                # search_btn_element = driver.find_element(
                #     By.XPATH, "//input[contains(@class, 's_btn') and @type='submit' and @id='su']")
                # # search_btn_element.click()  # 示例: 点击搜索按钮
                # action.move_to_element(search_btn_element).click().perform()
            if scroll_down:
                logger.info(f"Scrolling down {scroll_down} times...")
                for _ in range(scroll_down):
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(request.meta.get(
                        'selenium_scroll_delay', 1))  # 等待滚动加载

            if scroll_up:
                logger.info(f"Scrolling up {scroll_up} times...")
                for _ in range(scroll_up):
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(request.meta.get(
                        'selenium_scroll_delay', 1))

            if click_selector:
                logger.info(f"Clicking element: {click_selector}")
                click_element = WebDriverWait(driver, wait_time).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, click_selector))
                )
                click_element.click()
                logger.info("Element clicked. Waiting after click...")
                # 点击后可能需要额外等待内容加载
                time.sleep(request.meta.get('selenium_wait_after_click', 3))


            # 等待一小段时间确保 JS 执行完成 (或使用更精确的等待条件)
            # time.sleep(3) # 可以根据需要调整或移除

            # 获取页面源码
            body = driver.page_source
            current_url = driver.current_url  # URL 可能已改变 (例如重定向后)
            logger.info(f"Page source retrieved. Current URL: {current_url}")
            # 循环判断当前 url 是否重定向到验证页面，验证完后返回
            while "verifyCode" in current_url:
                logger.info("Page contains 'verifyCode', waiting...")
                time.sleep(10)
                driver.get(request.url)  # 重新加载页面，尝试通过验证
                current_url = driver.current_url  # 更新 current_url
                body = driver.page_source  # 更新页面内容
                logger.info(f"Current URL after verification attempt: {current_url}")
            # 循环判断当前 url 是否重定向到验证页面，验证完后返回
            # while "verifyCode" in current_url:
            #     logger.info("Page contains'verify', skipping.")
            #     # 如果是验证码页面，则等待
            #     time.sleep(10)

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

        # 注意: `process_response` 和 `process_exception` 方法在这里通常不需要实现
        # 因为我们是在 `process_request` 中直接生成并返回了 Response

    # 可选: 在 Spider 关闭时执行清理 (如果使用了驱动池)
    # def spider_closed(self, spider):
    #     logger.info("Spider closed. Cleaning up Selenium resources if necessary.")
    #     # 在这里关闭所有驱动实例或清理驱动池
