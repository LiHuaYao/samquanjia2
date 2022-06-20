import time
from datetime import datetime

import psutil
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,WebDriverException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from dao.Status import Status
from model.BankType import BankType
from model.IPPool import IPPool
from plus.ChromeOptions import ChromeOptions
from plus.Personification import Personification
from config import Config
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains

class KTB(Personification) :

    def __init__(self, proxy_index = None, order_no = None):
        Personification.__init__(self)

        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no

        self.tranfer_list_status = 0;
        self.config = Config.KTB
        self.status_path = self.config.STATUS_PATH

        self.print_d('准备打开页面')

        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=ktbnetbank")

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

        # driver = webself.driver.Chrome()
        self.driver.maximize_window()  # 最大化浏览器
        # self.driver.implicitly_wait(8)  # 设置隐式时间等待
        # print("chrome.")

        self.open_and_init()

        # self.sleep(5)
        # print("get.")
        # self.sendStatus(self.order_no,Status.o000);

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
                field_input_user_id = self.driver.find_element_by_id("userId")
                field_input_password = self.driver.find_element_by_id("password")
                field_input_captcha = self.driver.find_element_by_id("id_ImageCode")
                field_btn_login = self.driver.find_element_by_id("signIn")
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
            to_bank = BankType.ToBank.ktbnetbank[bank]
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

        # 判断是否有错误提示框，有则先关闭
        try:
            field_btn_error_close = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "errorCloseButton")))
        except Exception:
            pass;
        else:
            self.print_d('找到错误提示框，先关闭')
            field_btn_error_close.click();

        # 用户名输入框
        try:
            field_input_user_id = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "userId")))
        except Exception:
            self.print_d('没有找到用户名输入')
            return self.sendStatus(self.order_no, Status.l109);

        if user_name is not None :
            field_input_user_id.clear();
            field_input_user_id.send_keys(user_name);
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

    # 输入验证码
    def input_captcha(self, captcha = None):

        self.sendStatus(self.order_no, Status.l151);
        self.print_d('开始输入验证码')

        try:
            field_input_captcha = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "id_ImageCode")))
        except Exception:
            self.print_d('没有找到验证码输入')
            return self.sendStatus(self.order_no, Status.l152);

        if captcha is not None :
            field_input_captcha.send_keys(captcha);
            self.print_d("输入验证码成功");

        return self.sendStatus(self.order_no, Status.l153);

    # 点击登陆
    def handle_login(self):

        self.print_d('开始点击登陆按钮')

        try:
            field_btn_login = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "signIn")))
        except Exception:
            self.print_d('没有找到登陆按钮')
            return self.sendStatus(self.order_no, Status.l131);

        # field_btn_login.click()
        self.driver.execute_script("arguments[0].click();", field_btn_login)
        self.print_d("点击登陆按钮");

        # 判断是否登陆成功
        try:
            WebDriverWait(self.driver, 5).until_not(EC.visibility_of_element_located((By.ID, "content")))
        except Exception:
            self.print_d('登录成功，到用户默认主页');
            self.tranfer_list_status = 2
            return self.sendStatus(self.order_no, Status.l130);

        # 捕获登陆失败原因
        try:
            field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "td_loginpage_errormessage")))
        except Exception:
            self.print_d('登陆失败，未捕获到错误原因');
            return self.sendStatus(self.order_no, Status.l131);

        try:
            message = field_div_error.find_element_by_tag_name("div").get_attribute("innerHTML");
        except Exception:
            message = 'unknown error'

        self.print_d('登陆失败-%s' % message);

        res = self.sendStatus(self.order_no, Status.l132);
        res['actionMsg'] = message;
        result = self.sendStatus(self.order_no, res);

        return result

    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        self.print_d('此银行无需查找密码是否可以输入');
        return self.sendStatus(self.order_no, Status.l120);

    #输入密码并提交
    def input_psw_and_submit(self, userName, psw, captcha):

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

    # 获取账户列表
    def account_list(self):

        self.sendStatus(self.order_no, Status.t200);
        self.print_d('开始跳转至付款账户页面')

        account_list = []

        # 跳转至手机快捷转账
        try:
            field_btn_transfer = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="main.jsp#transferpromptpay"]')))
        except Exception:
            self.print_d('没有找到同行转账按钮')
            self.sendStatus(self.order_no, Status.t221);
            return account_list

        self.print_d("点击跳转转账按钮");

        # 此处按钮已加载完，但是界面上还有loading遮罩
        # self.sleep(2)
        self.driver.execute_script("arguments[0].click();", field_btn_transfer)
        # field_btn_transfer.click()

        # 付款方信息，区域
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'divAccountFromList_SelectorContentPlaceholder')))
        except Exception:
            self.print_d('没有找到付款账户信息')
            self.sendStatus(self.order_no, Status.t231);
            return account_list

        self.sendStatus(self.order_no, Status.t210);
        self.print_d("开始获取付款账户信息")

        try:
            account_items = self.driver.find_elements_by_css_selector('div.FundBlockAccount.AccountItem')
            # account_items = WebDriverWait(self.driver, 10).until(EC.visibility_of_elements_located((By.CSS_SELECTOR, 'div.FundBlockAccount.AccountItem')))
        except Exception:
            self.print_d('获取付款账户信息异常')
            self.sendStatus(self.order_no, Status.t231);
            return account_list
            
        account_len = len(account_items)
        index = 0

        while index < account_len:
            account_name = account_items[index].find_element_by_xpath('.//table[@name="tableRowStyleMainTable"]/tbody/tr[2]//td[@class="Center-indicator"]/table/tbody/tr/td/table/tbody/tr/td/b').get_attribute("innerHTML").lstrip().rstrip()
            account_num = account_items[index].find_element_by_xpath('.//table[@name="tableRowStyleMainTable"]/tbody/tr[2]//td[@class="Center-indicator"]/table/tbody/tr[3]/td/table/tbody/tr/td[@class="contentblockleft normal"]').get_attribute("innerHTML").lstrip().rstrip().replace("-", "");
            curr_bal = account_items[index].find_element_by_xpath(
                './/table[@name="tableRowStyleMainTable"]/tbody/tr[2]//td[@class="Center-indicator"]/table/tbody/tr[3]/td/table/tbody/tr/td[@class="contentblockright normal"]').get_attribute(
                "innerHTML").lstrip().rstrip()
            curr_bal_list = curr_bal.split()

            account = {};
            account.update({"accountName": account_name, "accountNumber": account_num, "currency": curr_bal_list[1], "balances": curr_bal_list[0]})
            account_list.append(account);
            index += 1;

        return account_list;

    # 到转账页
    def goto_transfer(self):
        self.print_d('此银行无需实现转账页跳转');
        pass;

    # 选择转账信息
    def select_tranfer_info(self, info):

        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.sendStatus(self.order_no, Status.t211);
        self.print_d('开始处理付款方信息')

        account_number = info['accountNumber']

        # 付款方拖拽选择框
        try:
            field_div_account = WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located((By.ID, "divFundFrom_" + account_number)))
        except Exception:
            self.print_d('没有找到付款方拖拽选择框')
            return self.sendStatus(self.order_no, Status.t212);

        # 付款方拖拽目标框
        try:
            field_div_account_area = WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located((By.ID, "divAccountFromSelection")))
        except Exception:
            self.print_d('没有找到付款方拖拽目标框')
            return self.sendStatus(self.order_no, Status.t212);

        # 拖拽付款方
        try:
            action = ActionChains(self.driver)
            action.drag_and_drop(field_div_account, field_div_account_area)
            action.perform()
        except Exception:
            self.print_d('拖拽付款元素异常');
            result = self.sendStatus(self.order_no, Status.t231);
        else:
            self.print_d('拖拽付款元素成功');
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

        # 选择使用收款方式
        try:
            field_btn_choice_promptpay = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//label[@for='inputAnyIDNo']")))
        except Exception:
            self.print_d('没有找到收款方快捷选择按钮')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择快捷方式按钮，显示出快捷类型下拉框
        field_btn_choice_promptpay.click()
        self.print_d('点击选择快捷方式按钮，显示出快捷类型下拉框')

        # 选择使用快捷类型
        try:
            field_div_choice_type = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "selTypeAccount")))
        except Exception:
            self.print_d('没有找到收款方快捷类型按钮')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择快捷方式类型按钮，显示出快捷类型选项
        field_div_choice_type.click()
        self.print_d('点击选择快捷方式类型按钮，显示出快捷类型选项')

        # 判断选择框是否正常弹出
        try:
            field_div_type_list = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ktbdropdown_menu")))
        except Exception:
            self.print_d('没有找到收款方快捷类型列表')
            return self.sendStatus(self.order_no, Status.t221);

        self.sleep(1)

        # 选择使用 Mobile Number
        try:
            field_td_type_mobile = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//td[@datakey='MSISDN']")))
        except Exception:
            self.print_d('没有找到收款方手机快捷类型选项')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择选择使用MobileNumber
        field_td_type_mobile.click()
        self.print_d('点击选择选择使用MobileNumber')

        # 手机号码选择框
        try:
            field_input_promptpay = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txtFromAccount")))
        except Exception:
            self.print_d('没有找到收款方手机输入框')
            return self.sendStatus(self.order_no, Status.t243);

        # 输入手机号码
        field_input_promptpay.clear()
        field_input_promptpay.send_keys(transferAccount);
        self.print_d("输入收款方手机号码成功");
        self.sendStatus(self.order_no, Status.t240);

        # 收款金额输入框
        try:
            field_input_amount = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txtAmount")))
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
            field_input_note = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txtNote")))
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
            field_btn_next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "lnkAnyIDNextStep")))
        except Exception:
            self.print_d('没有找到转账信息下一步按钮')
            return self.sendStatus(self.order_no, Status.t243);

        # 点击进行下一步，到OTP页面
        field_btn_next.click();
        self.print_d("提交转账信息，到OTP页面");
        return self.sendStatus(self.order_no, Status.t244);

    # 输入转账方信息并到发送验证码
    def input_transfer_info(self, info):

        # 判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.print_d('开始处理收款方信息')

        # 手机号码快捷转账
        result = self.transfer_mobile(info)
        if (result['actionCode'] != Status.t244['actionCode']):
            return result

        # 发现有重复转账，无视，直接提交
        try:
            field_btn_transfer_repeat = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "lnkConfirmDup")))
        except Exception:
            self.print_d("未发现有未处理的重复转账");
        else:
            self.print_d("发现有未处理的重复转账，无视直接提交");
            field_btn_transfer_repeat.click()

        # 获取OTP编号
        try:
            field_span_otp_refno = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "lblRefNo")))
        except Exception:
            self.print_d("未发现OTP标识");
            field_span_otp_refno = None

        if (field_span_otp_refno is None):
            # 捕获失败原因
            try:
                field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "td_errorMessageContainer_errormessage")))
            except Exception:
                self.print_d('转账失败，未捕获到错误原因');
                return self.sendStatus(self.order_no, Status.t261);

            message = field_div_error.find_element_by_tag_name("div").get_attribute("innerHTML");
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

    # 图形验证码
    def captcha_base64(self):

        # 验证码刷新按钮
        try:
            field_btn_refresh_captcha = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img[src^='resources/themes/themeOne/images/icons/login/icoRefresh.png']")))
        except Exception:
            self.print_d('没有找到刷新登陆验证码按钮')

        # 刷新验证码
        self.print_d("点击刷新登陆验证码按钮")
        field_btn_refresh_captcha.click()

        # 获取验证码图片位置，截取保存
        try:
            field_img_captcha = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "imageCodeDisplayId")))
        except Exception:
            self.print_d('没有找到登陆验证码')

        # 保存验证码图片
        captcha_path = self.save_captcha(field_img_captcha)
        if (captcha_path is None):
            self.print_d('保存登陆验证码失败')

        # 英文界面按钮
        try:
            field_btn_change_language = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class^='eng']")))
        except Exception:
            self.print_d('没有找到刷新登陆验证码按钮')

        # 切换英文界面
        self.print_d("点击切换英文界面按钮")
        field_btn_change_language.click()

        return self.img_base64(captcha_path)

    # 输入短信验证码
    def input_sms_code(self, code):
 
        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.sendStatus(self.order_no, Status.v321);
        self.print_d('开始输入OTP')

        # OTP输入框
        try:
            field_input_transfer_otp = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txtTOP")))
        except Exception:
            self.print_d('没有找到转账OTP输入框')
            return self.sendStatus(self.order_no, Status.v322);

        # 获取OTP编号
        try:
            field_span_otp_refno = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "lblRefNo")))
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
            locator = (By.XPATH, '//div[@id="spStep2_ScrollContentPlaceHolder"]//div[@class="BoxFund"]/table/tbody/tr[3]/td//table[2]/tbody/tr/td/a');
            field_btn_commit_otp = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(locator))
        except Exception:
            self.print_d("没有找到提交OTP按钮");
            return self.sendStatus(self.order_no, Status.v331);

        # 提交OTP
        field_btn_commit_otp.click()
        self.print_d("点击提交OTP");

        is_commit = False

        # 判断是否提交OTP成功
        try:
            locator = (By.CSS_SELECTOR, "img[src^='resources/themes/themeOne/images/icons/icon_save.png']");
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
        except Exception:
            pass;
        else:
            is_commit = True

        if (is_commit):
            self.print_d('提交OTP成功');

            # 假设接下来是转账成功
            
            try:
                filed_table_item = self.driver.find_elements_by_xpath('//div[@id="spStep3_ScrollContentPlaceHolder"]//div[@class="BoxFund"]//table/tbody/tr[3]/td/table/tbody/tr')

                finish_len = len(filed_table_item)
                index = 0

                # 获取标题的index
                while index < finish_len:
                    key = filed_table_item[index].find_element_by_xpath('.//td[1]').get_attribute("innerHTML")

                    # 状态 Status
                    if key.find('Status') >= 0:
                        index_status = index
                        
                    # 金额 Amount
                    if key.find('Amount') >= 0:
                        index_amount = index
                        
                    # 备注 Short Note
                    if key.find('Short Note') >= 0:
                        index_short_note = index

                    index += 1;

                # 根据index获取控件值
                try:
                    status = filed_table_item[index_status].find_element_by_xpath('.//td[2]').get_attribute("innerHTML").lstrip().rstrip()
                except NoSuchElementException as m:
                    status = ""

                # 结束页面判断
                # 文本标识是否存在
                # Success
                if 'Success' not in status:
                    self.print_d('转账失败-%s' % status);
                    res = self.sendStatus(self.order_no, Status.v345);
                    res['actionMsg'] = status;
                    result = self.sendStatus(self.order_no, res);
                    return result

                try:
                    amount_str = filed_table_item[index_amount].find_element_by_xpath('.//td[2]').get_attribute("innerHTML").lstrip().rstrip()
                except NoSuchElementException as m: 
                    amount = ""
                else:
                    amount_arr = amount_str.split()
                    amount = amount_arr[0]

                try:
                    note = filed_table_item[index_short_note].find_element_by_xpath('.//td[2]').get_attribute("innerHTML").lstrip().rstrip()
                except NoSuchElementException as m:
                    note = ""

                result = self.sendStatus(self.order_no, Status.v340);
                result.update({'reference':note});
                result.update({'orderMsg':status});
                result.update({'amount':self.format_amount(amount)});
                self.print_d('转账成功')

            except Exception as msg:
                self.print_d('查订单信息异常')
                return self.sendStatus(self.order_no, Status.v339);
        else:
            self.print_d('提交OTP成功，但转账失败');

            # 捕获失败原因
            try:
                locator = (By.ID, "td_errorMessageContainer_errormessage");
                field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
            except Exception:
                self.print_d('转账失败，未捕获到错误原因');
                return self.sendStatus(self.order_no, Status.v339);
            try:
                message = field_div_error.find_element_by_tag_name("div").get_attribute("innerHTML");
            except Exception:
                message = 'unknown error'

            # 验证码错误提示，可重试，返回341，其他错误返回339
            # Sorry, Incorrect OTP (4005)
            if (message.find("Incorrect OTP") >= 0):
                res = self.sendStatus(self.order_no, Status.v341);
            else:
                res = self.sendStatus(self.order_no, Status.v339);
                
            self.print_d('转账失败-%s' % message);
            res['actionMsg'] = message;
            result = self.sendStatus(self.order_no, res);

        return result

    def resend_sms_code(self):
        self.print_d('此功能未实现');
        pass;

    # 登出
    def logout(self):

        self.sendStatus(self.order_no, Status.o400);
        self.print_d('开始登出')

        try:
            field_btn_logout = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "logoutbt")))
        except Exception:
            self.print_d('没有找到登出按钮')
            return self.sendStatus(self.order_no, Status.o401);

        field_btn_logout.click()
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

        if (current_url.find("timeout.jsp") >= 0):
            if (auto_quit):
                self.quit();
            return True;
        else:
            return False;
