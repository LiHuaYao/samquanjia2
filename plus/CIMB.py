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
class CIMB(Personification):

    def __init__(self,proxy_index=None,order_no=None):
        Personification.__init__(self)
        self.config = Config.CIMB
        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no
        self.status_path = self.config.STATUS_PATH
        self.select_click = False;
        self.psw_input = None;
        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=" + BankType.Bank[2]['val'])
        # 设置代理
        if(self.config.US_PROXY_SERVER and proxy_index is not None):
            self.proxy_index = proxy_index
            proxy = IPPool.ip_list[proxy_index]
            proxy_server = proxy.proxy
            if proxy_server.find('://') < 0:
                proxy_server = 'http://'+proxy_server
            self.print_d('使用代理：%s'%proxy_server)
            chrome_options.add_argument("--proxy-server="+proxy_server)
        else:
            self.print_d('不使用代理服务')
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
    def is_use_proxy(self):
        return self.config.US_PROXY_SERVER
    def open_and_init(self):
        try:
            # self.driver.get('http://httpbin.org/get');
            self.driver.get(self.config.OPEN_URL);
        except TimeoutException:
            print('-----CIMB--TimeoutException------')
            self.quit()
        self.print_d('新建窗口-打开页面-页面加载中')
        self.sendStatus(self.order_no,Status.o000)
        driver_process = psutil.Process(self.driver.service.process.pid)
        if driver_process:
            self.chrome_driver_process = driver_process
        children_list = driver_process.children()
        if children_list:
            self.chrome_process = children_list[0]
        # self.sendStatus(self.order_no,Status.o000);
        wait_access_time = 6
        locator = (By.ID, 'test')
        try:
            WebDriverWait(self.driver, wait_access_time, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            try:
                title = self.driver.title
                if(title.find('Access Denied') > -1):
                    self.print_d('[第一次发现Access Denied-准备刷新]')
                    self.driver.refresh()
            except NoSuchElementException:
                pass
        try:
            WebDriverWait(self.driver, wait_access_time, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            try:
                title = self.driver.title
                if(title.find('Access Denied') > -1):
                    self.print_d('[第二次发现Access Denied-准备退出]')
                    if self.proxy_index is not None:
                        proxy = IPPool.ip_list[self.proxy_index]
                        denied_count = proxy.denied_count + 1
                        proxy.denied_count = denied_count
                        if denied_count >= Config.MAX_DENIED_COUNT :
                            self.print_d('[已到Access Denied次数-准备刷新IP]')
                    self.is_open = False
                    self.quit()
                    return self.sendStatus(self.order_no,Status.o403)
            except NoSuchElementException:
                pass
        try:
            WebDriverWait(self.driver, self.config.OPEN_TIME_OUT-wait_access_time*2, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('-----CIMB页面打开异常-----')
            # print('-----CIMB页面打开异常，准备关闭-----')
            # self.quit()
            return self.sendStatus(self.order_no, Status.o002)
        try:
            locator1 = (By.CLASS_NAME, 'select2-selection--single') #操作类型下拉列表
            WebDriverWait(self.driver, self.config.FIND_USER_NAME_TIME_OUT, 0.5).until(EC.element_to_be_clickable(locator1))
        except Exception:
            self.screen(None)
            self.save_html('CIMB-error')
            try:
                title = self.driver.title
                if(title.find('Access Denied') > -1):
                    self.print_d(title)
                    body = self.driver.find_element_by_tag_name('body')
                    self.print_d(body.text)
                    status = Status.o403
                    status['actionMsg'] = body.text
                    return self.sendStatus(self.order_no,status)
            except NoSuchElementException:
                pass
            try:
                title = self.driver.find_element_by_class_name('title')
                if title.text.find('Downtime') > -1:
                    self.print_d(title)
                    msg = self.driver.find_element_by_class_name('title-msg')
                    self.print_d(msg.text)
                    status = Status.o404
                    status['actionMsg'] = "System Downtime:"+msg.text
                    return self.sendStatus(self.order_no,status)
            except NoSuchElementException:
                pass
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
    def get_tranfer_list_status(self):
        return self.tranfer_list_status;
    def to_bank(self, bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.CIMBBank[bank]
        except Exception:
            return False
        if (to_bank is not None):
            self.t_to_bank = to_bank
            return True
    # 输入用户名
    def input_user_name(self,user_name = None):
        result = self.sendStatus(self.order_no,Status.l108)
        try:
            title = self.driver.title
            if (title.find('Access Denied') > -1):
                self.print_d(title)
                body = self.driver.find_element_by_tag_name('body')
                self.print_d(body.text)
                return self.sendStatus(self.order_no, Status.o403)
        except NoSuchElementException:
            pass
        try:
            title = self.driver.find_element_by_class_name('title')
            if title.text.find('Downtime') > -1:
                self.print_d(title)
                msg = self.driver.find_element_by_class_name('title-msg')
                self.print_d(msg.text)
                status = Status.o404
                status['actionMsg'] = "System Downtime:"+msg.text
                return self.sendStatus(self.order_no, status)
        except NoSuchElementException:
            pass
        #先选择操作类型
        if(False == self.select_click ):
            try:
                locator = (By.CLASS_NAME, 'select2-selection--single')
                WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception :
                result['actionMsg'] = '找不到 I want to ...'
                self.sleep(None)
                self.save_html(str(result))
                return result;
            else:
                select = self.driver.find_element_by_class_name("select2-selection--single");
                select.click()
                self.select_click = True;
                jsString = '$(".select2-results__options").css("height", "auto")';
                self.driver.execute_script(jsString);
                time.sleep(0.4)
        try:
            locator = (By.ID, 'select2-quickstart-real-results')
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            self.print_d(str(e))
            self.sleep(None)
            self.save_html(str(e))
            return Status.o000
        select_results = self.driver.find_element_by_id('select2-quickstart-real-results');
        li_list = select_results.find_elements_by_tag_name('li');
        for li in li_list:
            #View My Dashboard/View My Accounts/Transfer Money/Pay Bills/JomPAY/Top Up
            if ( li.text.find('Accounts') > -1 ):
                li.click()
                self.select_click = True
                time.sleep(0.3)
                break;
        user_id = self.driver.find_element_by_id('user-id')
        if user_name is not None :
            self.loginUserName = user_name
        user_id.clear()
        time.sleep(0.2)
        user_id.send_keys(self.loginUserName);
        time.sleep(0.2)
        login_btn = self.driver.find_element_by_class_name('googleCapthaCls')
        login_btn.click()
        # 先查错误弹窗
        try:
            locator1 = (By.ID, 'modal-confirm-desktop')
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator1))
        except Exception:
            self.print_d("输入用户名没有错误提示")
        else:
            self.print_d("输入用户名出错")
            result = Status.l109
            try:
                alert = self.driver.find_element_by_id('modal-confirm-desktop')
            except NoSuchElementException:
                content = self.driver.find_element_by_class_name('content-confirm-desktop')
                result.update({'actionMsg': content.text})
            else:
                content = alert.find_element_by_id('content')
                result.update({'actionMsg': content.text})
            if content.text.find('try again later' ) > -1 :
                self.print_d('[Unable to login at the moment due to some connection issue.换 ip重新输入一次]')
                if self.proxy_index is not None:
                    IPPool.refresh_ips(self.proxy_index)
                try:
                    btn_yes = self.driver.find_element_by_class_name('btn-yes')
                except NoSuchElementException :
                    pass
                else:
                    btn_yes.click()
                    time.sleep(0.5)
                    #重新输入
                    self.input_user_name()
            return result
        #secure-img
        try:
            locator = (By.ID, 'secure-img')
            WebDriverWait(self.driver, 30, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('-----secure-img用户名输入异常-----')
            result =  self.sendStatus(self.order_no,Status.l109)
            self.screen(None)
            self.save_html(str(result))
        else:
            result =  self.sendStatus(self.order_no,Status.l110)
            self.tranfer_list_status = 1
        return result
    #返回用户名输入
    def back_input_name(self,userName):
        try:
            back = self.driver.find_element_by_class_name('arrow-back')
        except NoSuchElementException:
            return False
        if back.is_displayed():
            back.click()
            self.select_click = False
        self.loginUserName = userName
        return True
    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        try:
            secure_word_label = self.driver.find_element_by_class_name('secure-word-label')
            secure_word_label.click()
        except Exception:
            return Status.l119
        else:
            self.is_check = True
            time.sleep(0.3)
            self.psw_input = self.driver.find_element_by_id('password')
            return Status.l120
    # 输入密码并提交
    def input_psw_and_submit(self, userName, psw):
        if(userName != self.loginUserName):
            # 重新输入用户名登录
            self.back_input_name(userName);
            time.sleep(0.5)
            result = self.input_user_name();
            if (result['actionCode'] != Status.l110['actionCode']):
                return result
            result = self.check_and_find_psw()
            if (result['actionCode'] != Status.l120['actionCode']):
                    return result
        if( (self.is_check == False) or (self.psw_input is None) ):
            self.psw_input = self.driver.find_element_by_id('password')
        try:
            self.psw_input.send_keys(psw)
        except ElementNotInteractableException:
            self.psw_input = self.driver.find_element_by_id('password')
            self.psw_input.send_keys(psw)
        self.print_d("输入密码")
        time.sleep(0.3)
        btn_login = self.driver.find_element_by_class_name('btn-login');
        self.print_d("点击登录")
        btn_login.click();
        #先查错误弹窗
        try:
            locator1 = (By.ID,'modal-confirm-desktop')
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator1))
        except Exception:
            self.print_d("登录没有错误提示")
        else:
            self.print_d("登录出错")
            result = Status.l131
            try:
                content = self.driver.find_element_by_class_name('content-confirm-desktop')
            except NoSuchElementException:
                pass
            else:
                if content.text.find('try again later' ) > -1 :
                    self.print_d('[Unable to login at the moment due to some connection issue.按Access Denied处理]')
                    result = Status.o403
                result.update({'actionMsg': content.text})
            return result
        #登录结果
        try:
            locator = (By.CLASS_NAME, 'header-logged-desk')
            WebDriverWait(self.driver, 50, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            # 登录出错
            self.print_d("登录出错")
            print(e)
            result = Status.l131
            try:
                content = self.driver.find_element_by_class_name('content-confirm-desktop')
            except NoSuchElementException:
                pass
            else:
                result.update({'actionMsg': content.text})
        else:
            #登录成功
            self.print_d("登录成功")
            result = Status.l130
            self.tranfer_list_status = 2
        return self.sendStatus(self.order_no,result)
    def login(self):
        return ;
    def logout(self):
        result = self.sendStatus(self.order_no, Status.o400);
        try:
            logout = self.driver.find_element_by_class_name('notification-image-logout')
        except NoSuchElementException:
            result =  self.sendStatus(self.order_no, Status.o401);
            return result
        logout.click();
        return self.sendStatus(self.order_no, Status.o402);
    def goto_transfer(self):
        try:
            pay_transfer = self.driver.find_element_by_class_name('pay-transfer')
            pay_transfer.click();
        except Exception:
            return False
        time.sleep(0.3)
        try:
            transfer_monry = self.driver.find_element_by_partial_link_text('Money')
            transfer_monry.click()
        except Exception:
            return False
        return True
    def goto_account(self,is_force):
        # my-accounts
        locator = (By.CLASS_NAME, 'my-accounts')
        WebDriverWait(self.driver, 10, 0.5).until(EC.element_to_be_clickable(locator))
        jsString = '$(".app-loader").hide();'
        self.driver.execute_script(jsString)
        time.sleep(0.5)
        my_accounts = self.driver.find_element_by_class_name('my-accounts')
        if (is_force or my_accounts.get_attribute("class").find('active') < 0):
            try:
                a = my_accounts.find_element_by_tag_name('a')
                a.click();
            except ElementClickInterceptedException:
                time.sleep(0.3)
                self.driver.execute_script("arguments[0].click();", a)
    def account_list(self):
        accountList = [];
        self.print_d("取帐号列表。")
        try:
            self.goto_account(False)
        except Exception as e:
            print('-----my-accounts-----')
            print(e)
            return accountList
        try:
            locator = (By.CLASS_NAME, 'collapse-body')
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            return accountList
        collapse_body_list = self.driver.find_elements_by_class_name('collapse-body')
        for collapse in collapse_body_list:
            account = {}
            accname = collapse.find_element_by_class_name('item-list-title')
            accnum = collapse.find_element_by_class_name('item-list-subtitle')
            currency = collapse.find_element_by_class_name('currency')
            bal = collapse.find_element_by_class_name('whole-number')
            account.update({"accountName": accname.text, "accountNumber": accnum.text.replace(" ", "")})
            account.update({"currency": currency.text, "balances": bal.text})
            accountList.append(account);
        return accountList
    # 到账户的转账列表页
    def goto_account_transfer(self,accountNum):
        isFindAccount = False
        try:
            self.goto_account(False)
        except Exception as e:
            print('-----my-accounts-----')
            print(e)
        self.print_d(accountNum)
        collapse_body_list = self.driver.find_elements_by_class_name('collapse-body')
        for collapse in collapse_body_list:
            accnum = collapse.find_element_by_class_name('item-list-subtitle')
            num = accnum.text
            num = num.replace(" ", "")
            print(num)
            if(num.find(accountNum) > -1):
                account = collapse.find_element_by_tag_name('a');
                account.click();
                isFindAccount = True
                self.tranfer_list_status = 2
                break
        return isFindAccount
    def get_transfer_list(self):
        transfer_list = []
        # id=basicTableHistory
        try:
            locator = (By.ID, 'basicTableHistory')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return transfer_list
        self.tranfer_list_status = 3
        table = self.driver.find_element_by_id('basicTableHistory')
        tbody = table.find_element_by_tag_name('tbody')
        tr_list = tbody.find_elements_by_tag_name('tr')
        for tr in tr_list:
            transfer = {}
            td_list = tr.find_elements_by_tag_name('td')
            date = td_list[0].get_attribute('data-search')
            # 05 Apr 2020 10:32:07 pm
            timeArray = time.strptime(date, "%d %b %Y %H:%M:%S %p")
            timeStamp = int(time.mktime(timeArray))
            transfer['time'] = timeStamp

            details = td_list[1].get_attribute('data-search')
            transfer['details'] = details.replace(" ", "")
            # I-REMITTANCE (IBFT)||637988204|df|MEPS FUNDS TRANSFER|LEE CHUN MOE    HLBB 7034081565
            # I-PAYMENT|FPXPAY PAYDIBS SDN BHD 02|96680685||GHZWCG00SP2020022100| 7034081565
            try:
                transfer['amount'] = td_list[2].find_element_by_class_name('whole-number').text
            except NoSuchElementException:
                pass
            else:
                transfer_list.append(transfer)
        return transfer_list

    # 选择转账帐号
    def select_tranfer_info(self, info):
        self.print_d('选择转账帐号');
        pay_transfer = self.driver.find_element_by_class_name('pay-transfer')
        classes = pay_transfer.get_attribute("class");
        # print('class=%s'%classes)
        if (classes.find('active') < 0):
            self.goto_transfer()
        # 选择转账帐号
        account_number = info['accountNumber']
        try:
            locator = (By.ID, 'select2-select2optgroup-container')
            WebDriverWait(self.driver, 7, 0.5).until(EC.element_to_be_clickable(locator))
        except Exception :
            return Status.t211
        select_account = self.driver.find_element_by_id('select2-select2optgroup-container')
        # print(select_account.text)
        if (select_account.text.find(account_number) == -1):
            try:
                select_account.click()
            except StaleElementReferenceException as e:
                self.print_d(str(e))
                self.driver.execute_script("arguments[0].click();", select_account)
                time.sleep(0.3)
                select_account = self.driver.find_element_by_id('select2-select2optgroup-container')
                select_account.click()
            time.sleep(0.3)
            results = self.driver.find_element_by_id('select2-select2optgroup-results')
            item_list = results.find_elements_by_css_selector('select2-results__item')
            for item in item_list:
                if ( item.text.find(account_number) > -1 ):
                    item.click()
                    break
        return Status.t230
     # 输入转账方信息并到发送验证码
    def input_transfer_info(self, info):
        result = Status.t210;
        try:
            locator = (By.CLASS_NAME, 'icon--search')
            WebDriverWait(self.driver, 13, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            print(e)
            return result
        # transferAccount, transferAmount, transferReference
        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        transferRecipientName = info['recipientName']
        paymentType = info['paymentType']
        try:
            input_text = self.driver.find_element_by_css_selector("input[class^='input-text']")
            input_text.click()
            locator = (By.CLASS_NAME, "select2-dropdown")
            try:
                WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception as e:
                print(e)
                return result
            else:
                input_text = self.driver.find_element_by_css_selector("input[class^='input-text']")
                input_text.send_keys(transferAccount)
                result = Status.t240;
        except Exception:
            self.print_d('查找input异常， ');
            self.action_code = Status.t230['actionCode'];
            return self.sendStatus(self.order_no, Status.t230);
        self.print_d("转账信息已填:" + transferAccount + "|" + transferAmount + "|" + transferReference);
        self.action_code = Status.t242['actionCode'];
        result = self.sendStatus(self.order_no, Status.t242);
        # send-money-account
        locator = (By.CLASS_NAME, 'send-money-account')
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            print('-----send-money-account-----')
            print(e)
        else:
            Proceed = self.driver.find_element_by_class_name('send-money-account')
            Proceed.click();
        #nav-tabs-justified
        justified = self.driver.find_element_by_class_name('nav-tabs-justified')
        li_list = justified.find_elements_by_tag_name('li')
        if ( len(li_list)< 1 ):
            return result
        if(self.t_to_bank == BankType.ToBank.CIMBBank['CIMBBank']):
            li_list[0].click();
        else:
            li_list[1].click();
            #select2-bank-name-e1-container
            try:
                locator = (By.CLASS_NAME, "tab-fundtransfer")
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception as e :
                print(e)
                return result
            else:
                tab_fundtransfer = self.driver.find_element_by_class_name('tab-fundtransfer')
                arrow = tab_fundtransfer.find_element_by_class_name('select2-selection__arrow')
                arrow.click();
            #select2-search__field
            try:
                locator = (By.CLASS_NAME, "select2-search__field")
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                return result
            else:
                search = self.driver.find_element_by_class_name('select2-search__field')
                search.send_keys(self.t_to_bank)
                time.sleep(0.3)
                results = self.driver.find_element_by_class_name('select2-results')
                try:
                    li = results.find_element_by_tag_name('li')
                except NoSuchElementException:
                    return result
                else:
                    li.click()
                    time.sleep(0.3)
                cimb_radio = self.driver.find_elements_by_class_name('cimb-radio')
                #Transfer Method-[Normal Transfer|Instant Transfer]
                cimb_radio[self.config.TRANSFER_METHOD].click()
                #Payment Type
                input_cmp = self.driver.find_element_by_xpath("//select[@id='payment-type']/..")
                arrow = input_cmp.find_element_by_class_name('select2-selection__arrow')
                arrow.click()
                try:
                    locator = (By.ID, "select2-payment-type-results")
                    WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
                except Exception:
                    return result
                results = self.driver.find_element_by_id('select2-payment-type-results')
                try:
                    li_list = results.find_elements_by_tag_name('li')
                    index = BankType.PaymentType.CIMBBank[paymentType]
                    li_list[index].click()
                except Exception:
                    return result
        undefined_list = self.driver.find_elements_by_id('undefined')
        if ( len(undefined_list) > 0 ):
            undefined_list[0].send_keys(transferAmount)
            undefined_list[1].send_keys(transferReference)
            result = Status.t241;
        #提交
        cimb_container = self.driver.find_element_by_class_name('cimb-container')
        btn_submit = cimb_container.find_element_by_class_name('btn-primary')
        btn_submit.click()
        #结果
        # 异常提醒
        try:
            locator0 = (By.CLASS_NAME, 'error-modal-container')
            WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception:
            # 成功-需要更严谨的判断,下一步有判断了
            result = Status.t260
        else:
            # 异常
            error_modal = self.driver.find_element_by_class_name('error-modal-container')
            text = error_modal.find_element_by_class_name('content')
            try:
                btn_yes = error_modal.find_element_by_class_name('btn-yes')
                btn_yes.click()
            except Exception:
                pass
            result = Status.t261
            result.update({'actionMsg': text.text})
            return result
        # if( self.t_to_bank == BankType.ToBank.CIMBBank['CIMBBank'] ):
        #     result = Status.v320
        # else:
        # 有的不用先手机确认
        try:
            locator = (By.ID, "requestTAC")
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            # 先在手机上验证
            result = self.sendStatus(self.order_no, Status.v290)
            # 读取页面内容
            try:
                secureTaccontainer = self.driver.find_element_by_id('secureTaccontainer')
            except NoSuchElementException:
                pass
            else:
                tac_content = secureTaccontainer.find_element_by_class_name('tac-content')
                result['actionMsg'] = tac_content.text
            # 先返回，新线程处理
            bg = Thread(target=self.listen_action)
            bg.start();
        else:
            requestTAC = self.driver.find_element_by_id('requestTAC')
            requestTAC.click()
            result =self.sendStatus(self.order_no, Status.v320)
        return result
    def listen_action(self):
        self.print_d('listen_action..')
        app_action = False
        # 监控转账结果
        try:
            locator = (By.CLASS_NAME, "icon--success")
            WebDriverWait(self.driver, 52, 1).until(EC.visibility_of_element_located(locator))
        except Exception:
            pass
        else:
            app_action = True
        if (app_action == True):
            try:
                paybills_id = self.driver.find_element_by_class_name('paybills-id')
                total = self.driver.find_element_by_class_name('paybill-table-total')
            except NoSuchElementException:
                result = Status.v341
            else:
                try:
                    paybills_id.find_element_by_class_name('icon--success')
                    strong = paybills_id.find_element_by_tag_name('strong')
                    amount = total.find_element_by_class_name('whole-number')
                except NoSuchElementException:
                    result = Status.v341
                else:
                    if(strong.text.find('Successful') >-1 ):
                        result = Status.v340
                        result.update({'orderMsg':'successful'})
                        amount_text = amount.text
                        amount_text = amount_text.strip()
                        result.update({'amount': amount_text})
                        result.update({'reference': self.order_no})
            # 完成转账就退出
            return  self.sendStatus(self.order_no,result)
        # 超时未处理就继续发验证码
        self.sendStatus(self.order_no, Status.v315)
        # 如果超过50秒有弹窗提示，就点发验证码
        #confirm-modal-container
        #btn-yes   <a>Proceed</a>
        try:
            locator = (By.CLASS_NAME, "confirm-modal-container")
            WebDriverWait(self.driver, 4, 1).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.sendStatus(self.order_no, Status.v319)
        else:
            self.sendStatus(self.order_no, Status.v300)
            modal = self.driver.find_element_by_class_name('confirm-modal-container')
            btn_yes = modal.find_element_by_class_name('btn-yes')
            if(btn_yes.text.find('Proceed') > -1):
                btn_yes.click()
            else:
                self.sendStatus(self.order_no, Status.v319)
        try:
            locator = (By.ID, "requestTAC")
            WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.sendStatus(self.order_no, Status.v319)
        else:
            requestTAC = self.driver.find_element_by_id('requestTAC')
            requestTAC.click()
            # 异常
            try:
                locator = (By.CLASS_NAME, "error-modal-container")
                WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                self.sendStatus(self.order_no, Status.v320)
            else:
                error_modal = self.driver.find_element_by_class_name('error-modal-container')
                text = error_modal.find_element_by_class_name('content')
                result = Status.v319
                result['actionMsg'] = text.text
                self.sendStatus(self.order_no, result)
    # 输入验证码
    def input_sms_code(self, code):
        result = Status.v321;
        try:
            locator0 = (By.ID, 'input-tac-sms')
            WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception:
            return result
        else:
            input_tac_sms = self.driver.find_element_by_id('input-tac-sms')
            input_tac_sms.clear()
            time.sleep(0.3)
            input_tac_sms.send_keys(code)
            result = Status.v330
        try:
            secbutton = self.driver.find_element_by_id('secbutton')
            btn = secbutton.find_element_by_class_name('btn-primary')
            btn.click()
            result = Status.v332
        except Exception:
            return result
        #判断结果
        try:
            locator0 = (By.CLASS_NAME, 'error-modal-container')
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception:
            #成功-需要更严谨的判断
            # result = Status.v340
            #class=paybills-id
            try:
                paybills_id = self.driver.find_element_by_class_name('paybills-id')
                total = self.driver.find_element_by_class_name('paybill-table-total')
            except NoSuchElementException:
                result = Status.v341
            else:
                try:
                    paybills_id.find_element_by_class_name('icon--success')
                    strong = paybills_id.find_element_by_tag_name('strong')
                    amount = total.find_element_by_class_name('whole-number')
                except NoSuchElementException:
                    result = Status.v341
                else:
                    if(strong.text.find('Successful') >-1 ):
                        result = Status.v340
                        result.update({'orderMsg':'Successful'});
                        amount_text = amount.text
                        amount_text = amount_text.strip()
                        result.update({'amount': amount_text});
                        result.update({'reference': self.order_no});
        else:
            #异常
            error_modal = self.driver.find_element_by_class_name('error-modal-container')
            text = error_modal.find_element_by_class_name('content')
            try:
                btn_yes = error_modal.find_element_by_class_name('btn-yes')
                btn_yes.click()
            except Exception:
                pass
            result = Status.v341
            result.update({'actionMsg':text.text})
        result = self.sendStatus(self.order_no,result)
        return result
    def  sendStatus(self,order_no,status):
        from utils.client import Client
        return Client.sendStatus(order_no,status,self.status_path)
    def is_session_timeout(self,auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception :
            self.quit()
            return True
        print(self.order_no+"--"+current_url)
        if (current_url.find("logout?sessionTimeout") > 0):
            if ( auto_quit ):
                self.quit();
            return True;
        else:
            return False;