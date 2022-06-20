import time
from datetime import datetime

import psutil
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,WebDriverException, TimeoutException,UnexpectedAlertPresentException
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
from PIL import Image

class Scbeasy(Personification) :

    def __init__(self,proxy_index=None,order_no=None):
        Personification.__init__(self)
        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no
        self.tranfer_list_status = 0;
        self.config = Config.Scbeasy
        self.print_d('准备打开页面')
        self.status_path = self.config.STATUS_PATH
        #特有属性
        self.is_add_account = False;#是否已增加了转账帐号
        self.tranfer_info = {};#是否已增加了转账帐号
        self.keys_data = None ;#键盘文字列表
        self.try_sms_count = 0 ;#尝试输入转账验证码的次数
        chrome_options = ChromeOptions.get_options()
        if(self.config.USE_NO_IMAGE):
            # 无图
            No_Image_loading = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", No_Image_loading)
        if(self.config.USE_NO_FLASH is None or self.config.USE_NO_FLASH == True):
            # 禁用 flash
            Flash = {"plugins.plugins_disabled": ['Adobe Flash Player']}
            chrome_options.add_experimental_option("prefs", Flash)
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
                userName = self.driver.find_element_by_css_selector("input[name^='LOGIN']");
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
                    password = self.driver.find_element_by_css_selector("input[name^='PASSWD']");
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
                    self.login_button = self.driver.find_element_by_css_selector("input[name^='lgin']");
                except NoSuchElementException:
                    pass
                break
    def get_tranfer_list_status(self):
        return self.tranfer_list_status;
    def to_bank(self,bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.Scbeasy[bank]
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
                locator2 = (By.CSS_SELECTOR, "input[name^='LOGIN']");
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator2))
            except Exception:
                self.print_d('没找到用户名输入')
                result = self.sendStatus(self.order_no,Status.l109);
                return result
            else:
                self.print_d('已找到用户名输入')
                self.user_name_input = self.driver.find_element_by_css_selector("input[name^='LOGIN']");
                self.login_button = self.driver.find_element_by_css_selector("input[name^='lgin']");
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
                locator2 = (By.CSS_SELECTOR, "input[name^='PASSWD']");
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator2))
            except Exception:
                self.print_d('没找到密码输入')
                result = self.sendStatus(self.order_no, Status.l109);
                return result
            else:
                self.psw_input = self.driver.find_element_by_css_selector("input[name^='PASSWD']");
                self.print_d('找到密码输入');
                self.action_code = Status.l120['actionCode'];
                result = self.sendStatus(self.order_no, Status.l120);
        else:
            self.print_d('已有密码输入');
            self.action_code = Status.l120['actionCode'];
            result = self.sendStatus(self.order_no, Status.l120);
        return result
    #输入密码并提交
    def input_psw_and_submit(self,userName,psw):
        self.loginPassword = psw;
        result = Status.l120
        # 当前输入的用户名
        if (self.user_name_input is None):
            try:
                locator0 = (By.ID, "userName")
                WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator0))
            except Exception:
                return Status.l109;
            self.user_name_input = self.driver.find_element_by_id("userName");
        self.print_d(userName + "|" + self.user_name_input.text)
        if (userName != self.user_name_input.text):
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
            self.action_code = Status.l121['actionCode'];
            return self.sendStatus(self.order_no, Status.l121);
        self.psw_input.clear();
        self.psw_input.send_keys(self.loginPassword);
        self.print_d(self.loginPassword);
        self.print_d(self.psw_input);
        self.print_d('输入密码');
        result = self.sendStatus(self.order_no, Status.l122);
        time.sleep(0.4)
        try:
            if (self.login_button is None):
                self.login_button = self.driver.find_element_by_css_selector("input[name^='lgin']");
            self.login_button.click();
            self.print_d("点击登录")
        except Exception as e:
            self.print_d(e);
            return result;
        is_login = False;
        error_text = None;
        for index in range(1, 40):
            # firstpage
            current_url = self.driver.current_url
            # https://www.scbeasy.com/online/easynet/page/firstpage.aspx#
            # https://www.scbeasy.com/online/easynet/page/err/error_signon.aspx
            if (current_url.find("firstpage") > 0):
                index = 41;
                is_login = True;
                break;
            elif(current_url.find("error_signon") > 0 or current_url.find("error_asp") > 0):
                index = 41;
                is_login = False;
                # 找错误提示
                try:
                    error_text = self.driver.find_element_by_id("errorText");
                except NoSuchElementException:
                    pass;
                if (error_text is None or len(error_text) < 5):
                    try:
                        bd_en_bk_11 = self.driver.find_element_by_class_name("bd_en_bk_11");
                        b = bd_en_bk_11.find_element_by_tag_name("b");
                        error_text = b.text;
                    except NoSuchElementException:
                        pass;

            else:
                time.sleep(0.5);
        if (is_login):
            self.print_d('登录成功');
            self.tranfer_list_status = 2
            self.action_code = Status.l130['actionCode'];
            result = self.sendStatus(self.order_no, Status.l130);
        else:
            self.print_d('帐号或密码不正确');
            self.screen(None);
            result = self.sendStatus(self.order_no, Status.l131);
            if(error_text is not None):
                result['actionMsg'] = error_text;
                result['bankMsg'] = error_text;
            #返回登录页，可继续登录
            try:
                mainpage = self.driver.find_element_by_id("mainpage");
                mainpage.click();
                # .TextMainBlack a
                locator0 = (By.CLASS_NAME, "TextMainBlack")
                WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator0))
                TextMainBlack = self.driver.find_element_by_class_name("TextMainBlack");
                English = TextMainBlack.find_element_by_tag_name("a");
                English.click();
            except Exception:
                self.print_d("点击返回登录页面异常");
                self.driver.get(self.config.OPEN_URL);

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
        #判断是不是在首页
        if(self.driver.current_url.find('firstpage') < 0 ):
            #如果不是在首页就不能通过点击进入，直接跳转链接 TODO scb 不能通过链接跳转，会有 session 异常
            self.driver.get("https://www.scbeasy.com/online/easynet/page/acc/acc_mpg.aspx");
        else:
            try:
                locator0 = (By.CSS_SELECTOR, "img[alt^='My Account']")
                WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator0))
            except Exception:
                self.print_d('-页面加载异常');
                self.driver.execute_script("LoadHM('1','acc/acc_mpg.aspx');");
            else:
                myAccount = self.driver.find_element_by_css_selector("img[alt^='My Account']");
                myAccount.click();
        try:
            locator2 = (By.ID, "DataProcess_SaCaGridView");
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator2))
        except Exception:
            self.print_d('没找到-DataProcess_SaCaGridView')
            return accountList
        table = self.driver.find_element_by_id("DataProcess_SaCaGridView");
        table_list = table.find_elements_by_tag_name("table");
        self.print_d(len(table_list))
        if(len(table_list) < 2):
            return accountList;
        self.print_d(table_list[1].text)
        tbody = table_list[1].find_element_by_tag_name("tbody");
        tr_list = tbody.find_elements_by_tag_name("tr");
        if(len(tr_list) < 1):
            self.print_d('账号列表为空');
        else:
            #删除第一列 表头
            # tr_list.pop(0);
            #删除最后一列 统计
            # tr_list.pop();
            for tr in tr_list:
                # tr_inner_table = tr.find_element_by_tag_name("table");
                td_list = tr.find_elements_by_tag_name("td");
                if(len(td_list) < 5 ):
                    continue;
                account_num = td_list[1].text
                account_name = td_list[2].text
                bal = td_list[4].text
                currency = "Baht"
                if ( account_name is None or len(account_name) < 1 ):
                    account_name = account_num
                account = {};
                account.update({"accountName": account_num, "accountNumber": account_num,
                                "currency": currency, "balances": bal})
                accountList.append(account);
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

    #到转账页-汇商使用统一的手机号转账
    def goto_transfer(self):
        self.print_d('开始到PromptPay转账');
        # self.sleep(1);
        result = False;
        FundTransfer_Image = None;
        try:
            FundTransfer_Image = self.driver.find_element_by_id("FundTransfer_Image");
        except NoSuchElementException:
            self.print_d("FundTransfer_Image-NoSuchElementException")
            self.driver.execute_script("javascript:__doPostBack('ctl00$FundTransfer_LinkButton','')");
        else:
            FundTransfer_Image.click();
        # 等待页面加载
        try:
            # PromptPay
            locator2 = (By.ID, "ctl15_AnyIDTransfer_LinkButton")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator2))
        except  Exception:
            print('到转账页加载超时');
            return False
        ctl15_AnyIDTransfer_LinkButton = self.driver.find_element_by_id("ctl15_AnyIDTransfer_LinkButton");
        ctl15_AnyIDTransfer_LinkButton.click();
        # 等待页面加载
        try:
            # DataProcess_lbtnNoProfile == Click here for other PromptPay No.
            locator2 = (By.ID, "DataProcess_lbtnNoProfile")
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator2))
        except  Exception:
            print('到转账页加载超时');
            return False
        DataProcess_lbtnNoProfile = self.driver.find_element_by_id("DataProcess_lbtnNoProfile");
        try:
            DataProcess_lbtnNoProfile.click();
        except Exception:
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", DataProcess_lbtnNoProfile);
        # 等待页面加载
        try:
            # DataProcess_txtCustAccTo == PromptPay input
            locator2 = (By.ID, "DataProcess_txtCustAccTo")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator2))
        except  Exception:
            print('到转账页加载超时');
            return False
        result = True;
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
        #等待输入手机出现-异步可能还没进行到这一步
        try:
            locator2 = (By.ID, "DataProcess_txtCustAccTo")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator2))
        except  Exception:
            print('到转账页加载超时');
            #如果知道没成功就再到转账页
            if(self.is_goto_transfer == False):
                self.is_goto_transfer = self.goto_transfer();
            if(self.is_goto_transfer == False):
                # 如果超时还没到就看是不是有 Click here for other PromptPay No.有就点击
                try:
                    DataProcess_lbtnNoProfile = self.driver.find_element_by_id("DataProcess_lbtnNoProfile");
                except NoSuchElementException :
                    pass;
                    return self.sendStatus(self.order_no, Status.t209);
                else:
                    DataProcess_lbtnNoProfile.click();
                    #再等
                    try:
                        locator2 = (By.ID, "DataProcess_txtCustAccTo")
                        WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator2))
                    except  Exception:
                        return self.sendStatus(self.order_no, Status.t209);
        # DataProcess_ddlCustAccFrom  目前单账号，多账号再补；TODO
        return self.sendStatus(self.order_no, Status.t230);
        #选择转账帐号
        account_number = info['accountNumber']
        return self.sendStatus(self.order_no, Status.t230);
    #输入转账方信息并提交-该银行需要先创建帐号，这里才是转账页面
    def input_transfer_info_continue(self):
        result = Status.t210;
        info = self.tranfer_info
        payAccountNumber = info['payAccountNumber'];
        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        try:
            #Account Number
            fromAccountSelect = Select(self.driver.find_element_by_css_selector("select[name^='fromAccount']"));
            fromAccountSelect.select_by_visible_text(payAccountNumber)
            #toAccountNumber
            toAccountSelect = Select(self.driver.find_element_by_css_selector("select[name^='toAccount']"));
            toAccountIndex = -1 ;
            index = -1 ;
            for select in toAccountSelect.options:
                self.print_d(select.text);
                index = index + 1 ;
                if(select.text.find(transferAccount) > -1 ):
                    toAccountIndex = index;
                    break;
            if(toAccountIndex > -1):
                toAccountSelect.select_by_index(toAccountIndex);
            else:
                self.print_d("没找到 toAccount option")
                result = self.sendStatus(self.order_no, Status.t243);
                return result;
            #Amount (THB)
            creditAmount = self.driver.find_element_by_css_selector("input[name^='creditAmount']");
            creditAmount.send_keys(transferAmount)
            #Note
            details = self.driver.find_element_by_css_selector("textarea[name^='details']");
            details.send_keys(transferReference)
        except NoSuchElementException:
            self.print_d("输入转账信息异常")
            result = self.sendStatus(self.order_no, Status.t243);
        #提交转账，下一步
        result = self.sendStatus(self.order_no, Status.t244);
        next_list = self.driver.find_elements_by_css_selector("div[align^='center']");
        next_btn = None;
        for n in next_list:
            try:
                a = n.find_element_by_tag_name("a");
                if(a.get_attribute('href').find("JumpOnSelect") > -1):
                    next_btn = a;
            except Exception:
                pass
        if (next_btn is not None):
            next_btn.click();
            result =  self.sendStatus(self.order_no, Status.t250);
        else:
            #直接执行 js 下一步
            self.driver.execute_script("JumpOnSelect(document.FundTransferForm,1);");
        #判断结果，等待验证码
        is_success = False;
        wait_index = 0 ;
        # 成功时的标题：<h1>Other Account Funds Transfer - Review</h1>
        while wait_index < 8 :
            #出错 <font color="red">The system cannot proceed this transaction, please try again later.</font>
            try:
                font_list = self.driver.find_element_by_css_selector("font[color^='red']");
            except NoSuchElementException as e :
                pass
            else:
                for f in font_list:
                    if(len(f.text) and f.text.find("cannot") > -1):
                        result = self.sendStatus(self.order_no, Status.v315);
                        result["actionMsg"] = f.text;
                        is_success = False;
                        wait_index = 9;
                        break;
            # 通过标题判断结果
            h1 = None;
            try:
                h1 = self.driver.find_element_by_tag_name("h1")
            except NoSuchElementException:
                pass
            if(h1 is not None):
                if(h1.text.find("Review") > -1):
                    is_success = True;
                    wait_index = 9;
                    break;
                else:
                    # 检查验证码输入：<input type="password" name="secondaryPassword" maxlength="12" size="12" value="" class="dropdownlist">
                    try:
                        self.driver.find_element_by_css_selector("input[name^='secondaryPassword']");
                    except Exception as e:
                        print('-----没找到验证码输入-----')
                        is_success = False;
                    else:
                        is_success = True;
                        wait_index = 9;
                        break;
            time.sleep(0.5);
            wait_index = wait_index + 1
        #成功，需要验证码
        if(is_success):
            result = self.sendStatus(self.order_no, Status.v320);
        else:
            result = self.sendStatus(self.order_no,Status.v319)
        return result

    #输入转账方信息并提交-该银行需要先创建帐号，所以这里是创建帐号
    def input_transfer_info(self, info):
        self.print_d("输入转账信息")
        result = Status.t210;
        try:
            # 是否在PromptPay页面
            # url == https://www.scbeasy.com/online/easynet/page/ftf/ftf_any_nprf_st1.aspx
            locator = (By.ID, "DataProcess_Header_Image")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('可能没在转账页')
            return result
        self.print_d("找到DataProcess_Header_Image")
        DataProcess_Header_Image = self.driver.find_element_by_id("DataProcess_Header_Image");
        alt = DataProcess_Header_Image.get_attribute("alt");
        if(alt == "PromptPay"):
            self.print_d("是在PromptPay")
        self.tranfer_info = info
        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        self.print_d(self.t_to_bank)
        try:
            # 转账phone number
            account_number_input = self.driver.find_element_by_id("DataProcess_txtCustAccTo");
            account_number_input.clear();
            account_number_input.send_keys(transferAccount);
            time.sleep(0.2);
            # Amount
            account_number_input = self.driver.find_element_by_id("DataProcess_txtCustAmount");
            account_number_input.clear();
            account_number_input.send_keys(transferAmount);
            time.sleep(0.2);
            # Description (Optional)
            account_number_input = self.driver.find_element_by_id("DataProcess_txtCustDesc");
            account_number_input.clear();
            account_number_input.send_keys(transferReference);
            time.sleep(0.2);
        except Exception:
            self.print_d('输入转账信息异常')
            result = self.sendStatus(self.order_no, Status.t243);
            return result
        self.print_d('输入转账信息完成')
        try:
            #提交next btn
            next = self.driver.find_element_by_id("nxt");
            next.click();
        except Exception :
            self.print_d("提交按键没找到")
            # 执行 js
            js_click = "__doPostBack('ctl00$DataProcess$Next_LinkButton','')"
            self.driver.execute_script(js_click)
        # 加载并短信验证码输入
        self.print_d("信息已填准备提交");
        self.action_code = Status.t244['actionCode'];
        result = self.sendStatus(self.order_no, Status.t244);
        #判断提交结果
        is_success = True;
        wait_index = 1;
        while wait_index < 10:
            url = self.driver.current_url
            if(url.find("err_post") > -1 ):
                #异常
                is_success = False;
                wait_index = 999;
                result = self.sendStatus(self.order_no, Status.t280);
                #错误提示
                try:
                    bd_th_rd_11_pd10 = self.driver.find_element_by_class_name("bd_th_rd_11_pd10");
                    p = bd_th_rd_11_pd10.find_element_by_tag_name("p");
                    result['actionMsg'] = p.text;
                    result['bankMsg'] = p.text;
                except Exception:
                    pass;
            else:
                time.sleep(0.5);
                wait_index = wait_index + 1;
        if(is_success):
            result = self.sendStatus(self.order_no,Status.t280);
        self.screen(self.order_no+"_test");
        self.save_html();
        #检查验证码
        try:
            # 验证码输入
            locator = (By.ID, "DataProcess_txtOTPCode")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception :
            result = self.sendStatus(self.order_no, Status.t261);
            try:
                #查找异常提示
                bd_th_rd_11_pd10 = self.driver.find_element_by_class_name("bd_th_rd_11_pd10");
            except NoSuchElementException :
                pass
            else:
                result['actionMsg'] = bd_th_rd_11_pd10.text;
                result['bankMsg'] = bd_th_rd_11_pd10.text;
                #如果是 There is a problem communicating with the server.  Please try again in a moment. 返回以供重试
                if(bd_th_rd_11_pd10.text.find("communicating")> -1 and bd_th_rd_11_pd10.text.find("again")> -1):
                    DataProcess_Back_LinkButton = self.driver.find_element_by_id("DataProcess_Back_LinkButton");
                    DataProcess_Back_LinkButton.click();

            return result;
        else:
            result = self.sendStatus(self.order_no, Status.v320);
            otp = self.driver.find_element_by_id("DataProcess_txtOTPCode");
            otp.click();
            time.sleep(0.5)
            # 获取键盘图片
            DivPinPad = self.driver.find_element_by_id("DivPinPad");
            key_img = DivPinPad.find_element_by_tag_name("img");
            key_img_path = self.save_captcha(key_img);
            keys_data = self.keys_img_split(key_img_path);
            self.print_d(keys_data)
            self.keys_data = keys_data;
        try:
            # 验证码识别
            DataProcess_lbOTPRefNo = self.driver.find_element_by_id("DataProcess_lbOTPRefNo");
            result["refno"] = DataProcess_lbOTPRefNo.text;
        except Exception :
            pass;
        return result;

    ##输入新建帐号验证码
    def input_add_sms_code (self,code):
        self.print_d("input_add_sms_code")
        result = self.sendStatus(self.order_no, Status.t291);
        locator2 = (By.CSS_SELECTOR, "input[name^='secondPassword']")
        try:
            WebDriverWait(self.driver, 6, 0.5).until(EC.element_to_be_clickable(locator2))
        except Exception:
            self.print_d(result['actionMsg']);
            return result
        secondPassword = self.driver.find_element_by_css_selector("input[name^='secondPassword']");
        secondPassword.send_keys(code);
        btnConfirm = self.driver.find_element_by_css_selector("input[name^='btnConfirm']");
        btnConfirm.click()
        #查找结果
        is_success = False;
        wait_index = 1;
        while wait_index < 8 :
            h1 = None;
            try:
                h1 = self.driver.find_element_by_tag_name("h1")
                # 错误时的内容： Create New Other Account - Review
            except NoSuchElementException:
                pass
            if(h1 is not None):
                if(h1.text.find("Review") > -1):
                    #还在输入验证码页
                    #判断错误提示
                    try:
                        sec_body = self.driver.find_element_by_xpath("//input[@name='secondPassword']/..");
                        font = sec_body.find_element_by_tag_name("font")
                    except NoSuchElementException:
                        self.print_d("没找到错误提示")
                    else:
                        result = self.sendStatus(self.order_no, Status.t291);
                        result['actionMsg'] = font.text;
                        is_success = False;
                        wait_index = 10
                        break;

                elif(h1.text.find("Transfer") > -1):
                    is_success = True;
            time.sleep(0.5)
            wait_index = wait_index+1
        if(is_success == True):
            self.is_add_account = True;
            result = self.sendStatus(self.order_no, Status.t292);
        return result

    def keys_img_split(self,keys_img_path):
        self.print_d("图片分割："+keys_img_path);
        keys_data = "";
        img = Image.open(keys_img_path);
        pic_w = 300;
        pic_h = 300;
        s_x = 8;
        s_y = 8;
        w = 21;
        h = 25;
        limit_x = 7;
        limit_y = 3;
        x = s_x;
        y = s_y;
        for i in range(0, 10):
            end_x = x + w;
            end_y = y + h;
            pic = img.crop((x, y, end_x, end_y));
            print(x, y, end_x, end_y)
            pic = pic.resize((pic_w, pic_h), Image.ANTIALIAS)
            path = Config.SCREEN + self.order_no+"-k" + str(i) + ".png";
            pic.save(path, quality=95, dpi=(72, 72));
            num = self.ocr_keys(path);
            if(num is None or len(num) < 1):
                num = "?";
            keys_data=keys_data+num;
            x = end_x + limit_x;
            if (x > img.size[0] - w):
                y = s_y + h + limit_y;
                x = s_x;
            if (y > img.size[1] + h):
                break;
        return keys_data;

    def ocr_keys(self,imgPath):
        import requests
        import base64

        num = '?';
        '''
        数字识别
        '''

        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/numbers"
        # 二进制方式打开图片文件
        f = open(imgPath, 'rb')
        img = base64.b64encode(f.read())

        params = {"image": img}
        access_token = Config.BAI_DU_ACCESS_TOKEN;
        request_url = request_url + "?access_token=" + access_token
        # headers = {'content-type': 'application/x-www-form-urlencoded', 'Connection':'close'}
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.post(request_url, data=params, headers=headers)
        data = None;
        if response:
            data = response.json();
        try:
            if (data is not None and data['words_result_num'] > 0):
                words_result = data['words_result'];
                num = words_result[0]['words'];
        except Exception:
            print(data);
            pass;
        return num

    ##输入验证码
    def input_sms_code (self,code):
        self.action_code = Status.v321['actionCode'];
        self.try_sms_count = self.try_sms_count +1;
        result = self.sendStatus(self.order_no,Status.v321);
        #判断页面超时
        if ( self.is_session_timeout(True) ):
            self.action_code = Status.o410['actionCode'];
            result = self.sendStatus(self.order_no, Status.o410);
            return result
        try:
            otp = self.driver.find_element_by_id("DataProcess_txtOTPCode");
        except  NoSuchElementException as msg:
            self.print_d('查找 otp输入 异常。');
            self.action_code = Status.v322['actionCode'];
            return  self.sendStatus(self.order_no, Status.v322);
        else:
            self.print_d("已找到 otp")
        # code = input("请输入收到的短信验证码:")
        self.print_d("验证码:%s"%code);
        try:
            # otp.click();
            self.driver.execute_script("DynamicPinpad_Reset()");
        except Exception as e:
            self.print_d('fail清空输入框:'+str(e));
        #第一次输入时可能要等待图片识别结果返回
        wait_keys_index = 0 ;
        if (self.try_sms_count > 1):
            wait_keys_index = 999;
        while wait_keys_index < 20 :
            if (self.keys_data is not None):
                wait_keys_index = 999;
                break;
            wait_keys_index = wait_keys_index+1;
            time.sleep(0.5)
        #如果还是空就现在识别键盘图片
        if( self.keys_data is None):
           # 获取键盘图片
           DivPinPad = self.driver.find_element_by_id("DivPinPad");
           key_img = DivPinPad.find_element_by_tag_name("img");
           key_img_path = self.save_captcha(key_img);
           keys_data = self.keys_img_split(key_img_path);
           self.print_d(keys_data)
           self.keys_data = keys_data;
        result = self.sendStatus(self.order_no, Status.v330);
        # 输入验证码，汇商不能直接输，先调用 js 实现
        # js 输入
        last_none_index = 0;
        for c in code:
            index = self.keys_data.find(c);
            if(index == -1):
                index = self.keys_data.find("?",last_none_index);
                last_none_index = index+1;
            input_js = "DynamicPinpad_Add("+str(index)+")";
            self.print_d(c+"|"+str(index)+"|"+input_js);
            self.driver.execute_script(input_js);
        # 点击 OK
        self.driver.execute_script("document.getElementById('DivPinPad').style.visibility='hidden'");
        #点击操作输入
        # map = self.driver.find_element_by_tag_name("map");
        # area_list = map.find_elements_by_tag_name("area");
        # if (len(area_list) < 10):
        #     self.print_d("area_list长度不对")
        #     return result;
        # for c in code:
        #     c = int(c);
        #     area_list[c].click();
        # self.screen(self.order_no+"click_sms_code");
        # # 点击 OK
        # area_list[10].click();
        # self.screen(self.order_no + "click_sms_code_ok");

        self.action_code = Status.v330['actionCode'];
        result = self.sendStatus(self.order_no, Status.v334);
        # Please double check the account name before continue.
        # TODO 对比账户名是否一致
        # DataProcess_ltCustAccToName = self.driver.find_element_by_id("DataProcess_ltCustAccToName");
        time.sleep(0.5);
        try:
            confirmBtn = self.driver.find_element_by_id("cnfrm");
        except  NoSuchElementException as msg:
            print('查找btnSubmit异常 %s'%msg);
            return self.sendStatus(self.order_no, Status.v331);

        self.print_d('找到 btnSubmit');
        is_success = False;
        error_text = '';
        wait_index = 0;
        # 确认
        confirmBtn.click();
        # 判断失败
        try:
            # 获取alert对话框
            dig_alert = self.driver.switch_to.alert
            error_text = dig_alert.text;
            dig_alert.accept()
        except Exception as e:
            self.print_d("获取Alert对话框=异常：");
            self.print_d(str(e));
        else:
            is_success = False;
            wait_index = 999;
        self.action_code = Status.v332['actionCode'];
        result = self.sendStatus(self.order_no, Status.v332);
        time.sleep(0.5);

        # 判断结果和异常
        while wait_index < 10 :
            #判断成功
            try:
                #当前步骤
                stp_a = self.driver.find_element_by_class_name("stp_a");
            except NoSuchElementException:
                # 错误提示
                try:
                    bd_th_rd_11_pd10 = self.driver.find_element_by_class_name("bd_th_rd_11_pd10");
                    p = bd_th_rd_11_pd10.find_element_by_tag_name("p");
                    error_text = p.text;
                except Exception:
                    pass;
                wait_index = wait_index + 1;
                time.sleep(0.5);
                continue;
            self.print_d(stp_a.text);
            if (stp_a.text.find("3") > -1 or stp_a.text.find("Acknowledgements") > -1):
                #加多一个成功判断
                try:
                    self.driver.find_element_by_id("saveFav");
                except NoSuchElementException:
                    self.print_d("转账结果没找到saveFav。")
                else:
                    is_success = True;
                    wait_index = 999;
                    break;
            #判断失败

            # 判断页面超时
            if (self.is_session_timeout(True)):
                self.action_code = Status.o410['actionCode'];
                result = self.sendStatus(self.order_no, Status.o410);
                is_success = False;
                wait_index = 999;
                break;
            # 判断异常
            try:
                font = self.driver.find_element_by_tag_name("font")
            except NoSuchElementException as e :
                pass
            else:
                if(font.text.find("unexpected") > -1):
                    #需要重新登录 TODO
                    result = self.sendStatus(self.order_no, Status.o430);
                    wait_index = 999;
                    break;
            time.sleep(0.5);
            wait_index = wait_index+1;
        self.screen();
        self.save_html();
        if (is_success):
            result = self.sendStatus(self.order_no, Status.v340);
            # 取转账结果信息
            result['orderMsg'] = 'Successful';
            result['amount'] = '';
            result['reference'] = '';
            try:
                Data = self.driver.find_element_by_id("Data");
                val_list = Data.find_elements_by_class_name("bd_th_blk_11");
                for val in val_list :
                    if(val.text.find(self.tranfer_info['amount'])>-1):
                        result['amount'] = self.tranfer_info['amount'];
                    elif(val.text.find(self.tranfer_info['reference'])>-1):
                        result['reference'] = self.tranfer_info['reference'];
            except Exception:
                pass;

            #自动补全

            if (len(result['amount']) < 1):
                self.print_d("--------自动补全amount-------");
                result['amount'] = self.tranfer_info['amount'];
            if (len(result['reference']) < 1):
                self.print_d("--------自动补全reference-------");
                result['reference'] = self.tranfer_info['reference'];

            result['amount'] = self.format_amount(result['amount'])
        else:
            # 清空键盘识别结果
            self.keys_data = None;
            if(result['actionCode'] < Status.v340['actionCode']):
                result = self.sendStatus(self.order_no, Status.v341);
            result['actionMsg'] = error_text;
            result['bankMsg'] = error_text;

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
            self.quit()
            return True
        self.print_d(self.order_no+"--"+current_url);
        #https://www.scbeasy.com/online/easynet/page/err/err_session.aspx?err_code=1&lang=E
        if (current_url.find("err_session") > 0):
            if ( auto_quit ):
                self.quit();
            return True;
        else:
            return False;
    def test(self):
        result = Status.v332;
        return result