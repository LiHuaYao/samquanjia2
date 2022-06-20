from threading import Thread

import psutil
from selenium.webdriver.chrome.service import Service

from config import Config
from model.BankType import BankType
from model.IPPool import IPPool
from plus.ChromeOptions import ChromeOptions
from plus.Personification import Personification
import time
from datetime import datetime

from dao.Status import Status
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    StaleElementReferenceException, WebDriverException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
class  CheckTest(Personification):

    def __init__(self,proxy_index=None):
        Personification.__init__(self)
        self.status_path = None
        self.is_open = False
        self.is_check = False
        self.select_click = False;
        self.psw_input = None;
        self.tranfer_list_status = 0;#0-初始化 1-输入用户名 2-登录成功（在 account页面） 3-已选择账户（在转账列表页）
        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=CheckTest")
        # 无图
        if Config.CHECK_OPEN_NO_IMAGE == True :
            No_Image_loading = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", No_Image_loading)
            self.print_d('CheckTest-使用无图模式')
        # 设置代理
        if(proxy_index is not None):
            self.proxy_index = proxy_index
            proxy = IPPool.ip_list[proxy_index]
            proxy_server = proxy.proxy
            if proxy_server.find('://') < 0:
                proxy_server = 'http://'+proxy_server
            self.print_d('CheckTest-使用代理：%s'%proxy_server)
            chrome_options.add_argument("--proxy-server="+proxy_server)
        else:
            self.print_d('CheckTest-不使用代理服务')
        self.print_d('新建窗口-准备获取Chrome')
        self.driver = webdriver.Chrome(options=chrome_options)
        self.print_d('新建窗口-已获取到Chrome-准备打开页面')
        # driver = webself.driver.Chrome()
        # self.driver.maximize_window()  # 最大化浏览器
        # self.driver.implicitly_wait(8)  # 设置隐式时间等待
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
        self.driver.delete_all_cookies()
        open_status = self.open_and_init()
        self.open_code = open_status['actionCode']
    def open_and_init(self):
        try:
            # self.driver.get('http://httpbin.org/get');
            self.driver.get(Config.CHECK_OPEN_URL);
        except TimeoutException:
            print('-----CheckTest--TimeoutException------')
            self.quit();
        # self.sleep(5)
        self.print_d('新建窗口-打开页面-页面加载中')
        self.sendStatus(self.order_no,Status.o000)
        driver_process = psutil.Process(self.driver.service.process.pid)
        if driver_process:
            self.chrome_driver_process = driver_process
        children_list = driver_process.children()
        if children_list:
            self.chrome_process = children_list[0]
        # self.sendStatus(self.order_no,Status.o000);
        locator = (By.ID, 'test')
        try:
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            pass
            # try:
            #     title = self.driver.title
            #     if(title.find('Access Denied') > -1):
            #         self.print_d('[第一次发现Access Denied-准备刷新]')
            #         self.driver.refresh()
            # except NoSuchElementException:
            #     pass
        try:
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            pass
            # try:
            #     title = self.driver.title
            #     if(title.find('Access Denied') > -1):
            #         self.print_d('[第二次发现Access Denied-准备退出]')
            #         if self.proxy_index is not None:
            #             proxy = IPPool.ip_list[self.proxy_index]
            #             denied_count = proxy.denied_count + 1
            #             proxy.denied_count = denied_count
            #             if denied_count >= Config.MAX_DENIED_COUNT :
            #                 self.print_d('[已到Access Denied次数-准备刷新IP]')
            #         self.is_open = False
            #         self.quit()
            #         return self.sendStatus(self.order_no,Status.o403)
            # except NoSuchElementException:
            #     pass
        try:
            WebDriverWait(self.driver, 50, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('-----CheckTest页面打开异常-第二步-----')
            # print('-----CheckTest页面打开异常，准备关闭-----')
            # self.quit()
        locator1 = (By.CLASS_NAME, 'select2-selection--single')
        try:
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator1))
        except Exception:
            # self.print_d('-----CheckTest页面打开异常，直接关闭窗口-----')
            self.order_no = 'CheckTest-init'
            self.screen(None)
            self.save_html('CheckTest-error')
            # try:
            #     title = self.driver.title
            #     if(title.find('Access Denied') > -1):
            #         self.print_d(title)
            #         body = self.driver.find_element_by_tag_name('body')
            #         # self.print_d(body.text)
            #         return self.sendStatus(self.order_no,Status.o403)
            # except NoSuchElementException:
            #     pass
            # if (Config.INVALID_WINDOW_AUTO_CLOSE):
            self.print_d('-----CheckTest页面打开异常，INVALID_WINDOW_AUTO_CLOSE=True 直接关闭窗口-----')
            self.quit()
            # else:
            #     self.print_d('-----CheckTest页面打开异常，INVALID_WINDOW_AUTO_CLOSE=False 不需要关闭窗口-----')
            return self.sendStatus(self.order_no,Status.o002)
        else:
            self.print_d('新建窗口-页面加载完成')
            self.is_open = True
            self.sendStatus(self.order_no, Status.o001)
            select = self.driver.find_element_by_class_name("select2-selection--single");
            try:
                self.print_d("click..")
                select.click()
            except Exception :
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", select)
            self.select_click = True;
            jsString = '$(".select2-results__options").css("height", "auto")';
            self.driver.execute_script(jsString)
        return self.sendStatus(self.order_no,Status.o001)
