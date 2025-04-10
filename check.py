import undetected_chromedriver as uc
import certifi
import os

# 配置SSL证书路径
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()
# 初始化浏览器（自动下载驱动）
driver = uc.Chrome()

# 访问目标网站
driver.get("https://nowsecure.nl")  # 知名反自动化检测测试页

# 检查是否绕过检测
assert "Oh yeah!" in driver.page_source
driver.quit()
