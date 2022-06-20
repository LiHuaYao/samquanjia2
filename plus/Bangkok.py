import time
from datetime import datetime

import psutil
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains

class Bangkok(Personification) :

    def __init__(self, proxy_index = None, order_no = None):
        Personification.__init__(self)

        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no

        self.tranfer_list_status = 0;
        self.config = Config.Bangkok
        self.status_path = self.config.STATUS_PATH

        self.print_d('准备打开页面')

        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=bangkokbank")

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
                self.field_input_user_id = self.driver.find_element_by_id("txiID")
                self.field_input_password = self.driver.find_element_by_id("txiPwd")
                self.field_btn_login = self.driver.find_element_by_id("btnLogOn")
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

    def to_bank(self,bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.bangkokbank[bank]
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
    def input_user_name(self,user_name = None):

        self.sendStatus(self.order_no, Status.l108);
        self.print_d('开始输入用户名')

        try:
            field_input_user_id = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txiID")))
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
            field_input_password = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "txiPwd")))
        except Exception:
            self.print_d('没有找到密码输入')
            return self.sendStatus(self.order_no, Status.l121);

        if psw is not None :
            field_input_password.clear();
            field_input_password.send_keys(psw);
            self.print_d("输入密码成功");

        return self.sendStatus(self.order_no, Status.l122);

    # 点击登陆
    def handle_login(self):

        self.print_d('开始点击登陆按钮')

        try:
            field_btn_login = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "btnLogOn")))
        except Exception:
            self.print_d('没有找到登陆按钮')
            return self.sendStatus(self.order_no, Status.l131);

        # field_btn_login.click()
        self.driver.execute_script("arguments[0].click();", field_btn_login)
        self.print_d("点击登陆按钮");

        # 判断是否登陆成功
        try:
            WebDriverWait(self.driver, 5).until_not(EC.visibility_of_element_located((By.ID, "toppage")))
        except Exception:
            self.print_d('登录成功，到用户默认主页');
            self.tranfer_list_status = 2
            return self.sendStatus(self.order_no, Status.l130);

        # 捕获登陆失败原因
        try:
            field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "lblError")))
        except Exception:
            self.print_d('登陆失败，未捕获到错误原因');
            return self.sendStatus(self.order_no, Status.l131);

        try:
            message = field_div_error.get_attribute("innerHTML").lstrip().rstrip()
        except Exception:
            message = 'unknown error'

        # 跳转回登陆页
        try:
            self.driver.get(self.config.OPEN_URL);
            self.print_d('重新跳转至登陆页面成功')
        except Exception:
            self.print_d('重新跳转至登陆页面失败')
            return self.sendStatus(self.order_no, Status.o002);

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
    def input_psw_and_submit(self, userName, psw):

        self.sendStatus(self.order_no, Status.l120);
        self.print_d('开始输入密码')

        # 用户名
        result = self.input_user_name(userName);
        if (result['actionCode'] != Status.l110['actionCode']):
            return result

        # 密码
        result = self.input_user_psw(psw)
        if (result['actionCode'] != Status.l122['actionCode']):
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

        self.sendStatus(self.order_no, Status.t209);
        self.print_d('保持在账户默认页')

        account_list = []

        # 是否为账户页
        defaultPage = 'https://ibanking.bangkokbank.com/workspace/16AccountActivity/wsp_AccountSummary_AccountSummaryPage.aspx'
        if (defaultPage != self.driver.current_url):
            self.print_d("非账户默认页");
            self.sendStatus(self.order_no, Status.o002);
            return account_list

        # 获取账户信息
        self.print_d("开始获取付款账户信息")

        try:
            field_div_account = WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_pnlMain")))
        except Exception:
            self.print_d('没有找到付款账户信息')
            self.sendStatus(self.order_no, Status.t212);
            return account_list

        try:
            account_items = field_div_account.find_elements_by_xpath('./table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/table/tbody/tr[@class="RowGridViewAll"]');
        except NoSuchElementException as msg:
            self.print_d("获取付款账户信息异常");
            self.screen(None)
            self.sendStatus(self.order_no, Status.t212);
            return account_list

        account_len = len(account_items)
        index = 0

        while index < account_len:
            # 昵称也许为空
            try:
                account_name = account_items[index].find_element_by_xpath('.//td[3]/span').get_attribute("innerHTML").lstrip().rstrip()
            except Exception as m:
                account_name = ""

            account_num = account_items[index].find_element_by_xpath('.//td[1]/a').get_attribute("innerHTML").lstrip().rstrip()
            balances = account_items[index].find_element_by_xpath('.//td[5]/span').get_attribute("innerHTML").lstrip().rstrip()
            currency = ""

            account = {};
            account.update({"accountName": account_name, "accountNumber": account_num, "currency": currency, "balances": balances})
            account_list.append(account);
            index += 1;

        return account_list;
    
    # 到账户的转账列表页
    def goto_account_transfer(self, accountNum):
        self.print_d('此功能未实现');
        pass;

    # 到转账页
    def goto_transfer(self):

        self.sendStatus(self.order_no, Status.t209);
        self.print_d('开始跳转至手机付款页面')

        try:
            self.driver.get("https://ibanking.bangkokbank.com/workspace/06Transfer/wsp_Transfer_AddPromptPayTransfer.aspx");
            self.print_d('跳转至手机付款页面成功')
            self.sendStatus(self.order_no, Status.t210);
            return True
        except Exception:
            self.print_d('跳转至手机付款页面失败')
            self.sendStatus(self.order_no, Status.t209);

        return False

    # 选择转账信息
    def select_tranfer_info(self, info):

        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        # 判断是否在手机转账页
        if (self.driver.current_url.find("wsp_Transfer_AddPromptPayTransfer.aspx") < 0):
            self.print_d('当前页面非手机转账页，跳转至手机转账页')
            self.goto_transfer()

        self.sendStatus(self.order_no, Status.t211);
        self.print_d('开始处理付款方下拉菜单')

        account_number = info['accountNumber']

        # 选择付款方下拉按钮
        try:
            locator = (By.XPATH, '//select[@name="ctl00$ctl00$C$CW$ddlFromAccountList"]')
            field_select_account = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
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

        # 选择使用 Mobile Number
        try:
            field_td_type_mobile = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_lblMain_ToMobilePhone")))
        except Exception:
            self.print_d('没有找到收款方手机快捷类型选项')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择选择使用MobileNumber
        field_td_type_mobile.click()
        self.print_d('点击选择选择使用MobileNumber')

        # 手机号码输入框
        try:
            field_input_promptpay = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_txtMain_ToMobilePhone")))
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
            field_input_amount = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_txtAmount")))
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
            field_input_note = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_txtPersonalReminder")))
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
            field_btn_next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00_ctl00_C_CW_btnNext")))
        except Exception:
            self.print_d('没有找到转账信息下一步按钮')
            return self.sendStatus(self.order_no, Status.t243);

        # 点击进行下一步，到OTP页面
        field_btn_next.click();
        self.print_d("提交转账信息，到OTP页面");
        return self.sendStatus(self.order_no, Status.t244);

    # 输入转账方信息并到发送验证码
    def input_transfer_info(self, info):

        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.print_d('开始处理收款方信息')

        # 手机号码快捷转账
        result = self.transfer_mobile(info)
        if (result['actionCode'] != Status.t244['actionCode']):
            return result

        # 是否到转账页面
        try:
            field_btn_next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "ctl00_ctl00_C_CW_ucOTPBox_btnConf")))
        except Exception:
            self.print_d('转账失败，未捕获到错误原因')
            return self.sendStatus(self.order_no, Status.t261);

        self.print_d("加载OTP页面成功，自动触发发送OTP，无OTP标识");
        result = self.sendStatus(self.order_no, Status.v320);
        result.update({'refno':''});

        return result;

    # 输入短信验证码
    def input_sms_code(self, code):
 
        #判断页面超时
        if (self.is_session_timeout(True)):
            return self.sendStatus(self.order_no, Status.o410);

        self.sendStatus(self.order_no, Status.v321);
        self.print_d('开始输入OTP')

        # OTP输入框
        try:
            field_input_transfer_otp = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "ctl00_ctl00_C_CW_ucOTPBox_txtOneTime")))
        except Exception:
            self.print_d('没有找到转账OTP输入框')
            return self.sendStatus(self.order_no, Status.v322);
         
        self.print_d('输入OTP- %s' % code)
        field_input_transfer_otp.clear();
        field_input_transfer_otp.send_keys(code);

        # 提交转账
        self.print_d('开始提交OTP')

        # 提交OTP按钮
        try:
            field_btn_commit_otp = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, 'ctl00_ctl00_C_CW_ucOTPBox_btnConf')))
        except Exception:
            self.print_d("没有找到提交OTP按钮");
            return self.sendStatus(self.order_no, Status.v331);

        # 提交OTP
        field_btn_commit_otp.click()
        self.print_d("点击提交OTP");

        is_commit = True

        # 错误情况 - 表单
        try:
            field_div_otp = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'DESVALSummary')))
        except Exception:
            is_commit = True
            self.print_d('提交添加收款信息OTP表单检测成功')
        else:
            message = field_div_otp.find_element_by_tag_name("span").get_attribute("innerHTML");
            message = message.replace('<br>', '')
            message = message.replace('&nbsp;', '')
            res = self.sendStatus(self.order_no, Status.v341);
            res['actionMsg'] = message;

            self.print_d('提交添加收款信息OTP异常-表单-%s' % message);
            # self.screen(None)
            return self.sendStatus(self.order_no, res);

        # 错误情况 - 提示页
        if (is_commit):
            try:
                field_div_otp_page = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'page-error-text')))
            except Exception:
                self.print_d('提交添加收款信息OTP提示页检测成功')
                # self.print_d('模拟成功情况')

                try:
                    locator = (By.ID, "ctl00_ctl00_C_CW_lbtClickHereToSave");
                    WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(locator))
                except Exception:
                    self.print_d('转账失败，未捕获到成功特征，标记为失败')
                    return self.sendStatus(self.order_no, Status.v339);

                try:
                    field_reulst = self.driver.find_element_by_id("ctl00_ctl00_C_CW_lblmainPromptPayTransferDesc").get_attribute("innerHTML").lstrip().rstrip()
                except Exception:
                    self.print_d('转账失败，未捕获到Result');
                    return self.sendStatus(self.order_no, Status.v339);

                if 'This transfer has been processed' in field_reulst:

                    # 根据index获取控件值
                    try:
                        status = self.driver.find_element_by_id('ctl00_ctl00_C_CW_lblmainPromptPayTransferDesc').get_attribute("innerHTML").lstrip().rstrip()
                    except NoSuchElementException as m:
                        status = ""

                    try:
                        amount = self.driver.find_element_by_id('ctl00_ctl00_C_CW_lblConfAmount_Value').get_attribute("innerHTML").lstrip().rstrip()
                    except NoSuchElementException as m: 
                        amount = ""

                    try:
                        note = self.driver.find_element_by_id('ctl00_ctl00_C_CW_lblConfPersonalReminder_Value').get_attribute("innerHTML").lstrip().rstrip()
                    except NoSuchElementException as m: 
                        note = ""

                    result = self.sendStatus(self.order_no, Status.v340);
                    # result.update({'reference':self.order_no});
                    result.update({'reference':note});
                    result.update({'orderMsg':status});
                    result.update({'amount':self.format_amount(amount)});
                    self.print_d('转账成功')
                    return result
                else:
                    message = field_reulst.replace('<br>', '')
                    message = message.replace('&nbsp;', '')
                    res = self.sendStatus(self.order_no, Status.v339);
                    res['actionMsg'] = message;

                    self.print_d('转账异常-未发现转账成功语句-%s' % message);
                    # self.screen(None)
                    return self.sendStatus(self.order_no, res);
            else:
                message = field_div_otp_page.get_attribute("innerHTML");
                message = message.replace('<br>', '')
                message = message.replace('&nbsp;', '')
                res = self.sendStatus(self.order_no, Status.v339);
                res['actionMsg'] = message;

                self.print_d('转账异常-提示页-%s' % message);
                # self.screen(None)
                return self.sendStatus(self.order_no, res);

        return self.sendStatus(self.order_no, Status.v339);

    # 登出
    def logout(self):

        self.sendStatus(self.order_no, Status.o400);
        self.print_d('开始登出')

        try:
            locator2 = (By.XPATH, '//a[@href="javascript:IMG2_onclick();"]');
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator2))
        except Exception:
            self.print_d('没找到登出按钮')
            return self.sendStatus(self.order_no, Status.o401);
        else:
            field_btn_logout = self.driver.find_element_by_xpath('//a[@href="javascript:IMG2_onclick();"]');

        #可能加载慢
        if (field_btn_logout is None):
            self.print_d("长时间没找到按钮登出，返回页面加载异常");
            self.screen(None)
            return self.sendStatus(self.order_no, Status.o401);

        field_btn_logout.click()
        self.sleep(1)
        self.quit();
        self.print_d("登出成功");

        return self.sendStatus(self.order_no, Status.o402);

    # 判断页面是否超时
    def is_session_timeout(self, auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception as we:
            self.quit()
            return True

        self.print_d(self.order_no + "--" + current_url)

        if (current_url.find("SessionTimeoutError.aspx") > 0):
            if (auto_quit):
                self.quit();
            return True;
        else:
            return False;
