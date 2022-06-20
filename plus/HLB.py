import time
from datetime import datetime

import psutil
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, \
    WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config import Config
from dao.Status import Status
from model.BankType import BankType
from model.IPPool import IPPool
from plus.ChromeOptions import ChromeOptions
from plus.Personification import Personification


class HLB(Personification) :

    def __init__(self,proxy_index=None,order_no=None):
        Personification.__init__(self)
        if order_no is None:
            self.order_no = 'init'
        else:
            self.order_no = order_no
        self.config = Config.Hlb
        self.t_to_bank = None
        self.status_path = self.config.STATUS_PATH
        chrome_options = ChromeOptions.get_options()
        chrome_options.add_argument("--bank-name=" + BankType.Bank[1]['val'])
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
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })
        self.open_and_init()
    def is_use_proxy(self):
        return Config.CIMB.US_PROXY_SERVER
    def open_and_init(self):
        try:
            self.driver.get(self.config.OPEN_URL);
        except TimeoutException as te :
            print(te)
            self.quit();
        # self.sleep(5)
        self.print_d('新建窗口-打开页面-页面加载中')
        if self.order_no:
            self.sendStatus(self.order_no, Status.o000)
        driver_process = psutil.Process(self.driver.service.process.pid)
        if driver_process :
            self.chrome_driver_process = driver_process
        children_list = driver_process.children()
        if children_list:
            self.chrome_process = children_list[0]
        # TODO 检查页面是否正常加载
        try:
            locator = (By.ID, 'idLoginId')
            #用户名输入框
            WebDriverWait(self.driver, self.config.FIND_USER_NAME_TIME_OUT, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception :
            self.print_d('-----检查广告----')
            try:
                check_ad_timeout = self.config.OPEN_TIME_OUT-self.config.FIND_USER_NAME_TIME_OUT
                if check_ad_timeout < 1 :
                    check_ad_timeout = 1
                #检查广告关闭按钮
                WebDriverWait(self.driver, check_ad_timeout , 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                self.print_d('-----没有广告----')
            else:
                self.print_d('-----关闭广告----')
                modalCloseImg = self.driver.find_element_by_class_name("modalCloseImg");
                modalCloseImg.click()
        self.is_open = True
        self.print_d('新建窗口-页面加载完成')
        self.open_code = Status.o001['actionCode']
        if self.order_no:
            self.sendStatus(self.order_no, Status.o001)
    def to_bank(self, bank):
        to_bank = None
        try:
            to_bank = BankType.ToBank.HLBBank[bank]
        except Exception:
            return False
        if (to_bank is not None):
            self.t_to_bank = to_bank
            return True
    # 返回用户名输入
    def back_input_name(self,userName):
        try:
            back_btn = self.driver.find_element_by_id('j_idt125');
        except Exception as e: #WebDriverException: Message: chrome not reachable
            self.print_d(e.__context__)
            #如果有异常可能页面没加载好，休眠等待一下
            time.sleep(1)
            return False
        back_btn.click()
        self.loginUserName = userName;
        return True
    # 输入密码并提交
    def input_psw_and_submit(self, userName, psw):
        self.loginPassword = psw;
        result = Status.l120
        if (userName != self.loginUserName):
            # 重新输入用户名登录
            self.back_input_name(userName);
            time.sleep(0.5)
            result = self.input_user_name();
            if (result['actionCode'] != Status.l110['actionCode']):
                return result
            result = self.check_and_find_psw()
            if (result['actionCode'] != Status.l113['actionCode']):
                return result
        else:
            pass

        if (self.is_check == False ):
            try:
                locator = (By.ID, 'idSBCBConfirmPic')
                WebDriverWait(self.driver, 3, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception:
                result = self.sendStatus(self.order_no,Status.l112)
                return result
            else:
                idSBCBConfirmPic = self.driver.find_element_by_id("idSBCBConfirmPic")
                idSBCBConfirmPic.click();
        try:
            locator = (By.ID, 'idPswd')
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception as e:
            print('-----idPswd-----')
            print(e)
            return self.sendStatus(self.order_no, Status.l112);
        self.psw_input = self.driver.find_element_by_id("idPswd")
        if (self.psw_input is None):
            self.action_code = Status.l121['actionCode'];
            return self.sendStatus(self.order_no, Status.l121);
        # self.psw_input.send_keys(self.loginPassword);
        jsString = '$("#idPswd").val("'+self.loginPassword+'")';
        self.driver.execute_script(jsString);
        time.sleep(0.2)
        idBtnSubmit2 = self.driver.find_element_by_id("idBtnSubmit2")
        idBtnSubmit2.click();
        # 判断有没有出错
        locator0 = (By.CLASS_NAME, 'ui-messages-error-summary')
        try:
            WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception:
            print('-----ui-messages-error-summary-----')
        else:
            print('登录异常')
            result = Status.l131;
            try:
                messages_error = self.driver.find_element_by_class_name("ui-messages-error-summary")
            except NoSuchElementException:
                pass
            else:
                result['actionMsg'] = messages_error.text;
            return result;

        is_login = False;
        for index in range(1, 40):
            current_url = self.driver.current_url
            # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
            print(current_url)
            if (current_url.find("/fo/main") > 0):
                is_login = True;
                break;
            else:
                time.sleep(0.5)
        if (is_login):
            self.action_code = Status.l130['actionCode'];
            result = Status.l130;
        else:
            print('帐号或密码不正确');
            self.action_code = Status.l131['actionCode'];
            result = Status.l131;
        return result
            # 输入用户名
    def input_user_name(self,user_name = None):
        self.print_d('开始输入用户名')
        result = self.sendStatus(self.order_no, Status.o000);
        try:
            modalCloseImg = self.driver.find_element_by_class_name("modalCloseImg");
        except NoSuchElementException as ne:
            pass
        else:
            modalCloseImg.click();
        start_time = datetime.now();
        idLoginId = (By.ID, 'idLoginId')
        try:
            WebDriverWait(self.driver, 20, 0.5).until(EC.visibility_of_element_located(idLoginId))
        except Exception as e:
            print('-----idLoginId-----')
            print(e)
            return self.sendStatus(self.order_no, Status.l109);
        self.print_d('找到输入')
        if user_name is not None :
            self.loginUserName = user_name
            time.sleep(0.2)
        idLoginId = self.driver.find_element_by_id("idLoginId")
        time.sleep(0.2)
        idLoginId.send_keys(self.loginUserName)
        self.print_d('完成输入')
        time.sleep(0.2);
        idBtnSubmit1 = self.driver.find_element_by_id("idBtnSubmit1")
        idBtnSubmit1.click();
        try:
            locator1 = (By.CLASS_NAME, 'ui-message-error-detail')
            WebDriverWait(self.driver, 2, 0.5).until(EC.visibility_of_element_located(locator1))
        except Exception:
            self.print_d('用户名输入没错')
            result = self.sendStatus(self.order_no, Status.l110)
            if self.config.RETURN_SAFETY_PIC :
                # 读取 预留图片
                try:
                    locator = (By.ID, 'j_idt66')
                    WebDriverWait(self.driver, self.config.AFTER_INPUT_NAME_TIME_OUT, 0.5).until(EC.visibility_of_element_located(locator))
                except Exception:
                    print('-----picture-----')
                else:
                    img = self.driver.find_element_by_id('j_idt66')
                    result.update({'picture': img.get_attribute('src')})
        else:
            result = self.sendStatus(self.order_no,Status.l109)
            error = self.driver.find_element_by_class_name('ui-message-error-detail')
            result['actionMsg'] = error.text
        return result
    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        result = Status.l110;
        locator = (By.ID, 'idSBCBConfirmPic')
        try:
            WebDriverWait(self.driver, self.config.AFTER_INPUT_NAME_TIME_OUT, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            print('-----idSBCBConfirmPic-----')
            try:
                idBtnSubmit1 = self.driver.find_element_by_id("idBtnSubmit1")
            except NoSuchElementException:
                return self.sendStatus(self.order_no, Status.l109);
            else:
                idBtnSubmit1.click();
                self.print_d('点击 NEXT')
                time.sleep(0.6)
        try:
            idSBCBConfirmPic = self.driver.find_element_by_id("idSBCBConfirmPic")
        except NoSuchElementException:
            return self.sendStatus(self.order_no, Status.l109);
        self.driver.execute_script("arguments[0].click();", idSBCBConfirmPic)
        # idSBCBConfirmPic.click();
        result = Status.l113;
        time.sleep(0.2)
        self.is_check = True
        return result
    def login(self) :
            result = self.sendStatus(self.order_no,Status.o000);
            try:
                modalCloseImg = self.driver.find_element_by_class_name("modalCloseImg");
            except NoSuchElementException as ne:
                pass
            else:
                modalCloseImg.click();

            start_time = datetime.now();
            idLoginId = (By.ID, 'idLoginId')
            try:
                WebDriverWait(self.driver, 60, 0.5).until(EC.visibility_of_element_located(idLoginId))
            except Exception as e:
                print('-----idLoginId-----')
                print(e)
                return self.sendStatus(self.order_no, Status.l109);

            idLoginId = self.driver.find_element_by_id("idLoginId")
            idLoginId.send_keys(self.loginUserName);
            time.sleep(0.5);
            # <input id="idLoginId" name="idLoginId" type="text" autocomplete="off" maxlength="16" class="ui-inputfield ui-inputtext ui-widget ui-state-default ui-corner-all large" role="textbox" aria-disabled="false" aria-readonly="false" aria-multiline="false">
            #
            # sendkey('userName');
            idBtnSubmit1 = self.driver.find_element_by_id("idBtnSubmit1")
            idBtnSubmit1.click();
            # <button id="idBtnSubmit1" name="idBtnSubmit1" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only submitbtn" onclick="if(!checkLoginId()){return false;};clearTooltip();PrimeFaces.ab({source:'idBtnSubmit1',update:'login_panel_id',onsuccess:function(data,status,xhr){try{startSessionTimer();}catch(e){};;},oncomplete:function(xhr,status,args){top.scroll(0,0);}});return false;" style="background: #84c34f; width: 100%; color: #fff; border: 0px; font-weight:bold;" type="submit" role="button" aria-disabled="false"><span class="ui-button-text ui-c">Next</span></button>
            #
            # click();
            locator = (By.ID, 'idSBCBConfirmPic')
            try:
                WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator))
            except Exception as e:
                print('-----idSBCBConfirmPic-----')
                print(e)
                return self.sendStatus(self.order_no, Status.l109);
            idSBCBConfirmPic = self.driver.find_element_by_id("idSBCBConfirmPic")
            idSBCBConfirmPic.click();

            # <div class="txt_center" style="display: inline-block; margin-left: 15px; margin-bottom: 10px;">
            #   <input id="idSBCBConfirmPic" type="checkbox" name="idSBCBConfirmPic" onchange="javascript:checkConfirmPic(this.checked);" style="margin-top: 3px; vertical-align: middle;">
            #       <span onclick="javascript:checkConfirmPicText();">
            #       <span class="txt_bold"><font style="vertical-align: inherit;">
            # <font style="vertical-align: inherit;">是的，这是我的安全图片</font>
            # </font>
            # </span></span>
            # </div>
            #
            # click();

            time.sleep(0.4)
            idPswd = self.driver.find_element_by_id("idPswd")
            idPswd.send_keys(self.loginPassword);
            time.sleep(0.4)
            # <input id="idPswd" name="idPswd" type="text" class="ui-inputfield ui-password ui-widget ui-state-default ui-corner-all large ui-watermark" style="margin: 10px 0 0 0;" autocomplete="off" maxlength="8" role="textbox" aria-disabled="false" aria-multiline="false">
            #
            #
            # sendKey('psw')

            idBtnSubmit2 = self.driver.find_element_by_id("idBtnSubmit2")
            idBtnSubmit2.click();
            # <button id="idBtnSubmit2" name="idBtnSubmit2" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only submitbtn" onclick="login('LTH990908');return false;;" style="background: #84c34f; width: 100%; color: #fff; border: 0px; font-weight:bold;" type="button" role="button" aria-disabled="true"><span class="ui-button-text ui-c"><font style="vertical-align: inherit;"><font style="vertical-align: inherit;">登录</font></font></span></button>
            #
            # click();

            # 判断有没有出错
            locator0 = (By.CLASS_NAME, 'ui-messages-error-summary')
            try:
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator0))
            except Exception as e:
                print('-----ui-messages-error-summary-----')
            else:
                print('登录异常')
                result = Status.l131
                try:
                    messages_error = self.driver.find_element_by_class_name("ui-messages-error-summary")
                except NoSuchElementException:
                    pass
                else:
                    result['actionMsg'] = messages_error.text;
                return result;

            is_login = False;
            for index in range(1, 40):
                current_url = self.driver.current_url
                # https://www.maybank2u.com.my/home/m2u/common/dashboard/casa
                print(current_url)
                if (current_url.find("/fo/main") > 0):
                    is_login = True;
                    break;
                else:
                    time.sleep(0.5)
            if( is_login ):
                self.action_code = Status.l130['actionCode'];
                result = Status.l130;
            else:
                print('帐号或密码不正确');
                self.action_code = Status.l131['actionCode'];
                result = Status.l131;
            print((datetime.now() - start_time).seconds);
            return result

            #https://s.hongleongconnect.my/rib/app/fo/main?refererExecution=e2s1&locale=en
    # 到账户的转账列表页
    def goto_account_transfer(self, accountNum):
        self.print_d("goto_account_transfer。")
        isFindAccount = False
        locator0 = (By.ID, 'idMainFrame')
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception as e:
            self.print_d('-----没取到idMainFrame-----')
        # idMainFrame
        self.driver.switch_to.frame("idMainFrame");
        try:
            idDTCasa_data = self.driver.find_element_by_id('idDTCasa_data')
        except Exception as e:
            self.print_d("-----idDTCasa_data------")
            self.print_d(e)
            return isFindAccount
        tr_list = idDTCasa_data.find_elements_by_tag_name("tr");
        if (len(tr_list) == 0):
            self.print_d("活期帐号列表空")
            self.screen(None)
            return isFindAccount;
        self.print_d("活期帐号列表长度=%d" % len(tr_list))
        for tr in tr_list:
            account = {}
            accname = tr.find_element_by_class_name('accname');
            accnum = tr.find_element_by_tag_name('a');
            self.print_d(accname.text);
            self.print_d(accnum.text);
            if (accnum.text.find(accountNum) > -1 ):
                accnum.click()
                isFindAccount = True
        return isFindAccount
    def goto_transfer(self):
        locator0 = (By.PARTIAL_LINK_TEXT, 'TRANSACT')
        try:
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception as e:
            print('-----TRANSACT-----')
            print(e)
        try:
            TRANSACT = self.driver.find_element_by_partial_link_text("TRANSACT");
        except Exception as ee:
            print(ee)
        else:
            TRANSACT.click();
            time.sleep(0.6);
            # 直接手机转账
            HLB = self.driver.find_element_by_partial_link_text("DuitNow to Mobile");
            HLB.click()

            # if ( self.t_to_bank == BankType.ToBank.HLBBank['HLBBank']):
            #     HLB = self.driver.find_element_by_partial_link_text("HLB");
            #     HLB.click()
            # else:
            #     # 其他银行
            #     IBG = self.driver.find_element_by_partial_link_text("IBG");
            #     IBG.click();
        return
    def account_list(self):
        accountList = [];
        self.print_d("取帐号列表。")
        self.print_d(self.driver.current_url)
        locator0 = (By.ID, 'idMainFrame')
        try:
            WebDriverWait(self.driver, 5, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception as e:
            self.print_d('-----没取到idMainFrame-----')
        # idMainFrame
        self.driver.switch_to.frame("idMainFrame");
        try:
            idDTCasa_data = self.driver.find_element_by_id('idDTCasa_data')
        except Exception as e :
            self.print_d("-----idDTCasa_data------")
            self.print_d(e)
            return accountList
        tr_list = idDTCasa_data.find_elements_by_tag_name("tr");
        if ( len(tr_list) == 0):
            self.print_d("活期帐号列表空")
            self.screen(None)
            return accountList;
        self.print_d("活期帐号列表长度=%d"%len(tr_list))
        for tr in tr_list:
            account = {}
            accname = tr.find_element_by_class_name('accname');
            accnum = tr.find_element_by_tag_name('a');
            self.print_d(accname.text);
            self.print_d(accnum.text);
            account.update({"accountName": accname.text, "accountNumber": accnum.text})
            accountList.append(account);
            tds = tr.find_elements_by_tag_name('td');
            self.print_d("tds长度=%d" % len(tds))
            if( len(tds) > 1):
                yuer_td = tds[1];
                balances = yuer_td.text
                currency = balances.splitlines()[0]
                bal = balances.splitlines()[1]
                self.print_d(currency)
                self.print_d(bal)
                account.update({"currency": currency, "balances": bal});
                # font_list = yuer_td.find_elements_by_xpath("./font/font")
                # for font in font_list:
                #     print(font.text);
                    # "currency": currency, "balances": bal
        return accountList
    # 选择转账信息
    def select_tranfer_info(self, info):
        self.print_d('选择转账帐号%s'%info);
        account_number = info['accountNumber']
        result = Status.t210;
        try:
            locator = (By.ID, "idSOMTransferFrom_label")
            WebDriverWait(self.driver, 8, 0.5).until(EC.visibility_of_element_located(locator))
        except Exception:
            self.print_d('可能没在转账页')
            return result
        try:
            idSOMTransferFrom_label = self.driver.find_element_by_id('idSOMTransferFrom_label')
            if (idSOMTransferFrom_label.text.find(account_number) > -1):
                result = Status.t230;
                return result
            idSOMTransferFrom_label.click();
            time.sleep(0.3)
            idSOMTransferFrom_panel = self.driver.find_element_by_id('idSOMTransferFrom_panel')
            li_list = idSOMTransferFrom_panel.find_elements_by_tag_name('li')
            for li in li_list:
                print(li.text)
                if (li.text.find(account_number) > -1):
                    li.click()
                    result = Status.t230;
                    result['actionMsg'] = '选择帐号成功';
        except Exception as e:
            result = Status.t212;
            print(e)
        return result
        # 选择转账帐号

    # 手机号码快捷转账
    def transfer_mobile(self, info):

        transferAccount = info['toAccountNumber']
        transferAmount = info['amount']
        transferReference = info['reference']
        transferRecipientName = info['recipientName']

        self.sendStatus(self.order_no, Status.t220);
        self.print_d('开始进行手机快捷转账')

        # 选择使用手机转账方式
        try:
            field_label_transfer_to = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idProxyType_label")))
        except Exception:
            self.print_d('没有找到转账方式下拉框')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择快捷方式方式按钮，显示出快捷方式选项
        field_label_transfer_to.click()
        self.print_d('点击转账方式下拉框，显示出转账方式选项')

        # 判断选择框是否正常弹出
        try:
            field_div_transfer_to_list = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idProxyType_panel")))
        except Exception:
            self.print_d('没有找到转账方式选项列表')
            return self.sendStatus(self.order_no, Status.t221);

        # 选择使用 Mobile Number
        try:
            field_li_transfer_to_mobile = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='idProxyType_panel']//li[contains(text(), 'Mobile Number')]")))
        except Exception:
            self.print_d('没有找到收款方手机快捷方式选项')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择选择使用MobileNumber
        field_li_transfer_to_mobile.click()
        self.print_d('点击选择选择使用Mobile Number')

        # 手机号码输入框
        try:
            field_input_mobile_number = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idProxyId")))
        except Exception:
            self.print_d('没有找到收款方手机号码输入框')
            return self.sendStatus(self.order_no, Status.t243);

        # 输入手机号码，前面+6
        field_input_mobile_number.clear()
        field_input_mobile_number.send_keys('+6'+transferAccount);
        self.print_d("输入收款方手机号码成功");
        self.sendStatus(self.order_no, Status.t240);

        # 输入完手机号码后，触发一下丢失焦点，否则选择类型时第一次click无效
        self.driver.execute_script("arguments[0].blur();", field_input_mobile_number)
        time.sleep(1)

        # 选择使用手机转账类型
        # try:
        #     field_label_transfer_method = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idRR")))
        # except Exception:
        #     self.print_d('没有找到转账类型下拉框')
        #     return self.sendStatus(self.order_no, Status.t221);

        # # 点击选择快捷方式类型按钮，显示出快捷类型选项
        # field_label_transfer_method.click()
        # self.print_d('点击转账类型下拉框，显示出转账类型选项')

        # # 判断选择框是否正常弹出
        # try:
        #     field_div_transfer_method_list = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idRR_panel")))
        # except Exception:
        #     self.print_d('没有找到转账类型选项列表')
        #     return self.sendStatus(self.order_no, Status.t221);

        # # 选择使用 Savings
        # try:
        #     field_li_transfer_method_saving = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='idRR_panel']//li[contains(text(), 'Savings')]")))
        # except Exception:
        #     self.print_d('没有找到Saving类型选项')
        #     return self.sendStatus(self.order_no, Status.t221);

        # # 点击选择选择使用Saving
        # field_li_transfer_method_saving.click()
        # self.print_d('点击选择选择使用Saving')
        
        # time.sleep(1)

        # # 转账备注输入框
        # try:
        #     field_input_note = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idOthInfo")))
        # except Exception:
        #     self.print_d('没有找到转账备注输入框')
        #     return self.sendStatus(self.order_no, Status.t243);

        # # 输入转账备注
        # field_input_note.clear()
        # field_input_note.send_keys(transferReference);
        # self.print_d("输入转账备注成功");
        # self.sendStatus(self.order_no, Status.t242);

        # 收款金额输入框
        try:
            field_input_amount = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "idAmt")))
        except Exception:
            self.print_d('没有找到收款金额输入框')
            return self.sendStatus(self.order_no, Status.t243);

        # 输入收款金额
        field_input_amount.clear()
        field_input_amount.send_keys(transferAmount);
        self.print_d("输入收款金额成功");
        self.sendStatus(self.order_no, Status.t241);

        # 勾选协议
        try:
            field_div_accept = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "j_idt657")))
        except Exception:
            self.print_d('没有找到协议勾选框')
            return self.sendStatus(self.order_no, Status.t221);

        # 点击选择快捷方式方式按钮，显示出快捷方式选项
        field_div_accept.click()
        self.print_d('点击勾选协议')

        # 下一步按钮
        try:
            field_btn_next = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.ID, "idBtnSubmit")))
        except Exception:
            self.print_d('没有找到转账信息下一步按钮')
            return self.sendStatus(self.order_no, Status.t243);

        # 点击进行下一步，到下一步页面
        field_btn_next.click();
        self.print_d("提交转账信息，到下一步页面");
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

        # 捕获失败原因
        try:
            field_span_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//span[@class='ui-messages-error-summary']")))
        except Exception:
            self.print_d('未检测到错误信息');
            # return self.sendStatus(self.order_no, Status.t261);
        else:
            message = field_span_error.get_attribute("innerHTML");
            res = self.sendStatus(self.order_no,Status.t261);
            res['actionMsg'] = message;

            self.print_d('转账失败-%s' % message);
            return self.sendStatus(self.order_no, res);



        print(result)

        # 获取OTP编号
        # try:
        #     field_span_otp_refno = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "lblRefNo")))
        # except Exception:
        #     self.print_d("未发现OTP标识");
        #     field_span_otp_refno = None

        # if (field_span_otp_refno is None):
        #     # 捕获失败原因
        #     try:
        #         field_div_error = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.ID, "td_errorMessageContainer_errormessage")))
        #     except Exception:
        #         self.print_d('转账失败，未捕获到错误原因');
        #         return self.sendStatus(self.order_no, Status.t261);

        #     message = field_div_error.find_element_by_tag_name("div").get_attribute("innerHTML");
        #     message = message.replace('&gt;', '>')

        #     res = self.sendStatus(self.order_no,Status.t261);
        #     res['actionMsg'] = message;

        #     self.print_d('转账失败-%s' % message);
        #     result = self.sendStatus(self.order_no, res);
        # else:
        #     otp_refno = field_span_otp_refno.get_attribute('innerHTML');

        #     self.print_d("加载OTP页面成功，自动触发发送OTP，OTP标识-%s" % otp_refno);
        #     result = self.sendStatus(self.order_no, Status.v320);
        #     result.update({'refno':otp_refno});

        # return result;


            # self.print_d('input_transfer_info.')
            # result = Status.t210;
            # transferAccount = info['toAccountNumber']
            # transferAmount = info['amount']
            # transferReference = info['reference']
            # # transferBank = info['toBank']
            # # toAccountType = info['toAccountType']
            # toAccountType = 'Current/Savings'
            # transferBank = self.t_to_bank
            # #选择银行
            # self.print_d('选择银行')
            # try:
            #     idBnk = self.driver.find_element_by_id("idBnk")
            # except NoSuchElementException:
            #     jsString = '$("#idChatContainer").remove();';
            #     self.driver.execute_script(jsString);
            #     self.print_d('不用选择银行')
            # else:
            #     self.print_d('开始选择银行')
            #     idBnk.click();
            #     time.sleep(0.2)
            #     #
            #     jsString = '$("#idBnk_panel>div").attr("style","");$("#idChatContainer").remove();';
            #     self.driver.execute_script(jsString);
            #     idBnk_panel = self.driver.find_element_by_id("idBnk_panel")
            #     li_list = idBnk_panel.find_elements_by_tag_name("li")
            #     for li in li_list:
            #         # self.print_d(li.text)
            #         if (li.text.find(transferBank) > -1 ):
            #             li.click();
            #             break
            #     jsString = 'window.scrollBy(0, -100)';
            #     self.driver.execute_script(jsString);
            #     try:
            #         #等待操作完成的反馈
            #         locator3 = (By.ID, "idSOMTrsfMode_label")
            #         WebDriverWait(self.driver, 3, 0.3).until(EC.visibility_of_element_located(locator3))
            #     except Exception as e:
            #         print('---idSOMTrsfMode_label---')
            #         print(e)
            #         return Status.t243;
            # #账户类型
            # self.print_d('账户类型')
            # idAcctTyp = self.driver.find_element_by_id("idAcctTyp")
            # idAcctTyp.click();
            # # self.driver.execute_script("arguments[0].click();", idAcctTyp)
            # time.sleep(0.3)
            # idAcctTyp_panel = self.driver.find_element_by_id("idAcctTyp_panel")
            # li_list = idAcctTyp_panel.find_elements_by_tag_name('li')
            # if self.config.ACCOUNT_TYPE > -1:
            #     at = ['Savings', 'Credit', 'Loan', 'Financing']
            #     toAccountType = at[self.config.ACCOUNT_TYPE]
            # for li in li_list:
            #     if (li.text.find(toAccountType) > -1):
            #         li.click();
            #         break
            # for i in range(1,10):
            #     idRR_label = self.driver.find_element_by_id('idRR_label')
            #     try:
            #         if ( idRR_label and idRR_label.text.find('Fund') > -1):
            #             break;
            #     except Exception:
            #         pass
            #     time.sleep(0.5);
            # # idAcctNo = self.driver.find_element_by_id("idAcctNo")
            # # idAcctNo.send_keys(transferAccount)
            # # time.sleep(1) #帐号字符稍微长一点，需要时间输入
            # #转出帐号
            # self.print_d('转出帐号')
            # jsString = '$("#idAcctNo").val("'+transferAccount+'")';
            # self.driver.execute_script(jsString);
            # time.sleep(0.3)
            # #金额
            # self.print_d('金额')
            # idAmt = self.driver.find_element_by_id("idAmt")
            # idAmt.clear()
            # idAmt.send_keys(transferAmount)
            # time.sleep(0.2)
            # # jsString = 'window.scrollBy(0, 100)';
            # # self.driver.execute_script(jsString);
            # try:
            #     locator3 = (By.ID, "idRR")
            #     WebDriverWait(self.driver, 3, 0.3).until(EC.visibility_of_element_located(locator3))
            # except Exception as e:
            #     print('---idRR---')
            #     print(e)
            #     return Status.t243;
            # # 选择 Bill payment
            # self.print_d('选择 Bill payment')
            # idRR = self.driver.find_element_by_id("idRR")
            # try:
            #     idRR.click();
            # except ElementClickInterceptedException:
            #     self.driver.execute_script("arguments[0].click();", idRR)
            # time.sleep(0.3)
            # idRR_panel = self.driver.find_element_by_id("idRR_panel")
            # li_list = idRR_panel.find_elements_by_tag_name('li')
            # for li in li_list:
            #     if (li.text.find('Bill') > -1):
            #         li.click();
            #         time.sleep(1.5)
            #         break
            # #备注
            # self.print_d('备注')
            # idOthInfo = self.driver.find_element_by_id("idOthInfo")
            # idOthInfo.clear()
            # idOthInfo.send_keys(transferReference)
            # time.sleep(0.3)
            # # 同意
            # try:
            #     self.print_d('同意')
            #     chkbox_box = self.driver.find_element_by_id("idSBCTnc")
            # except NoSuchElementException:
            #     pass
            # else:
            #     chkbox_box.click();
            #     time.sleep(0.3)
            # self.print_d('提交')
            # # idBtnSubmit next
            # idBtnSubmit = self.driver.find_element_by_id("idBtnSubmit")
            # idBtnSubmit.click();
            # time.sleep(1)
            # #有时点击一次无效
            # try:
            #     idBtnSubmit_2 = self.driver.find_element_by_id("idBtnSubmit")
            # except NoSuchElementException:
            #     pass
            # else:
            #     try:
            #         if(idBtnSubmit_2.is_displayed()):
            #             idBtnSubmit_2.click();
            #     except Exception as e:
            #         print(e)

            # #cx_chat_error_desc

            # # 判断有没有出错
            # try:
            #     locator0 = (By.CLASS_NAME, 'ui-messages-error-summary')
            #     WebDriverWait(self.driver, 2, 0.5).until(EC.visibility_of_element_located(locator0))
            # except Exception as e:
            #     print('-----ui-messages-error-summary-----')
            #     result = Status.t244;
            #     try:
            #         error_detail = self.driver.find_element_by_class_name('ui-message-error-detail')
            #     except NoSuchElementException:
            #         pass
            #     else:
            #         self.print_d('转账提交异常-0')
            #         result = Status.t261;
            #         try:
            #             messages_error = self.driver.find_element_by_class_name("ui-messages-error-summary")
            #         except NoSuchElementException:
            #             pass
            #         else:
            #             result['actionMsg'] = messages_error.text;
            #         self.screen(None)
            #         return result;
            #     # 判断有没有成功
            #     try:
            #         locator0 = (By.ID, 'idFormCfmAckDtl:idTACAdd')
            #         WebDriverWait(self.driver, 7, 0.5).until(EC.visibility_of_element_located(locator0))
            #     except Exception:
            #         result = Status.t244
            #     else:
            #         result = Status.t260
            #         #已自动发眼验证码
            #         result = Status.v320
            # else:
            #     self.print_d('转账提交异常-1')
            #     result = Status.t261
            #     try:
            #         messages_error = self.driver.find_element_by_class_name("ui-messages-error-summary")
            #     except NoSuchElementException:
            #         pass
            #     else:
            #         result['actionMsg'] = messages_error.text;
            #     self.screen(None)
            #     return result;
            # return result;
    # 重发验证码
    def resend_code (self,code):
        # 重发验证码 超过一点时间才能重发
        result = Status.v315
        # idFormCfmAckDtl:idBtnResend
        try:
            locator0 = (By.ID, 'idFormCfmAckDtl:idBtnResend')
            WebDriverWait(self.driver, 10, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception as e:
            return result

        try:
            idBtnResend = self.driver.find_element_by_id("idFormCfmAckDtl:idBtnResend");
        except NoSuchElementException as ne:
            print(ne)
            return result
        else:
            try:
                idBtnResend.click();
                result = Status.v320
            except Exception:
                result = Status.v319
    #输入验证码
    def input_sms_code (self,code):
        result = self.sendStatus(self.order_no,Status.v321)
        try:
            locator0 = (By.ID, 'idFormCfmAckDtl:idTACAdd')
            WebDriverWait(self.driver, 2, 0.5).until(EC.visibility_of_element_located(locator0))
        except Exception :
            return result
        idTACAdd = self.driver.find_element_by_id("idFormCfmAckDtl:idTACAdd");
        idTACAdd.send_keys(code)
        result = Status.v330
        time.sleep(0.5)
        #idFormCfmAckDtl:idBtnConfirmTrsf
        try:
            submit_btn = self.driver.find_element_by_id("idFormCfmAckDtl:idBtnConfirmTrsf");
        except NoSuchElementException:
            return Status.v331
        else:
            submit_btn.click()
            result = Status.v332
        #判断结果
        #txt_green txt_bold
        try:
            locator1 = (By.CLASS_NAME, 'txt_green')
            WebDriverWait(self.driver, 6, 0.5).until(EC.visibility_of_element_located(locator1))
        except Exception:
            self.print_d('--没找到Successful--')
            #如果没有找到成功提示就判断一下错误#ui-messages-error-summary
            try:
                locator0 = (By.CLASS_NAME, 'ui-messages-error-summary')
                WebDriverWait(self.driver, 4, 0.5).until(EC.visibility_of_element_located(locator0))
            except Exception:
                #重新找一下 successful
                self.print_d('重新找一下 successful')
                try:
                    reference = self.driver.find_element_by_class_name('txt_green')
                    reference_text = reference.text
                    if reference_text.find('Successful') > 0:
                        result = Status.v340
                        orderNo = self.order_no
                        result['orderMsg'] = 'Successful'
                        result['reference'] = orderNo
                        table_section = self.driver.find_element_by_class_name('table-section-dark')
                        tr_li = table_section.find_elements_by_tag_name('tr')
                        if len(tr_li) > 1:
                            td_li = tr_li[1].find_elements_by_tag_name('td')
                            if len(td_li) > 1:
                                amount_text = td_li[1].text
                                amount_text.strip()
                                result['amount'] = amount_text
                    self.sendStatus(self.order_no, result)
                except Exception:
                    self.print_d('--第二次没找到Successful--')
                    result = self.sendStatus(self.order_no, Status.v339)
            else:
                result = self.sendStatus(self.order_no,Status.v341)
                error_summary = self.driver.find_element_by_class_name('ui-messages-error-summary')
                result['actionMsg']= error_summary.text;
        else:
            self.print_d('--转账Successful--')
            result = Status.v340
            orderNo = self.order_no
            try:
                reference = self.driver.find_element_by_class_name('txt_green')
                reference_text = reference.text
                if reference_text.find('Successful') > -1:
                    result['orderMsg'] = 'Successful'
                    result['reference'] = orderNo
                    table_section = self.driver.find_element_by_class_name('table-section-dark')
                    tr_li = table_section.find_elements_by_tag_name('tr')
                    if len(tr_li) > 1:
                        td_li = tr_li[1].find_elements_by_tag_name('td')
                        if len(td_li) > 1:
                            amount_text = td_li[1].text
                            amount_text = amount_text.strip()
                            result['amount'] = amount_text
                self.sendStatus(self.order_no, result)
            except Exception:
                 self.print_d('-解析转账内容异常-')
        return result
    def is_session_timeout(self,auto_quit):
        try:
            current_url = self.driver.current_url
        except Exception as we:
            # self.print_d(we)
            self.quit();
            return True;
        print(self.order_no+"--"+current_url)
        if (current_url.find("logout?sessionTimeout") > 0):
            if ( auto_quit ):
                self.quit();
            return True;
        else:
            return False;
    def get_tranfer_list_status(self):
        return self.tranfer_list_status;