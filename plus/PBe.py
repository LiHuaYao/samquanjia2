import psutil
from selenium.webdriver.chrome.service import Service

from model.BankType import BankType
from model.IPPool import IPPool
from plus.ChromeOptions import ChromeOptions
from plus.Personification import Personification
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from config import Config
from dao.Status import Status

class PBe(Personification):

    def __init__(self,proxy_index=None,order_no=None):
        Personification.__init__(self)
        self.config = Config.PBebank
        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no
        self.status_path = self.config.STATUS_PATH
        self.user_name_input = None
        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=" + BankType.Bank[3]['val'])
        self.print_d('新建窗口-准备获取Chrome')
        if ( self.config.US_PROXY_SERVER and proxy_index is not None):
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
        # self.driver.delete_all_cookies()
        self.open_and_init()
    def is_use_proxy(self):
        return self.config.US_PROXY_SERVER
    def open_and_init(self):
       try:
           self.driver.get(self.config.OPEN_URL);
       except TimeoutException as te:
           print(te)
           self.quit();
           return False
       # self.sleep(5)
       self.print_d('新建窗口-打开页面-页面加载中')
       if self.order_no:
           self.sendStatus(self.order_no, Status.o001)
       wait_time = int(self.config.OPEN_TIME_OUT*0.8)
       try:
           locator0 = (By.ID, 'new-ebank-container')
           WebDriverWait(self.driver, wait_time, 0.5).until(EC.visibility_of_element_located(locator0))
       except Exception:
           self.print_d('新建窗口-页面加载异常-1')
           return False
       self.driver.switch_to.frame("new-ebank-container");
       try:
           locator0 = (By.ID, 'iframe1')
           WebDriverWait(self.driver, self.config.OPEN_TIME_OUT-wait_time, 0.5).until(EC.visibility_of_element_located(locator0))
       except Exception:
           self.print_d('新建窗口-页面加载异常-2')
           return False
       self.driver.switch_to.frame("iframe1");
       self.is_open = True
       self.print_d('新建窗口-页面加载完成')
       self.open_code = Status.o001['actionCode']
       if self.order_no:
           self.sendStatus(self.order_no, Status.o001)
       self.print_d('新建窗口-打开页面-页面加载中')
       if self.order_no:
           self.sendStatus(self.order_no, Status.o000)
       # 进程对象
       driver_process = psutil.Process(self.driver.service.process.pid)
       if driver_process:
           self.chrome_driver_process = driver_process
       children_list = driver_process.children()
       if children_list:
           self.chrome_process = children_list[0]
       try:
           locator = (By.CLASS_NAME, 'placeholder-no-fix') #用户名输入框
           WebDriverWait(self.driver, 30, 0.5).until(EC.visibility_of_element_located(locator))
       except Exception as e:
           print('-----placeholder-no-fix-----')
           print(e)
       else:
           self.user_name_input = self.driver.find_element_by_class_name('placeholder-no-fix');
           # self.is_open = True
       return self.is_open
    #输入安全问题
    def input_answer(self,answer):
        try:
            locator0 = (By.CSS_SELECTOR, "input[name^='USER_ANSWER'")
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception:
            return Status.l144
        user_answer =self.driver.find_element_by_css_selector("input[name^='USER_ANSWER'")
        user_answer.send_keys(answer)
        time.sleep(0.3)
        try:
            submit = self.driver.find_element_by_css_selector("button[type^='submit'")
        except NoSuchElementException:
            jsString = "doSubmit();"
            self.driver.execute_script(jsString)
        else:
            submit.click()
        try:
            locator = (By.CLASS_NAME, 'page-title')
            WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            # 登录出错
            self.print_d("登录超时-1")
            # 判断是否 Login Failed.
            try:
                logout = self.driver.find_element_by_class_name('logout')
            except NoSuchElementException:
                result = self.sendStatus(self.order_no, Status.l131)
                result['actionMsg'] = '登录超时'
            else:
                title = logout.find_element_by_id('title')
                if (title.text.find('Access Denied') > -1):
                    result = Status.o403
                description = logout.find_element_by_id('description')
                result['actionMsg'] = description.text
        else:
            # 登录成功
            self.print_d("登录成功-2")
            result = self.sendStatus(self.order_no, Status.l130)
        return result
    # 输入用户名
    def input_user_name(self,user_name = None):
        result = self.sendStatus(self.order_no,Status.l108)
        current_url = self.driver.current_url
        if( current_url.find('servlet/BxxxServle') == -1 and current_url.find('www.pbebank') > 0 ):
            self.user_name_input = None
            self.open_and_init()
        if (self.user_name_input is None):
            try:
                locator = (By.CLASS_NAME, 'placeholder-no-fix')
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                result = self.sendStatus(self.order_no, Status.l109)
                self.print_d('没找到用户名输入')
                result['actionMsg'] = '没找到用户名输入'
                return result
            else:
                user_id = self.driver.find_element_by_class_name('placeholder-no-fix')
        else:
            user_id = self.user_name_input
        if user_name is not None :
            self.loginUserName = user_name
        try:
            user_id.send_keys(self.loginUserName)
        except StaleElementReferenceException :
            try:
                user_id = self.driver.find_element_by_class_name('placeholder-no-fix')
            except NoSuchElementException:
                self.driver.switch_to.frame("iframe1");
                time.sleep(0.3)
                user_id = self.driver.find_element_by_class_name('placeholder-no-fix')
            user_id.send_keys(self.loginUserName)
        nextBtn = self.driver.find_element_by_id('NextBtn');
        nextBtn.click()
        #countSecW
        try:
            locator = (By.CLASS_NAME, 'countSecW')
            WebDriverWait(self.driver, 30, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            print('-----countSecW-----')
            result = self.sendStatus(self.order_no,Status.l109)
        else:
            result = self.sendStatus(self.order_no,Status.l110)
            self.tranfer_list_status = 1
        return result
    #返回用户名输入
    def back_input_name(self,userName):
        try:
            back = self.driver.find_element_by_id('Back')
        except NoSuchElementException :
            return False
        else:
            back.click();
            self.user_name_input = None;
            self.loginUserName = userName;
            return True
    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        try:
            locator = (By.ID, 'phrase_image')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            return False
        jsString = 'clickLabelAndChange("YES");'
        self.driver.execute_script(jsString);
        self.is_check = True
        time.sleep(0.4)
        try:
            password = self.driver.find_element_by_id('password')
        except NoSuchElementException:
            pass
        else:
            self.psw_input = password
        return True
    # 输入密码并提交
    def input_psw_and_submit(self, userName, psw):
        result = self.sendStatus(self.order_no,Status.l120)
        current_url = self.driver.current_url
        if (current_url.find('servlet/BxxxServle') == -1 and current_url.find('www.pbebank') > 0):
            result = Status.o410
            return result
        # test
        if (userName == 'test123456'):
            return Status.o403
        if (userName != self.loginUserName):
            # 重新输入用户名登录
            self.back_input_name(userName);
            time.sleep(0.5)
            result = self.input_user_name();
            if (result['actionCode'] != Status.l110['actionCode']):
                return self.sendStatus(self.order_no,result)
            result = self.check_and_find_psw()
            if (result['actionCode'] != Status.l120['actionCode']):
                return self.sendStatus(self.order_no,result)
        if ((self.is_check == False) or (self.psw_input is None)):
            self.psw_input = self.driver.find_element_by_id('password')
        self.psw_input.send_keys(psw)
        result = self.sendStatus(self.order_no,Status.l122)
        time.sleep(0.3)
        SubmitBtn = self.driver.find_element_by_id('SubmitBtn');
        self.print_d("点击登录")
        SubmitBtn.click();
        # 登录结果
        try:
            locator = (By.ID, 'hiddenErrorMessage')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception :
            #密码应该对了，就看能不能验证，顺利进去了
            pass
        else:
            self.print_d("登录出错-帐号密码问题")
            result = self.sendStatus(self.order_no,Status.l131)
            try:
                hiddenErrorMessage = self.driver.find_element_by_id('hiddenErrorMessage')
            except NoSuchElementException:
                pass
            else:
                result.update({'actionMsg': hiddenErrorMessage.text})
            return result
        #看能不能通过验证，顺利进到页面
        try:
            locator = (By.ID, 'new-ebank-container')
            WebDriverWait(self.driver, 40, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            # 登录超时
            self.print_d("登录超时-0")
            result = self.sendStatus(self.order_no,Status.l131)
            result['actionMsg'] = '登录超时'
            # 判断是否 Login Failed.
            try:
                logout = self.driver.find_element_by_class_name('logout')
            except NoSuchElementException:
                pass
            else:
                title = logout.find_element_by_id('title')
                if(title.text.find('Access Denied') > -1):
                    result = Status.o403
                    if self.proxy_index :
                        proxy = IPPool.ip_list[self.proxy_index]
                        denied_count = proxy.denied_count + 1
                        proxy.denied_count = denied_count
                        if denied_count >= Config.MAX_DENIED_COUNT:
                            self.print_d('[已到Access Denied次数-准备刷新IP]')
                            IPPool.refresh_ips(self.proxy_index)
                description = logout.find_element_by_id('description')
                result['actionMsg'] = description.text
            return result
        else:
            # 登录成功
            self.print_d("登录成功-0")
            self.driver.switch_to.frame("new-ebank-container")
            try:
                # self.print_d('title1=%s' % self.driver.title)
                this_title = self.driver.find_element_by_tag_name('title')
                # self.print_d('title2=%s' % this_title.text)
            except NoSuchElementException as e:
                self.print_d(e)
            # id:DuplicateLoginDialog  button  Proceed to login
            try:
                locator3 = (By.ID, 'DuplicateLoginDialog')
                WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator3))
            except Exception:
                self.print_d('可能需要刷新')
                # title_1 = self.driver.title
                title_2 = None
                title_3 = None

                self.print_d('title1=%s' %self.driver.title)
                try:
                    title_3 = self.driver.find_element_by_id('title')
                    this_title = title_3
                    self.print_d('title3=%s' %title_3.text)
                except NoSuchElementException:
                    pass
                try:
                    # self.driver.switch_to.default_content()
                    title_2 = self.driver.find_element_by_tag_name('title')
                    self.print_d('title2=%s'%title_2.text)
                except Exception:
                    try:
                        no_js = self.driver.find_element_by_class_name('no-js')
                        no_js.find_element_by_tag_name('title')
                    except NoSuchElementException:
                        pass
                # this_title = title_1
                if title_2 is not None and len(title_2.text) > 1:
                    this_title = title_2
                self.print_d('title=%s'%this_title)
                # 判断 Access Denied
                if (this_title.text.find('Denied') > -1):
                    self.print_d('Access Denied')
                    result = Status.o403
                    try:
                        description = self.driver.find_element_by_id('description')
                    except NoSuchElementException:
                        pass
                    else:
                        result['actionMsg'] = description.text
                    return result
                elif this_title.text.find('Failed') > -1:
                    # 判断 Login Failed.
                    self.print_d('Login Failed.')
                    result = self.sendStatus(self.order_no, Status.l131)
                    try:
                        description = self.driver.find_element_by_id('description')
                    except NoSuchElementException:
                        result['actionMsg'] = this_title.text
                    else:
                        result['actionMsg'] = description.text
                    return result
                else :
                    try:
                        page_name = self.driver.find_element_by_class_name('page-name')
                    except NoSuchElementException:
                        pass
                    else:
                        page_text = page_name.text
                        if (page_text.find('Question') > -1):
                            # 安全问题
                            self.print_d('触发安全问题')
                            result = Status.l140
                            try:
                                form_horizontal = self.driver.find_element_by_class_name('form-horizontal')
                                label_inline = form_horizontal.find_element_by_class_name('label-inline')
                            except NoSuchElementException:
                                pass
                            else:
                                result['question'] = 'question';
                                result['securityQuestion'] = label_inline.text
                                return result
                try:
                    locator = (By.CLASS_NAME, 'page-title')
                    WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
                except Exception:
                    #self.driver.refresh()
                    # src = container.get_attribute('src')
                    try:
                        jsString = "document.getElementById('new-ebank-container').contentWindow.location.reload(true)"
                        self.driver.execute_script(jsString)
                    except Exception:
                        pass
                    time.sleep(2)
                else:
                    # 登录成功
                    self.print_d("登录成功-2")
                    result = self.sendStatus(self.order_no, Status.l130)

                try:
                    DuplicateLoginDialog = self.driver.find_element_by_id('DuplicateLoginDialog')
                except NoSuchElementException:
                    try:
                        self.driver.find_element_by_id('header_task_bar')
                    except NoSuchElementException:
                        self.print_d("登录出错")
                        result = self.sendStatus(self.order_no, Status.l131)
                    else:
                        self.print_d("登录成功-1")
                        self.tranfer_list_status = 2
                        result = self.sendStatus(self.order_no, Status.l130)
                    return result
                else:
                    self.print_d("Proceed to login")
                    button = DuplicateLoginDialog.find_element_by_class_name('red')
                    button.click();
            else:
                DuplicateLoginDialog = self.driver.find_element_by_id('DuplicateLoginDialog')
                self.print_d("Proceed to login")
                button = DuplicateLoginDialog.find_element_by_class_name('red')
                button.click();
            try:
                locator = (By.CLASS_NAME, 'page-title')
                WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception as e:
                # 登录出错
                self.print_d("登录超时-1")
                # 判断是否 Login Failed.
                try:
                    logout = self.driver.find_element_by_class_name('logout')
                except NoSuchElementException:
                    result = self.sendStatus(self.order_no, Status.l131)
                    result['actionMsg'] = '登录超时'
                else:
                    title = logout.find_element_by_id('title')
                    if (title.text.find('Access Denied') > -1):
                        result = Status.o403
                    description = logout.find_element_by_id('description')
                    result['actionMsg'] = description.text
            else:
                # 登录成功
                self.print_d("登录成功-2")
                result = self.sendStatus(self.order_no,Status.l130)
                # self.driver.switch_to.frame("new-ebank-container");
        return result
    def logout(self):
        result = self.sendStatus(self.order_no,Status.o400)
        try:
            locator = (By.ID, 'header_task_bar')
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            result = self.sendStatus(self.order_no,Status.o401)
        else:
            header_task_bar = self.driver.find_element_by_id('header_task_bar')
            logout = header_task_bar.find_element_by_tag_name('a')
            logout.click();
            #logout
            try:
                locator = (By.CLASS_NAME, 'logout')
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                result = self.sendStatus(self.order_no,Status.o401)
            else:
                result = self.sendStatus(self.order_no,Status.o402)
                try:
                    title = self.driver.find_element_by_id('title')
                    result['actionMsg'] = title.text
                    self.quit()
                except Exception:
                    pass
        return result
    def to_bank(self, bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.PublicBank[bank]
        except Exception:
            return False
        if (to_bank is not None):
            self.t_to_bank = to_bank
            return True
    #登录
    def login(self):
        return ;
    def goto_transfer(self):
        #TRANSFER
        transfer = None;
        try:
            transfer = self.driver.find_element_by_partial_link_text('Transfer')
        except NoSuchElementException:
            print('------TRANSFER-----')
            try:
                themmenu = self.driver.find_element_by_id('themmenu')
            except NoSuchElementException:
                pass
            else:
                img = themmenu.find_element_by_tag_name('img')
                img.click()
                time.sleep(0.5)
                try:
                    TRANSFER = self.driver.find_element_by_partial_link_text('TRANSFER')
                except NoSuchElementException:
                    pass
        if(transfer is None):
            return False
        transfer.click()

        if(self.t_to_bank == BankType.ToBank.PublicBank['PublicBank']):
            #PB Account
            PB_Account = self.driver.find_element_by_partial_link_text('PB Account')
            PB_Account.click()
            try:
                locator = (By.PARTIAL_LINK_TEXT, 'To Other')
                WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                return
            # To Other Account
            To_Other = self.driver.find_element_by_partial_link_text('To Other')
            To_Other.click()
        else:
            #Other Bank Account
            Other_Bank = self.driver.find_element_by_partial_link_text('Other Bank')
            Other_Bank.click()
            try:
                locator = (By.PARTIAL_LINK_TEXT, 'Instant')
                WebDriverWait(self.driver, 14, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                return
            # Instant Transfer
            Instant = self.driver.find_element_by_partial_link_text('Instant')
            Instant.click()
            time.sleep(0.3)
            # To Other Account
            To_Other = self.driver.find_element_by_partial_link_text('To Other')
            To_Other.click()
        return
    def account_list(self):
        self.print_d("account_list.")
        accountList = [];
        try:
            ACCOUNT = self.driver.find_element_by_partial_link_text('ACCOUNT')
        except NoSuchElementException:
            print('------ACCOUNT-----')
        else:
            # print(len(ACCOUNT))
            div = ACCOUNT.find_element_by_tag_name('div')
            div.click()
            try:
                locator = (By.ID, 'table-column-toggle1')
                WebDriverWait(self.driver, 14, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                return accountList
            table = self.driver.find_element_by_id('table-column-toggle1')

            tr_list = table.find_elements_by_tag_name('tr')
            for tr in tr_list:
                account = {}
                td_list = tr.find_elements_by_tag_name('td')
                if (len(td_list) > 4):
                    number = td_list[0].text
                    number = number.splitlines()[0]
                    account.update({"accountName": "None", "accountNumber": number})
                    account.update({"currency": td_list[3].text, "balances": td_list[4].text})
                    accountList.append(account);
        return accountList
    # 选择转账帐号
    def select_tranfer_info(self, info):
        #TODO 目前只发现一个账号，已经默认选择了；多个账号情况需要明确好再开发
        account_number = info['accountNumber']
        try:
            locator = (By.CSS_SELECTOR, "select[name^='FROM_ACC_NO']")
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return Status.t211
        select = self.driver.find_element_by_css_selector("select[name^='FROM_ACC_NO']")
        Select(select).select_by_value(account_number)
        return Status.t230
     #输入转入账号、转账金额、备注等信息并到发送验证码
    def input_transfer_info(self, info):
        result = Status.t210
        try:
            locator = (By.CSS_SELECTOR, "input[name^='TRANSACTION_AMT'")
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('可能没在转账页')
            return result
        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        transferRecipientName = info['recipientName']
        paymentType = info['paymentType']
        if (self.t_to_bank == BankType.ToBank.PublicBank['PublicBank']):
            # Account No
            input = self.driver.find_element_by_css_selector("input[name^='TO_ACC_NO'")
            input.send_keys(transferAccount)
            result = Status.t240
            time.sleep(0.2)
            # Reference
            input = self.driver.find_element_by_css_selector("input[name^='RECIPIENT_REF'")
            input.send_keys(transferReference)
            time.sleep(0.2)
            #amount
            input = self.driver.find_element_by_css_selector("input[name^='TRANSACTION_AMT'")
            input.send_keys(transferAmount)
            time.sleep(0.2)
        else:
            select = self.driver.find_element_by_css_selector("select[name^='TO_BANK_NBR']")
            Select(select).select_by_value(self.t_to_bank)
            result = Status.t230
            time.sleep(0.2)
            input = self.driver.find_element_by_css_selector("input[name^='BENE_ACC_NO'")
            input.send_keys(transferAccount)
            result = Status.t240
            time.sleep(0.2)
            input = self.driver.find_element_by_css_selector("input[name^='RECIPIENT_REFERENCE'")
            input.send_keys(transferReference)
            time.sleep(0.2)
            input = self.driver.find_element_by_css_selector("input[name^='PAYMENT_REFERENCE'")
            input.send_keys(transferRecipientName)
            time.sleep(0.2)
            input = self.driver.find_element_by_css_selector("input[name^='TRANSACTION_AMT'")
            input.send_keys(transferAmount)
            time.sleep(0.2)
            select = self.driver.find_element_by_css_selector("select[name^='PAYMENT_TYPE'")
            Select(select).select_by_value(BankType.PaymentType.PublicBank[paymentType])
        result = Status.t244
        #提交
        jsString = 'javascript:doSubmit();'
        self.driver.execute_script(jsString);
        result = Status.t250
        #结果
        try:
            locator = (By.ID, 'errorMsg')
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            pass
        else:
            result = Status.t261
            try:
                errorMsg = self.driver.find_element_by_id('errorMsg')
                result['actionMsg'] = errorMsg.text;
            except Exception:
                pass
            return result
        # form-horizontal
        try:
            locator = (By.CLASS_NAME, 'form-horizontal')
            WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return
        #发送验证码
        result = Status.v315
        form_actions = self.driver.find_element_by_class_name('form-actions')
        button_list = form_actions.find_elements_by_tag_name('button')
        if (len(button_list) > 3):
            button_list[2].click()
            try:
                locator = (By.ID, 'pac_iframe')
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                result = Status.v319
                return result
            else:
                modal_dialog = self.driver.find_element_by_xpath("//div[@id='pac_iframe']/..")
                result = Status.v320
                try:
                    locator = (By.CSS_SELECTOR, "input[name^='SECFA']")
                    WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
                except Exception as e:
                    print("--------input[name^='SECFA'-----------")
                close = modal_dialog.find_element_by_tag_name('button')
                close.click();
        return result
    ##输入验证码
    def input_sms_code(self, code):
        result = self.sendStatus(self.order_no,Status.v330)
        try:
            locator = (By.CSS_SELECTOR, "input[name^='SECFA']")
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return result
        SECFA = self.driver.find_element_by_css_selector("input[name^='SECFA']")
        try:
            SECFA.send_keys(code)
            form_actions = self.driver.find_element_by_class_name('form-actions')
            button_list = form_actions.find_elements_by_tag_name('button')
        except Exception:
            return result
        try:
            if ( len(button_list) > 3):
                button_list[3].click()
        except Exception:
            result = Status.v333
            return result
        else:
            result = Status.v334
        #结果
        try:
            locator = (By.CLASS_NAME, 'page-name')
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            #可能成功，需要更严谨判断
            result = Status.v340
            self.save_html("支付成功页面源码")
            return result
        else:
            #（非pub to pub）肯定出错了
            #pub to pub 不能认为出错
            page_name = self.driver.find_element_by_class_name('page-name')
            if page_name.text.find('Other PB') > 0:
                try:
                    inner_note_message = self.driver.find_element_by_class_name('inner-note-message')
                except NoSuchElementException:
                    pass
                else:
                    result = Status.v340
                    result['actionMsg'] = inner_note_message.text
                    result['orderMsg'] = 'Successful'
                    try:
                        form = self.driver.find_element_by_class_name('form-horizontal')
                        result['amount'] = 0 ;
                        row_list = form.find_elements_by_class_name('row')
                        if len(row_list) > 5:
                            row_5 = row_list[5]
                            reference = row_5.find_element_by_class_name('label-inline1').text
                            reference = reference.strip()
                            result['reference'] = reference
                        if len(row_list) > 6:
                            row_6 = row_list[6]
                            amount_text = row_6.find_element_by_class_name('label-inline1').text
                            amount_text = amount_text.strip()
                            amount_text = amount_text.replace('RM', '')
                            result['amount'] = amount_text
                    except Exception :
                        pass
                    self.sendStatus(self.order_no, result)
                    self.save_html("PubToPub支付成功页面源码")
            else:
                result = Status.v341
                result['actionMsg']= page_name.text;
        return result

    def  sendStatus(self,order_no,status):
        from utils.client import Client
        return Client.sendStatus(order_no,status,self.status_path)
    def is_session_timeout(self,auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception as e:
            # self.print_d(e)
            self.quit();
            return True;
        print(self.order_no+"--"+current_url)
        if (current_url.find("logout?sessionTimeout") > 0):
            if ( auto_quit ):
                self.quit();
            return True;
        else:
            return False;
    # 到账户的转账列表页
    def goto_account_transfer(self, accountNum):
        self.print_d("goto_account_transfer.")
        isFindAccount = False
        try:
            ACCOUNT = self.driver.find_element_by_partial_link_text('ACCOUNT')
        except NoSuchElementException:
            print('------ACCOUNT-----')
        else:
            # print(len(ACCOUNT))
            div = ACCOUNT.find_element_by_tag_name('div')
            div.click()
            #table-column-toggle1
            try:
                locator = (By.ID, 'table-column-toggle1')
                WebDriverWait(self.driver, 14, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                return isFindAccount
            table = self.driver.find_element_by_id('table-column-toggle1')

            tr_list = table.find_elements_by_tag_name('tr')
            for tr in tr_list:
                td_list = tr.find_elements_by_tag_name('td')
                if (len(td_list) > 0):
                    if(td_list[0].text.find(accountNum) > -1 ):
                        a = td_list[0].find_element_by_tag_name('a')
                        a.click()
                        isFindAccount = True
        return isFindAccount
    def get_transfer_list(self):
        transfer_list = [];
        try:
            locator = (By.PARTIAL_LINK_TEXT, 'History')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return transfer_list
        jsString = 'javascript:viewTrnxHist()'
        self.driver.execute_script(jsString);
        try:
            locator = (By.ID, 'table-column-toggle')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            return transfer_list
        self.tranfer_list_status = 3
        table = self.driver.find_element_by_id('table-column-toggle')
        tr_list = table.find_elements_by_tag_name('tr')
        for tr in tr_list:
            td_list = tr.find_elements_by_tag_name('td')
            if len(td_list) < 4 :
                continue
            transfer = {}
            date = td_list[0].text
            # 01-04-2020
            timeArray = time.strptime(date, "%d-%m-%Y")
            timeStamp = int(time.mktime(timeArray))
            transfer['time'] = timeStamp

            details = td_list[1].get_attribute('data-search')
            transfer['details'] = details.replace(" ", "")
            debit_mount = td_list[2].text
            credit_mount = td_list[3].text
            if len(debit_mount) > 1 :
                transfer['amount'] = debit_mount
            else:
                transfer['amount'] = credit_mount
            transfer_list.append(transfer)
        return transfer_list

    def get_tranfer_list_status(self):
        return self.tranfer_list_status;