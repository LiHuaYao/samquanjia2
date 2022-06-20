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
from selenium.webdriver.support.select import Select

class Krungsri(Personification) :

    def __init__(self,proxy_index=None,order_no=None):
        Personification.__init__(self)
        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no
        self.tranfer_list_status = 0;
        self.config = Config.Krungsri
        self.print_d('准备打开页面')
        self.status_path = self.config.STATUS_PATH
        chrome_options = ChromeOptions.get_options()
        if(self.config.USE_NO_IMAGE):
            # 无图
            No_Image_loading = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", No_Image_loading)
        chrome_options.add_argument("--bank-name=" + BankType.Bank[4]['val'])
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
        # self.driver.maximize_window()  # 最大化浏览器
        # self.driver.implicitly_wait(8)  # 设置隐式时间等待
        # print("chrome.")
        self.open_and_init()

        # self.sleep(5)
        # print("get.")
        # self.sendStatus(self.order_no,Status.o000);
    def is_use_proxy(self):
        return self.config.US_PROXY_SERVER
    def open_and_init(self):
        try:
            self.driver.get(self.config.OPEN_URL);
        except TimeoutException as te:
            print(te)
            self.quit();
        self.print_d('新建窗口-打开页面-页面加载中')
        if self.order_no:
            self.sendStatus(self.order_no, Status.o000)
        driver_process = psutil.Process(self.driver.service.process.pid)
        if driver_process:
            self.chrome_driver_process = driver_process
        children_list = driver_process.children()
        if children_list:
            self.chrome_process = children_list[0]
        #TODO 检查页面是否正常加载
        #初始化时先把用户名输入和 Login 找到
        self.is_open = True
        self.user_name_input = None
        self.delayCoefficient = 1
        open_wait_index = 1;
        while open_wait_index < self.config.FIND_USER_NAME_TIME_OUT:
            try:
                open_wait_index = open_wait_index + 1;
                userName = self.driver.find_element_by_class_name("input-new-login-username");
            except  NoSuchElementException as msg:
                self.print_d('还没找到用户名输入。%d' % open_wait_index);
                self.sleep(1);
            else:
                self.print_d('新建窗口-页面加载完成')
                self.open_code = Status.o001['actionCode']
                if self.order_no:
                    self.sendStatus(self.order_no, Status.o001)
                self.user_name_input = userName;
                try:
                    password = self.driver.find_element_by_class_name("input-new-login-password");
                except NoSuchElementException:
                    pass
                else:
                    self.psw_input = password;
                # self.sendStatus(self.order_no, Status.o001);
                self.action_code = Status.o001['actionCode'];
                delayCoefficient = open_wait_index / 3;
                if (delayCoefficient < 1):
                    delayCoefficient = 1;
                print("delay=%d" % delayCoefficient)
                try:
                    self.login_button = self.driver.find_element_by_class_name("login_submit")
                except NoSuchElementException:
                    pass
                break
    def get_tranfer_list_status(self):
        return self.tranfer_list_status;
    def to_bank(self,bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.Krungsri[bank]
        except Exception:
            return False
        if (to_bank is not None):
            self.t_to_bank = to_bank
            return True
    #输入用户名
    def back_input_name(self,userName):
        #SecurityPhrase---close---3hEiD
        # self.user_name_input = None;
        # self.loginUserName = userName;
        # try:
        #     locator2 = (By.CSS_SELECTOR, "span[class^='SecurityPhrase---close'");
        #     WebDriverWait(self.driver, 1.5, 0.5).until(EC.visibility_of_element_located(locator2))
        # except Exception:
        #     self.print_d('没找到关闭');
        # else:
        #     close = self.driver.find_element_by_css_selector("span[class^='SecurityPhrase---close'");
        #     close.click();
        return
    # 取转账列表
    def get_transfer_list(self):
        transfer_list = []
        is_account_info = False
        for index in range(1, 20):
            current_url = self.driver.current_url
            # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
            print(current_url)
            if (current_url.find("accountDetails") > 0):
                is_account_info = True;
                break;
            else:
                time.sleep(1)
        if False == is_account_info:
            return  transfer_list
        try:
            locator2 = (By.TAG_NAME, "tbody");
            WebDriverWait(self.driver, 15, 0.5).until(EC.visibility_of_element_located(locator2))
        except Exception:
            self.print_d('没找到转账列表');
            return transfer_list
        self.tranfer_list_status = 3
        tbody = self.driver.find_element_by_tag_name('tbody')
        tr_list = tbody.find_elements_by_tag_name('tr')
        print(len(tr_list))
        for tr in tr_list:
            td_list = tr.find_elements_by_tag_name('td');
            print(len(td_list))
            if (len(td_list) <4 ):
                continue
            amount = td_list[3]
            self.print_d(amount.text)
            div = amount.find_element_by_tag_name('div')
            classes = div.get_attribute('class')
            print(classes)
            if classes.find('negativeAmount') > -1:
                self.print_d('转出')
            else:
                self.print_d('转入的')
                transfer = {}
                transfer['amount'] = amount.text.replace('RM', '')

                date = td_list[0].text
                timeArray = time.strptime(date, "%d %b %Y")
                timeStamp = int(time.mktime(timeArray))
                transfer['time'] = timeStamp

                transfer['details'] = td_list[1].text

                transfer_list.append(transfer)
        return transfer_list

    #输入用户名
    def input_user_name(self,user_name = None):
        result = self.sendStatus(self.order_no,Status.l108);
        self.print_d('开始输入用户名')
        # self.save_html('开始输入用户名'+str(result))
        if (self.user_name_input is None):
            try:
                locator2 = (By.CLASS_NAME, "input-new-login-username");
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator2))
            except Exception:
                self.print_d('没找到用户名输入')
                result = self.sendStatus(self.order_no,Status.l109);
                return result
            else:
                self.print_d('已找到用户名输入')
                self.user_name_input = self.driver.find_element_by_class_name("input-new-login-username");
                self.login_button = self.driver.find_element_by_class_name("login_submit")
                # LoaderNew---overlay
        ##可能加载慢
        if (self.user_name_input is None):
            self.print_d("长时间没找到用户名输入，返回页面加载异常");
            self.screen(None);
            self.screen(self.order_no + '_' + str(Status.o002['actionCode']))
        if user_name is not None :
            self.loginUserName = user_name
        self.user_name_input.clear();
        self.user_name_input.send_keys(user_name);
        # js = "$('#username').val('"+self.loginUserName+"');"
        # self.driver.execute_script(js)
        self.print_d("输入用户名");
        self.action_code = Status.l108['actionCode'];
        result = self.sendStatus(self.order_no, Status.l108);

        # time.sleep(0.2)
        # self.login_button.click();
        # self.print_d("点击 LOGIN");
        # 输入用户名是不是正常 notification-error
        self.action_code = Status.l110['actionCode'];
        result = self.sendStatus(self.order_no, Status.l110);
        return result;
    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        if (self.psw_input is None):
            try:
                locator2 = (By.CLASS_NAME, "input-new-login-password");
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator2))
            except Exception:
                self.print_d('没找到密码输入')
                result = self.sendStatus(self.order_no, Status.l109);
                return result
            else:
                self.psw_input = self.driver.find_element_by_class_name("input-new-login-password");
                self.print_d('找到密码输入');
                self.action_code = Status.l120['actionCode'];
                result = self.sendStatus(self.order_no, Status.l120);
        else:
            self.print_d('已有密码输入');
            self.action_code = Status.l120['actionCode'];
            result = self.sendStatus(self.order_no, Status.l120);
        return result
    #输入密码并提交
    def input_psw_and_submit(self,userName,psw,captcha = None):
        self.loginPassword = psw;
        result = Status.l120
        if (userName != self.loginUserName):
            #重新输入用户名登录
            self.back_input_name(userName);
            time.sleep(0.5)
            result = self.input_user_name(userName);
            if(result['actionCode'] != Status.l110['actionCode']):
                return result
            result = self.check_and_find_psw()
            if (result['actionCode'] != Status.l120['actionCode']):
                return result

        if (self.psw_input is None):
            try:
                self.psw_input = self.driver.find_element_by_class_name("input-new-login-password");
            except NoSuchElementException :
                self.action_code = Status.l121['actionCode'];
                return self.sendStatus(self.order_no, Status.l121);
        self.psw_input.send_keys(self.loginPassword);
        self.print_d(self.loginPassword);
        self.print_d(self.psw_input);
        self.print_d('输入密码');
        result = self.sendStatus(self.order_no, Status.l122);
        time.sleep(0.4)
        if(self.login_button is None):
            self.login_button = self.driver.find_element_by_class_name("login_submit")
        try:
            self.login_button.click();
            self.print_d("点击登录")
        except Exception:
            return result
        is_login = False;
        security_check = False;
        security_pic="";
        # 输入密码是不是正常 notification-error
        # try:
        #     locator2 = (By.CLASS_NAME, "notification-error");
        #     WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator2))
        # except Exception:
        #     self.print_d('密码输入成功');
        # else:
        #     self.print_d('密码输入异常');
        #     res = self.sendStatus(self.order_no,Status.l131);
        #     try:
        #         notification_error = self.driver.find_element_by_class_name("notification-error");
        #         span = notification_error.find_element_by_tag_name("span");
        #     except NoSuchElementException:
        #         pass
        #     else:
        #         span_text = span.text;
        #         res['actionMsg'] = span_text;
        #     self.screen(None)
        #     self.quit();
        #     self.action_code = res['actionCode'];
        #     return self.sendStatus(self.order_no, res);
        for index in range(1, 40):
            current_url = self.driver.current_url
            # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
            # print(current_url)
            if (current_url.find("MyPortfolio") > 0):
                is_login = True;
                break;
            # elif(current_url.find("Login.aspx") > 0 and current_url.find("language") < 0):
            #     is_login = False;
            #     break;
            else:
                time.sleep(1);
                # 找错误提示

                #找输入验证码
                try:
                    myModal = self.driver.find_element_by_id("myModal");
                    img = myModal.find_element_by_tag_name("img");
                    security_pic = img.get_attribute('src');
                except NoSuchElementException:
                    pass
                else:
                    if(myModal.is_displayed()):
                        security_check = True;
                        break
        if(security_check):
            result = self.sendStatus(self.order_no, Status.l140);  # 安全验证
            result['question'] = 'question';
            result['securityQuestion'] = security_pic;
            return result
        if (is_login):
            self.print_d('登录成功');
            self.tranfer_list_status = 2
            self.action_code = Status.l130['actionCode'];
            result = self.sendStatus(self.order_no, Status.l130);
        else:
            self.print_d('帐号或密码不正确');
            self.screen(None)
            self.action_code = Status.l131['actionCode'];
            result = self.sendStatus(self.order_no, Status.l131);
        return result
    #登录
    def login(self) :
        self.print_d('开始登录')
        start_time = datetime.now();
        #LoaderNew---overlay
        action = self.input_user_name();
        if (action['actionCode'] != Status.l110['actionCode'] ):
            return action;
        # self.sleep(1.5)
        action = self.check_and_find_psw();
        if (action['actionCode'] != Status.l120['actionCode'] ):
            return action;
        action = self.input_psw_and_submit();
        return action

        # 输入安全问题
    def input_answer(self, answer):
        try:
            myModal = self.driver.find_element_by_id("myModal");
            user_answer = myModal.find_element_by_css_selector("input[type^='text'")
        except NoSuchElementException:
            return Status.l144
        user_answer.send_keys(answer)
        time.sleep(0.3)
        try:
            submit = myModal.find_element_by_css_selector("input[value^='Submit'")
        except NoSuchElementException:
            pass
            # jsString = "doSubmit();"
            # self.driver.execute_script(jsString)
        else:
            submit.click()
        is_login = False;
        for index in range(1, 40):
            current_url = self.driver.current_url
            # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
            print(current_url)
            if (current_url.find("MyPortfolio") > 0):
                is_login = True;
                break;
            # elif(current_url.find("Login.aspx") > 0 and current_url.find("language") < 0):
            #     is_login = False;
            #     break;
            else:
                time.sleep(1);
                # 找错误提示
        if(is_login == False):
            # 登录出错
            self.print_d("登录超时-1")
            result = self.sendStatus(self.order_no, Status.l131)
        else:
            # 登录成功
            self.print_d("登录成功-2")
            result = self.sendStatus(self.order_no, Status.l130)
        return result


    def account_list(self):
        self.print_d("取帐号列表")
        accountList = [];
        account_len = 0 ;
        find_index = 0 ;
        tr_list = [];

        while (account_len < 1 and find_index < 20) :
            try:
                table = self.driver.find_element_by_class_name("myport_table");
                tbody = table.find_element_by_tag_name("tbody");
                tr_list = tbody.find_elements_by_tag_name("tr");
            except  NoSuchElementException as msg:
                self.print_d('查找帐号列表异常');
                self.screen(None);
            else:
                account_len = len(tr_list)
            self.sleep(1)
            find_index += 1;
        if (account_len  > 0 ):
            index = 0;
            while index < account_len:
                print(index);
                td_list = tr_list[index].find_elements_by_tag_name("td");
                account_num = td_list[1].text;
                account_name = account_num;
                available_balance = td_list[2].text;
                print(available_balance);
                ab = available_balance.split( );
                # print(ab[0]);
                # print(ab[1]);
                bal = ab[0];
                currency = ab[1];
                account = {};
                account.update({"accountName": account_name, "accountNumber": account_num,
                                "currency": currency, "balances": bal})
                index += 1;
                accountList.append(account);
        # Client.send_account_list(self.order_no,accountList);
        self.accountList = accountList;
        return accountList;

    #显示余额  Navigation---amounts
    # try:
    #     spans = self.driver.find_element_by_css_selector("div[class^='Navigation---amounts']").find_elements_by_tag_name("span");
    #     amounts= "";
    #     for span in spans:
    #         amounts = amounts +span.text;
    #
    # except  NoSuchElementException as msg:
    #     print('查找amounts元素异常 %s'%msg);
    # else:
    #     print("帐号总余额：%s"%amounts);
        # 到账户的转账列表页

    def goto_account_transfer(self, accountNum):
        isFindAccount = False
        try:
            locator2 = (By.CSS_SELECTOR, "div[class^='ApplyCard---container']")
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator2))
        except  Exception:
            print('ApplyCard---container')
        else:
            account_numbers = self.driver.find_elements_by_css_selector("span[class^='Card---accountNumber']");
            for num in account_numbers:
                print(num.text)
                if (num.text.find(accountNum) > -1 ):
                    isFindAccount = True;
                    num.click()
                    break
        if (False == isFindAccount):
            self.print_d('没找到帐号');
            self.screen(None);
        return isFindAccount

    #到转账页
    # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
    def goto_transfer(self):
        self.print_d('开始到转账页');
        # self.sleep(1);
        result = False;
        try:
            self.driver.get("https://www.krungsrionline.com/BAY.KOL.WebSite/Pages/FundTransfer/OtherTransfer.aspx?pgno=11");
            result = True;
        except  Exception :
            self.print_d('到转账页异常');
        # transfer_other = self.driver.find_element_by_partial_link_text("Other Account");
        # transfer_other.click();
        return result;
    def get_account_name_by_num(self,accountNum):
        if ( len(self.accountList) > 0):
            for account in self.accountList:
                if(account['accountNumber'] == accountNum):
                    return account['accountName']
        return None
    #选择转账信息
    # https://www.maybank2u.com.my/home/m2u/common/transactions/transfer
    def select_tranfer_info(self,info):
        self.print_d('选择转账帐号');
        return self.sendStatus(self.order_no, Status.t230);
        #选择转账帐号
        account_number = info['accountNumber']
        #https://www.maybank2u.com.my/home/m2u/common/transactions/transfer
        current_url = self.driver.current_url
        self.print_d(current_url)
        wait = 0
        if (current_url.find('/OtherTransfer') < 0 and wait < 20):
            wait = wait + 1
            time.sleep(1)
            current_url = self.driver.current_url
        accountName = self.get_account_name_by_num(account_number)
        is_select_account = False;
        accounts_dropdown = None;
        locator2 = (By.CSS_SELECTOR, "div[class^='PayNavigation---selected']")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.element_to_be_clickable(locator2))
        except Exception:
            self.print_d('*****')
            # if (not self.goto_transfer()):
            return self.sendStatus(self.order_no,Status.t209)
        else:
            index = 0
            while index < 10 :
                try:
                    selected = self.driver.find_element_by_css_selector("div[class^='PayNavigation---selected']")
                except Exception:
                    pass
                else:
                    if( selected.text.find('TRANSFER') > -1 ):
                        break
                time.sleep(0.5)
        find_accounts_dropdown_index = 0
        while find_accounts_dropdown_index < 10:
            accounts_dropdowns = self.driver.find_elements_by_id("accounts_dropdown");
            if (len(accounts_dropdowns) == 1):
                accounts_dropdown = accounts_dropdowns[0];
            elif (len(accounts_dropdowns) > 1):
                for ad in accounts_dropdowns:
                    if (ad.is_displayed()):
                        accounts_dropdown = ad
                        find_accounts_dropdown_index = 10
                        break
                    time.sleep(0.5)
        if (accounts_dropdown is None):
            self.screen(None)
            return Status.t211
        try:
            row = accounts_dropdown.find_element_by_class_name("row")
        except NoSuchElementException as e :
            print(e)
        else:
            # print(row.text)
            # print(accountName)
            # print(row.text.find(accountName))
            if (not accountName or accountName is None):
                return self.sendStatus(self.order_no,Status.t212)
            if (row.text.find(accountName) > -1):
                is_select_account = True
        if (not is_select_account):
            if(accounts_dropdown is None):
                self.screen(None);
                self.action_code = Status.t211['actionCode'];
                return self.sendStatus(self.order_no, Status.t211) ;
            accounts_dropdown.click();
            time.sleep(0.7);
            try:
                select_account = self.driver.find_element_by_partial_link_text(account_number);
            except Exception as e :
                self.action_code = Status.t212['actionCode'];
                return self.sendStatus(self.order_no, Status.t212);
            if( select_account ):
                print(select_account.text);
                select_account.click();
                time.sleep(0.6)
            else:
                self.action_code = Status.t212['actionCode'];
                return self.sendStatus(self.order_no, Status.t212);
        # 选择转账类型
        paytoDropdowns = self.driver.find_elements_by_id("payto_dropdown");
        print("paytoDropdowns.len=%d"%len(paytoDropdowns));
        if (len( paytoDropdowns ) > 1):
            paytoDropdowns[1].click();
        else:
            paytoDropdowns[0].click();
        # self.sleep(1);
        try:
            locator3 = (By.PARTIAL_LINK_TEXT, "Other")
            WebDriverWait(self.driver, 2, 0.5).until(EC.visibility_of_element_located(locator2))
        except Exception:
            return self.sendStatus(self.order_no,Status.t221)
        otherAccounts = self.driver.find_element_by_partial_link_text("Other");
        otherAccounts.click();
        # self.sleep(0.3)
        self.action_code = Status.t220['actionCode'];
        result = self.sendStatus(self.order_no, Status.t220);
        # self.sleep(2.5)
        locator1 = (By.XPATH, "//input[@placeholder='New Transfer']")
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator1))
        except Exception as e:
            print("***************")
            print(e)
            return result
            # < input  type = "text" class ="PayFromToContainer---paymentInput---2QHL7" placeholder="New Transfer" value="" >
        try:
            newTransfer = self.driver.find_element_by_xpath("//input[@placeholder='New Transfer']");
        except  NoSuchElementException as msg:
            print('New Transfer');
            # self.exitFun("newTransfer error");
            return result
        else:
            newTransfer.click();
            time.sleep(0.4)
            jsString = '$(".dropdown-menu").css("max-height","none")';
            self.driver.execute_script(jsString);
        # self.sleep(3);
        # to_bank = BankType.ToBank.MayBank[to_bank]
        self.print_d("to_bank=%s"%self.t_to_bank)
        try:
            locator = (By.PARTIAL_LINK_TEXT, self.t_to_bank)
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e :
            print('----------')
            print(e)
        try:
            tobank = self.driver.find_element_by_partial_link_text(self.t_to_bank);
        except NoSuchElementException:
            return self.sendStatus(self.order_no,Status.t231)
        # self.sleep(0.6)
        self.driver.execute_script("arguments[0].click();", tobank)
        # tobank.click();
        self.action_code = Status.t230['actionCode'];
        return self.sendStatus(self.order_no, Status.t230);
    #输入转账方信息并提交
    def input_transfer_info(self, info):
        self.print_d("输入转账信息")
        result = Status.t210;
        try:
            # 是否在转账页面
            locator = (By.ID, "ddlBanking")
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('可能没在转账页')
            return result
        self.print_d("找到选择银行类型 select")
        # transferAccount, transferAmount, transferReference
        #转账银行类型
        selector = Select(self.driver.find_element_by_id("ddlBanking"))

        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        transferRecipientName = info['recipientName']
        # select_bank_text = BankType.ToBank.Krungsri[self.t_to_bank]
        self.print_d(self.t_to_bank)
        selector.select_by_index(self.t_to_bank)  # 通过标签显示的text进行选择
        time.sleep(1)
        try:
            # 转账帐号
            account_number_input = self.driver.find_element_by_class_name("value_AccTo");
            account_number_input.send_keys(transferAccount);
            time.sleep(1)
            # 转账金额
            amount_input = self.driver.find_element_by_class_name("value_amount");
            amount_input.send_keys(transferAmount);
            time.sleep(1)
            # type
            selector = Select(self.driver.find_element_by_id("ctl00_cphSectionData_ddlFixedType"))
            selector.select_by_index("6")  # 通过index进行选择,index从0开始
            #备注
            text_area_list = self.driver.find_elements_by_class_name("noresize_TextArea");
            memo = None;
            for ta in text_area_list:
                if(ta.is_displayed()):
                    memo = ta ;
                    break
            if (memo != None):
                memo.send_keys(transferReference)
            print(memo);
        except Exception:
            self.print_d('转账信息输入异常')
            result = self.sendStatus(self.order_no, Status.t243);
            return result

        print("转账信息已填:" + transferAccount + "|" + transferAmount);
        self.action_code = Status.t242['actionCode'];
        result = self.sendStatus(self.order_no, Status.t242);

        #提交
        try:
            btnTransfer = self.driver.find_element_by_css_selector("input[value^='Submit']");
        except  NoSuchElementException as msg:
            print('查找 btn-Submit 异常， ');
            self.screen(None)
            self.action_code = Status.t230['actionCode'];
            return self.sendStatus(self.order_no, Status.t230);
        else:
            print(btnTransfer.tag_name+"|"+btnTransfer.text);
            btnTransfer.click();
            self.action_code = Status.t250['actionCode'];
            result = self.sendStatus(self.order_no, Status.t250);
        #判断与转账单是否成功
        locator3 = (By.CLASS_NAME, "summary_error_box")
        try:
            WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator3))
        except Exception:
            is_confirm_transfer = False;
            for index in range(1, 20):
                current_url = self.driver.current_url
                # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
                print(current_url)
                if (current_url.find("ConfirmTransfer") > 0):
                    is_confirm_transfer = True;
                    break;
                else:
                    time.sleep(1)
            if (is_confirm_transfer):
                print("成功");
                result = self.sendStatus(self.order_no, Status.v320);
            else:
                print("超时");
                result = self.sendStatus(self.order_no, Status.t261);
        else:
            title = self.driver.find_element_by_class_name("summary_error_box");
            result = Status.t261;
            result['actionMsg'] = title.text;
            self.screen(None)
            self.action_code = result['actionCode'];
            result = self.sendStatus(self.order_no, result);
        return result;

    ##输入验证码
    def input_sms_code (self,code):
        self.print_d("输入验证码")
        self.action_code = Status.v321['actionCode'];
        result = self.sendStatus(self.order_no,Status.v321);
        #判断页面超时
        if ( self.is_session_timeout(True) ):
            self.action_code = Status.o410['actionCode'];
            result = self.sendStatus(self.order_no, Status.o410);
            return
        try:
            otp = self.driver.find_element_by_class_name("textbox_otppassword");
        except  NoSuchElementException as msg:
            self.print_d('查找 otp输入 异常。');
            self.action_code = Status.v322['actionCode'];
            result = self.sendStatus(self.order_no, Status.v322);
            try:
                errorMessage = self.driver.find_element_by_class_name("errorMessage");
            except NoSuchElementException:
                pass
            else:
                result = self.sendStatus(self.order_no, Status.o430);
                result['actionMsg'] = errorMessage.text;
                result['bankMsg'] = errorMessage.text;
            return result
        else:
            self.print_d("已找到 otp")

        # code = input("请输入收到的短信验证码:")
        self.print_d("验证码:%s"%code);
        try:
            otp.clear();
        except Exception as e:
            self.print_d('fail清空输入框')
        # 输入验证吗
        otp.send_keys(code);
        self.action_code = Status.v330['actionCode'];
        result = self.sendStatus(self.order_no, Status.v330);
        time.sleep(1);
        try:
            confirmBtn = self.driver.find_element_by_css_selector("input[value^='Confirm']");
        except  NoSuchElementException as msg:
            self.print_d('查找confirmBtn异常 %s'%msg);
            try:
                button_yellow = self.driver.find_elements_by_class_name("button_yellow");
                for bt in button_yellow :
                    if(bt.get_attribute('type') == "button"):
                        confirmBtn = bt;
                        break;
            except NoSuchElementException :
                self.action_code = Status.v331['actionCode'];
                return self.sendStatus(self.order_no, Status.v331);

        self.print_d('找到 confirmBtn');
        # 确认
        confirmBtn.click();
        self.action_code = Status.v332['actionCode'];
        result = self.sendStatus(self.order_no, Status.v332);
        time.sleep(1);
        # LoaderN
        index = 0;
        loading = False;
        # while index < 30:
        #     try:
        #         LoaderNew = self.driver.find_element_by_id("UpdateProgress");
        #         if(LoaderNew.is_displayed()):
        #             loading = True
        #     except Exception as msg:
        #         self.print_d("UpdateProgress:"+msg);
        #         break;
        #     if(loading):
        #         self.print_d('loading.');
        #         index += 1;
        #         self.sleep(0.5);
                #TransactionSummary---currency
        locator3= (By.CLASS_NAME, "page_header")
        try:
            WebDriverWait(self.driver, 15, 0.5).until(EC.visibility_of_element_located(locator3))
        except Exception as e:
            self.print_d(e)
            result = Status.v339;
            return result
        #判断转账结果
        self.print_d('$$$$$$加载完成$$$$$')
        time.sleep(1.5)
        self.screen(None)
        self.save_html(None)
        transfer_success = False;
        try:
            progress_current = self.driver.find_element_by_class_name("progress_current");
            self.print_d(progress_current.text);
            if (progress_current.text.find("3") > -1):
                transfer_success = True;
            #TODO 加多一个成功判断
        except  NoSuchElementException as msg:
            self.print_d('转账没成功');
            result = Status.v341;

        if(transfer_success == False):
            for index in range(1, 10):
                current_url = self.driver.current_url
                # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
                self.print_d(current_url)
                if (current_url.find("CompletedTransfer") > 0):
                    transfer_success = True;
                    break;
                else:
                    try:
                        transaction_result_green = self.driver.find_element_by_class_name("transaction_result_green");
                    except NoSuchElementException:
                        time.sleep(0.5)
                    else:
                        transfer_success = True;
                        break;

        # 结束页面判断
        # 文本标识是否存在
        # Fund transfer transaction is complete.
        try:
            field_reulst = self.driver.find_element_by_id("ctl00_cphSectionData_pnlSuccessMsg").get_attribute("innerHTML").lstrip().rstrip()
        except Exception:
            self.print_d('转账失败，未捕获到Result');
            return self.sendStatus(self.order_no, Status.v339);

        if 'Fund transfer transaction is complete' not in field_reulst:
            try:
                field_error_reulst = self.driver.find_element_by_class_name("transaction_result_errorbox_body").get_attribute("innerHTML").lstrip().rstrip()
            except Exception:
                self.print_d('转账失败，未捕获到Error');
                return self.sendStatus(self.order_no, Status.v339);
            else:
                self.print_d('转账失败-%s' % field_error_reulst);
                res = self.sendStatus(self.order_no, Status.v345);
                res['actionMsg'] = field_error_reulst;
                result = self.sendStatus(self.order_no, res);
                return result

        if (transfer_success):
            #取信息
            result = Status.v340
            result.update({'orderMsg':''});
            result.update({'amount':''});
            result.update({'reference':''});
            result['orderMsg'] = 'Successful';
            try:
                locator3 = (By.CLASS_NAME, "wrap-text")
                WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator3))
                wrap_text = self.driver.find_element_by_class_name("wrap-text");
                reference = wrap_text.text;
                result['reference']  = reference.strip()
            except Exception as msg:
                self.print_d('查订单信息异常一');
                self.print_d(msg);
            try:
                rows = self.driver.find_elements_by_class_name("transaction_detail_row_value");
                amount = None;
                amount_text = "";
                if(len(rows) > 0 ):
                    amount = rows[0]
                if(amount is not None):
                    amount_text = amount.text;
                    amount_text_list = amount_text.split(" ");
                    amount_text = amount_text_list[0];
                result['amount'] = self.format_amount(amount_text)
            except Exception as msg:
                self.print_d('查订单信息异常二');
                self.print_d(msg);
            self.sendStatus(self.order_no, result);
            return result; #返回转账成功
        else:
            #转账异常，取错误信息
            error_text = None;
            result = Status.v341;
            locator = (By.CLASS_NAME, "summary_error_box")
            try:
                WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception as e:
                self.print_d(e);
                try:
                    errorMessage = self.driver.find_element_by_class_name("errorMessage");
                except NoSuchElementException:
                    pass
                else:
                    result = Status.o430;
                    error_text = errorMessage.text;
            else:
                summary_error_box = self.driver.find_element_by_class_name("summary_error_box");
                ul = summary_error_box.find_element_by_tag_name("ul");
                error_text = ul.text;
            if(error_text is not None):
                result['actionMsg'] = error_text;
                result['bankMsg'] = error_text;
            # try:
            #     summary_error_box = self.driver.find_element_by_class_name("summary_error_box");
            #     ul = summary_error_box.find_element_by_tag_name("ul");
            # except NoSuchElementException :
            #     self.print_d("summary_error_box:NoSuchElementException")
            #     pass
            # else:
            #     result['actionMsg'] = ul.text;
        # 确认验证码是不是正确，转账是否成功
        # try:
        #     #<div class='notifications-tr'>
        #     notiDismiss = self.driver.find_element_by_class_name("notification-dismiss");
        #     message = self.driver.find_element_by_class_name("notification-message");
        # except  NoSuchElementException as msg:
        #     self.print_d('没有验证码错误提示');
        #     # result = self.sendStatus(self.order_no, Status.v340);
        #     #TransactionSummary---confirmed
        # else:
        #     # psw
        #     self.print_d('验证码错误');
        #     result = self.sendStatus(self.order_no, Status.v341);
        #     result['actionMsg'] = message.text;
        #     notiDismiss.click();
        return result
    # exit('转账结束');
    def resend_sms_code(self):
        #https://www.maybank2u.com.my/home/m2u/common/transactions/transfer
        click_here = self.driver.find_element_by_partial_link_text("click here");
        if (click_here):
            click_here.click();
        else:
            print('没有 click here ')
        return
    def logout(self):
        result = self.sendStatus(self.order_no, Status.o400);
        try:
            profile_white = self.driver.find_element_by_css_selector("img[src^='/static/icons/profile_white']")
        except  NoSuchElementException as msg:
            print('logout时用户没找到');
            result = self.sendStatus(self.order_no, Status.o401);

        else:
            profile_white.click();
            self.sleep(1)
            try:
                unlocked_gold = self.driver.find_element_by_css_selector("img[src^='/static/icons/unlocked_gold'")
            except  NoSuchElementException as msg:
                print('logout图标没找到');
                result = self.sendStatus(self.order_no, Status.o401);
            else:
                unlocked_gold.click();
                self.quit();
                result = self.sendStatus(self.order_no, Status.o402);
        return result;
    def check_session(self,auto_click):
        has_session_note = False;
        try:
            sessionModal = self.driver.find_element_by_css_selector("div[class^='SessionModal---confirmBtn']");
        except  NoSuchElementException as msg:
            print('没有 session 提示');
        else:
            print('session 提示');
            has_session_note = True;
            if ( auto_click == True):
                btn_success = sessionModal.find_element_by_class_name('btn-success');
                btn_success.click();
        return has_session_note;
    def is_session_timeout(self,auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception as we:
            # self.print_d(we)
            self.quit()
            return True
        print(self.order_no+"--"+current_url)
        if (current_url.find("ErrorSession") > 0):
            if ( auto_quit ):
                self.quit();
            return True;
        else:
            return False;
    def test(self):
        result = Status.v332;
        # 判断转账成功
        try:
            self.driver.find_element_by_css_selector("img[src^='/static/icons/success_white']");
        except  NoSuchElementException as msg:
            print('转账没成功');
            result = Status.v341;
        else:
            # 取信息
            result = Status.v340;
            result.update({'orderMsg': ''});
            result.update({'amount': ''});
            result.update({'reference': ''});
            try:
                wordWraps = self.driver.find_elements_by_css_selector("div[class^='TransactionSummary---wordWrap']");
                principalAmount = self.driver.find_element_by_css_selector(
                    "span[class^='TransactionSummary---principalAmount']");
                if (len(wordWraps) > 3):
                    result.update['reference'] = wordWraps[2].text;
                    result.update['orderMsg'] = wordWraps[3].text;
                result['amount'] = principalAmount.text;
            except NoSuchElementException as msg:
                print('查订单信息异常')
            return result;  # 返回转账成功
        try:
            # TransactionSummary---rejected---3p7pd panel panel-default
            self.driver.find_element_by_css_selector("div[class^='TransactionSummary---rejected'");
        except  NoSuchElementException as msg:
            print('转账信息没问题');
        else:
            print('转账信息拒绝');
            result = Status.v341;
            try:
                currencys = self.driver.find_elements_by_css_selector("span[class^='TransactionSummary---currency'");
                if (currencys and len(currencys) > 1):
                    span = currencys[1].find_element_by_tag_name("span");
                if (span):
                    result['actionMsg'] = span.text
            except Exception as msg:
                print('异常');
            self.quit();
            self.action_code = result['actionCode'];
            return self.sendStatus(self.order_no, result);

        # 确认验证码是不是正确，转账是否成功
        try:
            # <div class='notifications-tr'>
            notiDismiss = self.driver.find_element_by_class_name("notification-dismiss");
            message = self.driver.find_element_by_class_name("notification-message");
        except  NoSuchElementException as msg:
            print('没有验证码错误提示');
            result = self.sendStatus(self.order_no, Status.v340);
            # TransactionSummary---confirmed
        else:
            # psw
            print('验证码错误');
            result = self.sendStatus(self.order_no, Status.v341);
            result['actionMsg'] = message.text;
            notiDismiss.click();
        return result

# 过期退出 https://www.maybank2u.com.my/home/m2u/common/logout?sessionTimeout=true
# 登录 https://www.maybank2u.com.my/home/m2u/common/login.do
# 登录成功 Account页 https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
# 转账支付页 https://www.maybank2u.com.my/home/m2u/common/transactions/pay
# 转账页 https://www.maybank2u.com.my/home/m2u/common/transactions/transfer

#session 延期h  sessionModal
#https://www.maybank2u.com.my/home/m2u/common/logout?securityQuestionFailed=Login%20Alert!%20You%20have%20two%20login%20sessions%20open%20at%20the%20same%20time.%20For%20security%20reasons,%20this%20session%20will%20be%20terminated.