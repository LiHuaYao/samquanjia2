import random

from selenium.webdriver.chrome.options import Options

class ChromeOptions():
    @staticmethod
    def get_options():
        chrome_options = Options()

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("window-size=1024,768")
        # 添加沙盒模式
        chrome_options.add_argument("--no-sandbox")

        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-browser-side-navigation")
        #-linux下打开-
        # 无头模式
        chrome_options.add_argument('--headless')
        # 单线程
        chrome_options.add_argument("--single-process")
        # 不要zygote线程
        chrome_options.add_argument("--no-zygote")

        chrome_options.add_argument("--renderer-process-limit=1")
        #-linux-end--
        chrome_options.add_argument("--disable-plugins")
        # chrome_options.add_argument("--enable-automation")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        #隐藏滚动条, 应对验证码图片偏移
        chrome_options.add_argument('--hide-scrollbars')
        # 无图
        # No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", No_Image_loading)

        # 添加UA
        ua_list=[
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        # 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        ]
        #Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36
        index = random.randint(0, len(ua_list)-1 )
        ua = ua_list[index]
        print(ua)
        chrome_options.add_argument('--user-agent="%s"' % ua)

        return chrome_options