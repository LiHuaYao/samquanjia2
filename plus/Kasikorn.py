import time
from datetime import datetime

import psutil
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,WebDriverException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from dao.Status import Status
from model.BankType import BankType
from model.IPPool import IPPool
from plus.ChromeOptions import ChromeOptions
from plus.Personification import Personification
from config import Config
from selenium.webdriver.support.select import Select

class Kasikorn(Personification) :

    def __init__(self, proxy_index = None, order_no = None):
        Personification.__init__(self)

        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no

        self.tranfer_list_status = 0;
        self.config = Config.Kasikorn
        self.status_path = self.config.STATUS_PATH

        self.print_d('准备打开页面')

        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=krungsri")

        self.print_d('新建窗口-准备获取Chrome')

        # 设置代理
        if (self.config.US_PROXY_SERVER and proxy_index is not None):
            self.proxy_index = proxy_index
            proxy = IPPool.ip_list[proxy_index]
            self.proxy = proxy
            proxy_server = proxy.proxy
            if proxy_server.find('://') < 0:
                proxy_server = 'http://' + proxy_server
            self.print_d('使用代理：%s' % proxy_server)
            chrome_options.add_argument("--proxy-server=" + proxy_server)
        else:
            self.print_d('不使用代理服务') 

        self.driver = webdriver.Chrome(options=chrome_options)
        self.print_d('新建窗口-已获取到Chrome-准备打开页面')

        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                                   Object.defineProperty(navigator, 'webdriver', {
                                     get: () => undefined
                                   })
                                    // overwrite the `languages` property to use a custom getter
                                    Object.defineProperty(navigator, "languages", {
                                      get: function() {
                                        return ["zh-CN","zh","zh-TW","en-US","en"];
                                      }
                                    });

                                    // Overwrite the `plugins` property to use a custom getter.
                                    Object.defineProperty(navigator, 'plugins', {
                                      get: () => [1, 2, 3, 4, 5],
                                    });

                                    // Pass the Webdriver test
                                    Object.defineProperty(navigator, 'webdriver', {
                                      get: () => false,
                                    });


                                    // Pass the Chrome Test.
                                    // We can mock this in as much depth as we need for the test.
                                    window.navigator.chrome = {
                                      runtime: {},
                                      // etc.
                                    };

                                    // Pass the Permissions Test.
                                    const originalQuery = window.navigator.permissions.query;
                                    window.navigator.permissions.query = (parameters) => (
                                      parameters.name === 'notifications' ?
                                        Promise.resolve({ state: Notification.permission }) :
                                        originalQuery(parameters)
                                    );
                                 """
        })

        self.open_and_init()

    def is_use_proxy(self):
        return self.config.US_PROXY_SERVER

    def open_and_init(self):
        self.print_d('新建窗口-打开页面-页面加载中')

        try:
            self.driver.get(self.config.OPEN_URL);
        except TimeoutException as te:
            self.print_d(te)
            self.quit();

        self.print_d('新建窗口-打开页面-页面加载完成')

        if self.order_no:
            self.sendStatus(self.order_no, Status.o000)

        driver_process = psutil.Process(self.driver.service.process.pid)
        if driver_process:
            self.chrome_driver_process = driver_process

        children_list = driver_process.children()
        if children_list:
            self.chrome_process = children_list[0]

        #初始化时先检查控件是否加载成功
        self.is_open = False
        open_wait_index = 0

        while open_wait_index < self.config.OPEN_TIME_OUT:
            open_wait_index = open_wait_index + 1
            self.print_d('新建窗口-页面元素加载中-等待(%d)' % open_wait_index)
            self.sleep(1)
            try:
                field_input_user_name = self.driver.find_element_by_id("userName")
                field_input_password = self.driver.find_element_by_id("password")
                field_btn_login = self.driver.find_element_by_id("loginBtn")
            except NoSuchElementException as msg:
                pass
            else:
                self.is_open = True
                break

        if (self.is_open):
            self.print_d('新建窗口-页面加载完成')
            self.open_code = Status.o001['actionCode']
            self.print_d('页面打开延迟-总共等待(%d)' % open_wait_index)

            if self.order_no:
                return self.sendStatus(self.order_no, Status.o001)
        else:
            self.print_d('新建窗口-页面加载异常')
            self.quit();
            return self.sendStatus(self.order_no, Status.o002)

    def get_tranfer_list_status(self):
        return self.tranfer_list_status;

    def to_bank(self, bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.Kasikorn[bank]
        except Exception:
            return False
        if (to_bank is not None):
            self.t_to_bank = to_bank
            return True

    #输入用户名并且点击 login
    def back_input_name(self, userName):
        # 无动作
        pass

    #输入用户名
    def input_user_name(self, user_name = None):

        self.sendStatus(self.order_no, Status.l108);
        self.print_d('开始输入用户名')

        # 用户名输入框
        try:
            field_input_user_name = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "userName")))
        except Exception:
            self.print_d('没有找到用户名输入')
            return self.sendStatus(self.order_no, Status.l109);

        if user_name is not None :
            field_input_user_name.clear();
            field_input_user_name.send_keys(user_name);
            self.print_d("输入用户名成功");

        return self.sendStatus(self.order_no, Status.l110);

    # 输入密码
    def input_user_psw(self, psw = None):

        self.sendStatus(self.order_no, Status.l120);
        self.print_d('开始输入密码')

        try:
            field_input_password = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "password")))
        except Exception:
            self.print_d('没有找到密码输入')
            return self.sendStatus(self.order_no, Status.l121);

        if psw is not None :
            field_input_password.send_keys(psw);
            self.print_d("输入密码成功");

        return self.sendStatus(self.order_no, Status.l122);

    # 图形验证码
    def captcha_base64(self):

        # 验证码刷新按钮
        # try:
        #     field_btn_refresh_captcha = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img[src^='resources/themes/themeOne/images/icons/login/icoRefresh.png']")))
        # except Exception:
        #     self.print_d('没有找到刷新登陆验证码按钮')

        # # 刷新验证码
        # self.print_d("点击刷新登陆验证码按钮")
        # field_btn_refresh_captcha.click()

        # 是否弹出图形验证码
        captcha_base64 = ''

        try:
            field_img_captcha = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "captchaImg")))
        except Exception:
            self.print_d('无需输入图形验证码')
        else:
            # 保存验证码图片
            captcha_path = self.save_captcha(field_img_captcha)
            if (captcha_path is None):
                self.print_d('保存登陆验证码失败')

        return self.img_base64(captcha_path)

    # 输入验证码
    def input_captcha(self, captcha = None):

        self.sendStatus(self.order_no, Status.l151);
        self.print_d('开始输入验证码')

        try:
            field_input_captcha = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "captcha")))
        except Exception:
            self.print_d('没有找到验证码输入')
            return self.sendStatus(self.order_no, Status.l152);

        if captcha is not None :
            field_input_captcha.send_keys(captcha);
            self.print_d("输入验证码成功");

        return self.sendStatus(self.order_no, Status.l153);

    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        self.print_d('此银行无需查找密码是否可以输入');
        return self.sendStatus(self.order_no, Status.l120);

    # 点击登陆
    def handle_login(self):

        self.print_d('开始点击登陆按钮')

        try:
            field_btn_login = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        except Exception:
            self.print_d('没有找到登陆按钮')
            return self.sendStatus(self.order_no, Status.l131);

        # field_btn_login.click()
        self.driver.execute_script("arguments[0].click();", field_btn_login)
        self.print_d("点击登陆按钮");

        # 判断是否登陆成功
        try:
            field_frame = WebDriverWait(self.driver, 5).until_not(EC.visibility_of_element_located((By.ID, 'ssoIFrame1')))
        except Exception as m:
            self.print_d('登录成功，到用户默认主页');
            self.tranfer_list_status = 2
            return self.sendStatus(self.order_no, Status.l130);

        # self.driver.switch_to.default_content()

        # 捕获登陆失败原因
        try:
            field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "errorText")))
        except Exception:
            self.print_d('登陆失败，未捕获到错误原因');
            return self.sendStatus(self.order_no, Status.l131);

        try:
            message = field_div_error.find_element_by_tag_name("div").get_attribute("innerHTML");
            message = re.sub('<[^>]+>', '', message)
            message = message.replace('&nbsp;', '')
        except Exception:
            message = 'unknown error'

        self.print_d('登陆失败-%s' % message);

        res = self.sendStatus(self.order_no, Status.l132);
        res['actionMsg'] = message;
        result = self.sendStatus(self.order_no, res);

        return result

    #输入密码并提交
    def input_psw_and_submit(self, userName, psw, captcha = None):

        self.sendStatus(self.order_no, Status.l120);
        self.print_d('开始输入账号密码')

        # 用户名
        result = self.input_user_name(userName);
        if (result['actionCode'] != Status.l110['actionCode']):
            return result

        # 密码
        result = self.input_user_psw(psw)
        if (result['actionCode'] != Status.l122['actionCode']):
            return result

        # 验证码
        if (captcha is not None and captcha is not ''):
            result = self.input_captcha(captcha)
            if (result['actionCode'] != Status.l153['actionCode']):
                return result

        # 登陆
        result = self.handle_login()
        if (result['actionCode'] != Status.l130['actionCode']):
            return result

        self.print_d('登陆成功')
        return self.sendStatus(self.order_no, Status.l130);

    #登录
    def login(self) :
        self.print_d('此功能未实现'); 
        pass;

    def account_list(self):

        self.sendStatus(self.order_no, Status.t200);
        self.print_d('开始跳转至账户管理页')

        account_list = []

        self.driver.switch_to.default_content()

        try:
            field_frame = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'ssoIFrame1')))
        except Exception as m:
            self.print_d('ssoIFrame1-页面加载异常-%s' % m)
            return account_list
        else:
            self.print_d('切换frame-ssoIFrame1')
            self.driver.switch_to.frame(field_frame)

        # Account Summary页
        try:
            field_a_account_summary = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/retail/cashmanagement/inquiry/AccountSummary.do?action=list_domain2']")))
        except Exception:
            self.print_d('没有找到跳转至Account Summary的A标签')
            return account_list;

        self.print_d("开始获取付款账户信息")
        self.driver.execute_script("arguments[0].click();", field_a_account_summary)

        # 账户信息
        try:
            field_tbody_account = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//td[@class='table2_center']/../..")))
            field_tr_account = field_tbody_account.find_elements_by_tag_name("tr")
        except Exception:
            self.print_d('没有找到付款账户信息')
            self.sendStatus(self.order_no, Status.t212);
            return account_list

        if (len(field_tr_account) > 0):
            for tr in field_tr_account:
                field_td_account = tr.find_elements_by_tag_name("td")
                if (len(field_td_account) < 3 or field_td_account[0].text.find("-") < 0):
                    continue;
                account_num = field_td_account[0].text
                bal = field_td_account[3].text

                account = {};
                account.update({"accountName": account_num, "accountNumber": account_num, "currency": 'THB', "balances": bal})
                account_list.append(account);

        return account_list;

    # 到账户的转账列表页
    def goto_account_transfer(self, accountNum):
        self.print_d('此功能未实现');
        pass;

    # 到转账页
    def goto_transfer(self):

        self.sendStatus(self.order_no, Status.t209);
        self.print_d('开始跳转至手机付款页面')

        self.driver.switch_to.default_content()
     
        try:
            field_frame = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, 'ssoIFrame1')))
        except Exception as m:
            self.print_d('ssoIFrame1-页面加载异常-%s' % m)
            self.sendStatus(self.order_no, Status.t209);
        else:
            self.print_d('切换frame-ssoIFrame1')
            self.driver.switch_to.frame(field_frame)

        # PromptPay Funds Transfer页
        try:
            field_a_promptpay = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/retail/cashmanagement/PromptPayTransfer.do']")))
        except Exception:
            self.print_d('没有找到跳转至PromptPay Funds Transfer的A标签')
            self.sendStatus(self.order_no, Status.t209);

        try:
            self.driver.execute_script("arguments[0].click();", field_a_promptpay)
            self.print_d('跳转至手机付款页面成功')
            self.sendStatus(self.order_no, Status.t210);
            return True
        except Exception:
            self.print_d('跳转至手机付款页面失败')
            self.sendStatus(self.order_no, Status.t209);

        return False

    # 选择转出的账号
    def select_tranfer_info(self,info):

        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.sendStatus(self.order_no, Status.t211);
        self.print_d('开始处理付款方信息')

        account_number = info['accountNumber']

        # 选择付款方下拉按钮
        try:
            field_select_account = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, 'fromAccount')))
        except Exception:
            self.print_d('没有找到付款方下拉菜单')
            return self.sendStatus(self.order_no, Status.t243);

        # 选择付款方
        option_item = field_select_account.find_elements_by_tag_name("option")
        option_len = len(option_item)
        index = 0 
        select_index = 0     # 下标为0的是默认项 ---- Please Select ----

        while index < option_len:
            option_val = option_item[index].get_attribute("innerHTML")

            # 下拉菜单中出现付款卡号
            if option_val.find(account_number) >= 0:
                select_index = index

            index += 1;

        # 选择下拉菜单
        try:
            Select(field_select_account).select_by_index(select_index)
        except Exception as m:
            self.print_d('选择付款元素异常');
            self.action_code = Status.t243['actionCode'];
            result = self.sendStatus(self.order_no, Status.t243);
        else:
            self.print_d('选择付款元素成功');
            self.action_code = Status.t230['actionCode'];
            result = self.sendStatus(self.order_no, Status.t230);

        return result

    # 手机号码快捷转账
    def transfer_mobile(self, info):

        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        transferRecipientName = info['recipientName']

        self.sendStatus(self.order_no, Status.t220);
        self.print_d('开始进行手机快捷转账')

        # Transfer To 下拉框
        try:
            field_select_paytype = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, "promptPayType")))
        except Exception:
            self.print_d('没有找到收款方快捷选择按钮')
            return self.sendStatus(self.order_no, Status.t221);

        Select(field_select_paytype).select_by_value('02')
        self.print_d('点击选择快捷方式类型，选择Mobile No')

        # 手机号码输入框
        try:
            field_input_promptpayid = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, "promptPayId")))
        except Exception:
            self.print_d('没有找到收款方手机号码输入框')
            return self.sendStatus(self.order_no, Status.t221);

        # 输入手机号码
        field_input_promptpayid.clear()
        field_input_promptpayid.send_keys(transferAccount);
        self.print_d("输入收款方手机号码成功");
        self.sendStatus(self.order_no, Status.t240);
        
        # 收款金额输入框
        try:
            field_input_amount = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, "creditAmount")))
        except Exception:
            self.print_d('没有找到收款金额输入框')
            return self.sendStatus(self.order_no, Status.t243);

        # 输入收款金额
        field_input_amount.clear()
        field_input_amount.send_keys(transferAmount);
        self.print_d("输入收款金额成功");
        self.sendStatus(self.order_no, Status.t241);

        # 转账备注输入框
        try:
            field_input_note = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, "details")))
        except Exception:
            self.print_d('没有找到转账备注输入框')
            return self.sendStatus(self.order_no, Status.t243);

        # 输入转账备注
        field_input_note.clear()
        field_input_note.send_keys(transferReference);
        self.print_d("输入转账备注成功");
        self.sendStatus(self.order_no, Status.t242);

        # 下一步按钮
        try:
            field_btn_next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "btnNext")))
        except Exception:
            self.print_d('没有找到转账信息下一步按钮')
            return self.sendStatus(self.order_no, Status.t243);

        # 点击进行下一步，到OTP页面
        field_btn_next.click();
        self.print_d("提交转账信息，到OTP页面");
        return self.sendStatus(self.order_no, Status.t244);

    # 输入转入账号、转账金额、备注等信息并提交
    def input_transfer_info(self, info):

        # 判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.print_d('开始处理收款方信息')

        # 手机号码快捷转账
        result = self.transfer_mobile(info)
        if (result['actionCode'] != Status.t244['actionCode']):
            return result

        # 获取OTP编号
        try:
            field_span_otp_refno = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//b[contains(text(), 'Ref. Code')]/../../following-sibling::td")))
        except Exception:
            self.print_d("未发现OTP标识");
            field_span_otp_refno = None

        if (field_span_otp_refno is None):
            # 捕获失败原因
            try:
                field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//td[@class='body']")))
            except Exception:
                self.print_d('转账失败，未捕获到错误原因');
                return self.sendStatus(self.order_no, Status.t261);

            message = field_div_error.get_attribute("innerHTML");
            message = message.replace('&gt;', '>')

            res = self.sendStatus(self.order_no,Status.t261);
            res['actionMsg'] = message;

            self.print_d('转账失败-%s' % message);
            result = self.sendStatus(self.order_no, res);
        else:
            otp_refno = field_span_otp_refno.get_attribute('innerHTML');

            self.print_d("加载OTP页面成功，自动触发发送OTP，OTP标识-%s" % otp_refno);
            result = self.sendStatus(self.order_no, Status.v320);
            result.update({'refno':otp_refno});

        return result;

    # 输入短信验证码
    def input_sms_code(self, code):
 
        # 判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.sendStatus(self.order_no, Status.v321);
        self.print_d('开始输入OTP')

        # OTP输入框
        try:
            field_input_transfer_otp = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.NAME, "secondaryPassword")))
        except Exception:
            self.print_d('没有找到转账OTP输入框')
            return self.sendStatus(self.order_no, Status.v322);

        # 获取OTP编号
        try:
            field_span_otp_refno = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//b[contains(text(), 'Ref. Code')]/../../following-sibling::td")))
        except Exception:
            self.print_d("没有找到转账OTP标识");
            return self.sendStatus(self.order_no, Status.v322);
        
        otp_refno = field_span_otp_refno.get_attribute('innerHTML');
        self.print_d('输入OTP（%s）- %s' % (otp_refno, code))
        field_input_transfer_otp.clear();
        field_input_transfer_otp.send_keys(code);

        # 提交转账
        self.print_d('开始提交OTP')

        # 提交OTP按钮
        try:
            locator = (By.XPATH, "//input[@src='/retailstatic/images/button/Confirm_en.gif']");
            field_btn_commit_otp = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
        except Exception:
            self.print_d("没有找到提交OTP按钮");
            return self.sendStatus(self.order_no, Status.v331);

        # 提交OTP
        field_btn_commit_otp.click()
        self.print_d("点击提交OTP");

        # 判断是否到结束页面
        try:
            locator = (By.CSS_SELECTOR, "img[src^='/retailstatic/images/button/bt_print.gif']");
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
        except Exception:
            # 捕获失败原因 1
            try:
                locator = (By.XPATH, "//input[@name='secondaryPassword']/..");
                field_td_error = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                field_message = field_td_error.find_element_by_tag_name("font");
            except Exception:
                self.print_d('转账失败，未捕获到错误原因 1');
                return self.sendStatus(self.order_no, Status.v339);
                # # 捕获失败原因 2
                # try:
                #     locator = (By.CSS_SELECTOR, "td[text-align='center'][font-weight='bold']");
                #     field_td_error = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(locator))
                #     field_message = field_td_error;
                # except Exception:
                #     self.print_d('转账失败，未捕获到错误原因 2');
                #     self.sendStatus(self.order_no, Status.v339);

            try:
                message = field_message.get_attribute("innerHTML");
            except Exception:
                message = 'unknown error'

            # 验证码错误提示，可重试，返回341，其他错误返回339
            # Sorry, Incorrect OTP (4005)
            if (message.find("Invalid password") >= 0):
                res = self.sendStatus(self.order_no, Status.v341);
            else:
                res = self.sendStatus(self.order_no, Status.v339);
                
            self.print_d('转账失败-%s' % message);
            res['actionMsg'] = message;
            return self.sendStatus(self.order_no, res);

        # 结束页面判断
        # 文本标识是否存在
        # Your transaction has completed.
        try:
            field_reulst = self.driver.find_element_by_xpath("//b[contains(text(), 'Transaction Result')]/../following-sibling::td").get_attribute("innerHTML").lstrip().rstrip()
        except Exception:
            self.print_d('转账失败，未捕获到Result');
            return self.sendStatus(self.order_no, Status.v339);

        if 'Your transaction has completed' in field_reulst:
            self.print_d('提交OTP成功');
            
            # amount
            try:
                amount = self.driver.find_element_by_xpath("//b[contains(text(), 'Amount (THB)')]/../following-sibling::td").get_attribute("innerHTML").lstrip().rstrip()
            except NoSuchElementException as m:
                amount = ""

            # note
            try:
                note = self.driver.find_element_by_xpath("//b[contains(text(), 'Note')]/../following-sibling::td").get_attribute("innerHTML").lstrip().rstrip()
            except NoSuchElementException as m:
                note = ""

            result = self.sendStatus(self.order_no, Status.v340);
            result.update({'reference':note});
            result.update({'orderMsg':field_reulst});
            result.update({'amount':self.format_amount(amount)});
            self.print_d('转账成功')
            return result
        else:
            self.print_d('转账失败-%s' % field_reulst);
            res = self.sendStatus(self.order_no, Status.v345);
            res['actionMsg'] = field_reulst;
            result = self.sendStatus(self.order_no, res);

        return result

    def resend_sms_code(self):
        self.print_d('此功能未实现');
        pass;

    # 登出
    def logout(self):

        self.sendStatus(self.order_no, Status.o400);
        self.print_d('开始登出')

        self.driver.switch_to.default_content()

        try:
            field_btn_logout = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'Logout')]")))
        except Exception:
            self.print_d('没有找到登出按钮')
            return self.sendStatus(self.order_no, Status.o401);

        field_btn_logout.click()

        # confirm 对话框
        dialog_box = self.driver.switch_to_alert()
        dialog_box.accept()

        self.sleep(1)
        self.quit();
        self.print_d("登出成功");

        return self.sendStatus(self.order_no, Status.o402);

    def check_session(self,auto_click):
        self.print_d('此功能未实现');
        pass;

    # 判断页面是否超时
    def is_session_timeout(self, auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception as we:
            self.quit()
            return True

        self.print_d(self.order_no + "--" + current_url)

        if (current_url.find("LogOutLostSession.jsp") >= 0):
            if (auto_quit):
                self.quit();
            return True;
        else:
            return False;

    # 继续回到转账
    def  go_transfer_continue(self):
        result = Status.t209;
        self.print_d("继续回到转账");

        #这个银行是跟直接到转账页面一样的，所以调用一下就可以
        is_tran = self.goto_transfer();
        if (is_tran):
            result = Status.t210;
        return result

    #转账账号不存在，需要添加
    # def add_account(self,info):
    #     result = Status.t235
    #     is_add_account_page = False;
    #     accountName = info['accountName'];
    #     accountNumber = info['accountNumber'];
    #     #判断当前页面
    #     try:
    #         h1 = self.driver.find_element_by_tag_name("h1");
    #         # Create New Other Account
    #         if (h1.text.find("Create") > -1 ):
    #             is_add_account_page = True;
    #     except Exception:
    #         pass
    #     if(accountName is None):
    #         accountName = accountNumber
    #     if( is_add_account_page == False):
    #         try:
    #             locator2 = (By.CLASS_NAME, "acclink");
    #             WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(locator2))
    #         except Exception:
    #             self.print_d('到增加帐号异常');
    #             result = Status.t236;
    #             return result;
    #         acclinks = self.driver.find_elements_by_class_name("acclink")
    #         if(len(acclinks) < 1):
    #             result = Status.t236;
    #             return result;
    #         add_other_account = acclinks[1]
    #         add_other_account.click()
    #         self.print_d('Create New Other Account');
    #     try:
    #         # 是否在添加账号页面
    #         locator = (By.CSS_SELECTOR, "select[name^='bankID']")
    #         WebDriverWait(self.driver, 15, 0.5).until(EC.visibility_of_element_located(locator))
    #     except Exception:
    #         self.print_d('可能没在添加转账页')
    #         return result
    #     self.print_d("找到选择银行类型 select")
    #     # transferAccount, transferAmount, transferReference
    #     # 此时在  Create New Other Account
    #     #转账银行类型
    #     selector = Select(self.driver.find_element_by_css_selector("select[name^='bankID']"))

    #     self.print_d(self.t_to_bank)
    #     selector.select_by_index(self.t_to_bank)  # 通过index 进行选择
    #     time.sleep(0.3)
    #     try:
    #         # 转账帐号
    #         account_number_input = self.driver.find_element_by_css_selector("input[name^='accountNumber']");
    #         account_number_input.clear();
    #         account_number_input.send_keys(accountNumber);
    #         time.sleep(0.3)
    #         # 帐号 Name
    #         account_name_input = self.driver.find_element_by_css_selector("input[name^='accountName']");
    #         account_name_input.clear();
    #         account_name_input.send_keys(accountName);
    #         time.sleep(0.3);
    #     except Exception:
    #         self.print_d('新建帐号输入异常')
    #         result = self.sendStatus(self.order_no, Status.t243);
    #         return result
    #     try:
    #         #先提交保存帐号
    #         image = self.driver.find_element_by_css_selector("input[type^='image']");
    #         image.click();
    #     except Exception :
    #         self.print_d("提交按键没找到")
    #         # 执行 js
    #         js_click = "$(\"input[type='image']\").click()"
    #         self.driver.execute_script(js_click)
    #     self.print_d("新建帐号提交");
    #     # 查找结果
    #     is_success = False;
    #     wait_index = 1;
    #     while wait_index < 8:
    #         h1 = None;
    #         try:
    #             h1 = self.driver.find_element_by_tag_name("h1")
    #             # 错误时的内容：
    #         except NoSuchElementException:
    #             pass
    #         if (h1 is not None):
    #             self.print_d(h1.text);
    #             self.print_d("a");
    #             if (h1.text.find("Review") < 0):
    #                 self.print_d("b");
    #                 # 还在输入转账信息页 Create New Other Account
    #                 # 判断错误提示
    #                 try:
    #                     red_font_list = self.driver.find_elements_by_css_selector("font[color='red']");
    #                 except NoSuchElementException:
    #                     self.print_d("没找到错误提示");
    #                 if (len(red_font_list) > 0):
    #                     for font in red_font_list:
    #                         if (len(font.text) > 5):
    #                             self.print_d("新建帐号提交异常");
    #                             self.print_d(font.text);
    #                             result = self.sendStatus(self.order_no, Status.t236)
    #                             result['actionMsg'] = font.text;
    #                             result['bankMsg'] = font.text;
    #                             is_success = False;
    #                             wait_index = 10;
    #                             break;
    #             else:
    #                 self.print_d("c");
    #                 try:
    #                     self.driver.find_element_by_css_selector("input[name^='secondPassword']");
    #                 except  NoSuchElementException:
    #                     self.print_d('没找到otp输入。');
    #                 else:
    #                     self.print_d("d");
    #                     is_success = True;
    #                     result = self.sendStatus(self.order_no, Status.t291);
    #                     wait_index = 10;
    #                     break;
    #         time.sleep(0.5)
    #         wait_index = wait_index + 1;

    #     self.action_code = result['actionCode'];
    #     self.print_d(is_success);
    #     if (is_success):
    #         # 短信识别码 .sec_body
    #         refno = "";
    #         try:
    #             sec_body_list = self.driver.find_elements_by_class_name("sec_body");
    #             if len(sec_body_list) > 2:
    #                 refno = sec_body_list[1].text;
    #         except Exception:
    #             pass;
    #         result["refno"] = refno;
    #     #截图确认短信有没有发送
    #     self.screen(self.order_no + "is_send_sms");
    #     return result;

    # def get_account_name_by_num(self,accountNum):
    #     if ( len(self.accountList) > 0):
    #         for account in self.accountList:
    #             if(account['accountNumber'] == accountNum):
    #                 return account['accountName']
    #     return None



    #输入新建帐号验证码
    # def input_add_sms_code (self,code):
    #     self.print_d("input_add_sms_code")
    #     result = self.sendStatus(self.order_no, Status.t292);
    #     locator2 = (By.CSS_SELECTOR, "input[name^='secondPassword']")
    #     try:
    #         WebDriverWait(self.driver, 6, 0.5).until(EC.element_to_be_clickable(locator2))
    #     except Exception:
    #         self.print_d(result['actionMsg']);
    #         return result
    #     secondPassword = self.driver.find_element_by_css_selector("input[name^='secondPassword']");
    #     secondPassword.clear();
    #     secondPassword.send_keys(code);
    #     btnConfirm = self.driver.find_element_by_css_selector("input[name^='btnConfirm']");
    #     btnConfirm.click();
    #     #等待一秒让页面加载，以免被 页面上显示的上次结果 混淆
    #     time.sleep(1);
    #     #查找结果
    #     is_success = False;
    #     wait_index = 1;
    #     while wait_index < 8 :
    #         h1 = None;
    #         try:
    #             h1 = self.driver.find_element_by_tag_name("h1")
    #             # 错误时的内容： Create New Other Account - Review
    #         except NoSuchElementException:
    #             pass
    #         if(h1 is not None):
    #             if(h1.text.find("Review") > -1):
    #                 #还在输入验证码页
    #                 #判断错误提示
    #                 try:
    #                     sec_body = self.driver.find_element_by_xpath("//input[@name='secondPassword']/..");
    #                     font = sec_body.find_element_by_tag_name("font");
    #                 except NoSuchElementException:
    #                     self.print_d("没找到错误提示");
    #                     #查找 session 过期
    #                     try:
    #                         font_red = self.driver.find_element_by_tag_name("font");
    #                         if (font_red.text.find("unexpected") > -1 or font_red.text.find("session") > -1):
    #                             wait_index = 10;
    #                             result['actionMsg'] = font_red.text;
    #                             result['bankMsg'] = font_red.text;

    #                             result = self.sendStatus(self.order_no, Status.t292);
    #                             is_success = False;
    #                             break;
    #                     except NoSuchElementException as e:
    #                         pass
    #                 else:
    #                     if ((font is not None) and len(font.text) > 5):
    #                         result['actionMsg'] = font.text;
    #                         result['bankMsg'] = font.text;
    #                         result = self.sendStatus(self.order_no, Status.t292);
    #                         is_success = False;
    #                         wait_index = 10
    #                         break;

    #             elif(h1.text.find("Transfer") > -1 or h1.text.find("Transaction") > -1):
    #                 is_success = True;
    #         time.sleep(0.5)
    #         wait_index = wait_index+1
    #     if(is_success == True):
    #         self.is_add_account = True;
    #         result = self.sendStatus(self.order_no, Status.t293);
    #     else:
    #         self.screen();
    #     return result

    ##输入验证码
    # def input_sms_code (self,code):
    #     self.print_d("输入验证码")
    #     self.action_code = Status.v321['actionCode'];
    #     result = self.sendStatus(self.order_no,Status.v321);
    #     #判断页面超时
    #     if ( self.is_session_timeout(True) ):
    #         self.action_code = Status.o410['actionCode'];
    #         result = self.sendStatus(self.order_no, Status.o410);
    #         return
    #     try:
    #         otp = self.driver.find_element_by_css_selector("input[name^='secondaryPassword']");
    #     except  NoSuchElementException as msg:
    #         self.print_d('查找 otp输入 异常。');
    #         self.action_code = Status.v322['actionCode'];
    #         return  self.sendStatus(self.order_no, Status.v322);
    #     else:
    #         self.print_d("已找到 otp")

    #     # code = input("请输入收到的短信验证码:")
    #     self.print_d("验证码:%s"%code);
    #     try:
    #         otp.clear();
    #     except Exception as e:
    #         self.print_d('fail清空输入框')
    #     # 输入验证吗
    #     otp.send_keys(code);
    #     self.action_code = Status.v330['actionCode'];
    #     result = self.sendStatus(self.order_no, Status.v330);
    #     time.sleep(1);
    #     try:
    #         # confirmBtn = self.driver.find_element_by_css_selector("input[name^='btnSubmit']");
    #         confirmBtn = self.driver.find_element_by_css_selector("input[src^='/retailstatic/images/button/Confirm_en.gif']");
    #     except  NoSuchElementException as msg:
    #         print('查找btnSubmit异常 %s'%msg);
    #         return self.sendStatus(self.order_no, Status.v331);

    #     self.print_d('找到 btnSubmit');
    #     # 确认
    #     confirmBtn.click();
    #     self.action_code = Status.v332['actionCode'];
    #     result = self.sendStatus(self.order_no, Status.v332);
    #     time.sleep(1);
    #     # 判断结果和异常





    #     #判断转账结果
    #     self.print_d('$$$$$$加载完成$$$$$')
    #     is_success = False;
    #     wait_index = 0;
    #     error_text = "";
    #     while wait_index < 8:
    #         h1 = None;
    #         try:
    #             h1 = self.driver.find_element_by_tag_name("h1")
    #             # 成功时的内容： Inter-bank Funds Transfer - Transaction Result
    #         except NoSuchElementException:
    #             pass
    #         if (h1 is not None):
    #             if (h1.text.find("Transaction") > -1 and h1.text.find("Result") > -1):
    #                 # 成功
    #                 is_success = True;
    #                 result = self.sendStatus(self.order_no, Status.v340);
    #                 result['orderMsg'] = 'Successful';
    #                 result['amount'] = '';
    #                 result['reference'] = '';
    #                 try:
    #                     FundTransferForm = self.driver.find_element_by_name("FundTransferForm");
    #                     tr_list = FundTransferForm.find_elements_by_tag_name("tr");
    #                     for tr in tr_list:
    #                         if(tr is None or len(tr.text) < 1):
    #                             continue;
    #                         self.print_d(tr.text);
    #                         if (tr.text.find("Amount") > -1):
    #                             td_list = tr.find_elements_by_tag_name("td");
    #                             if (len(td_list) > 1):
    #                                 amount_text = td_list[1].text;
    #                                 result['amount'] = amount_text.strip();
    #                         elif (tr.text.find("Note") > -1):
    #                             td_list = tr.find_elements_by_tag_name("td");
    #                             if (len(td_list) > 1):
    #                                 reference = td_list[1].text;
    #                                 result['reference'] = reference.strip()
    #                                 # orderMsg =  wordWraps[3].text
    #                 except Exception as e :
    #                     self.print_d("没找到转账信息");
    #                     self.print_d(str(e));
    #                     # 查找 session 过期
    #                     try:
    #                         font_red = self.driver.find_element_by_tag_name("font");
    #                         if (font_red.text.find("unexpected") > -1 or font_red.text.find("session") > -1):
    #                             wait_index = 10;
    #                             result['actionMsg'] = font_red.text;
    #                             result['bankMsg'] = font_red.text;
    #                             result = self.sendStatus(self.order_no, Status.o410);
    #                             is_success = False;
    #                             break;
    #                     except NoSuchElementException as e:
    #                         pass
    #             else:
    #                 # 失败
    #                 # 验证码错误等判断
    #                 is_success = False;
    #                 result = Status.v341;
    #                 try:
    #                     sec_body = self.driver.find_element_by_xpath("//input[@name='secondaryPassword']/..");
    #                     font = sec_body.find_element_by_tag_name("font");
    #                     self.print_d(font.text);
    #                     if(len(font.text) >5):
    #                         error_text = font.text;
    #                         if(error_text.find("Invalid") > -1):
    #                             wait_index = 999;
    #                             break;
    #                 except Exception as e:
    #                     self.print_d(str(e))
    #         #session 过期和 unexpected判断
    #         try:
    #             font = self.driver.find_element_by_tag_name("font")
    #         except NoSuchElementException :
    #             pass
    #         else:
    #             if(font.text.find("session") > -1):
    #                 #需要重新登录 TODO
    #                 is_submit = False;
    #                 result = Status.o410;
    #                 error_text = font.text;
    #                 wait_index = 999;
    #                 break;
    #             elif(font.text.find("unexpected") > -1):
    #                 is_submit = False;
    #                 result = Status.o404;
    #                 error_text = font.text;
    #                 wait_index = 999;
    #                 break;
    #         time.sleep(0.5)
    #         wait_index = wait_index + 1
    #     if (is_success):
    #         self.print_d("自动补齐")
    #         if(len(result['amount']) <1):
    #             result['amount'] = self.tranfer_info['amount'];
    #         if (len(result['reference']) < 1):
    #             result['reference'] = self.tranfer_info['reference'];
    #     else:
    #         result['actionMsg'] = error_text;
    #         result['bankMsg'] = error_text;
    #     return result
    # # exit('转账结束');