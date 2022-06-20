import time
from datetime import datetime

from selenium.common.exceptions import WebDriverException
import logging

from dao.Status import Status


class Personification:

    def __init__(self,proxy_server=None):
        self.open_code = Status.o000['actionCode']
        self.order_no = None
        self.proxy_port = None
        self.proxy_ip = None
        self.proxy_index = None
        self.logger = logging
        self.is_quit = False
        self.delayCoefficient = 1
        self.config = None
        self.is_check = False
        self.is_open = False
        self.psw_input = None
        self.login_button = None
        self.tranfer_list_status = 0;  # 0-初始化 1-输入用户名 2-登录成功（在 account页面） 3-已选择账户（在转账列表页）
        self.is_goto_transfer = False;  # 是否成功到转账页
        pass
    def is_use_proxy(self):
        return False
    def get_order_no(self):
        return self.order_no
    def get_proxy_index(self):
        return self.proxy_index
    def open_and_init(self):
        pass
    def reopen(self):
        pass
    def to_bank(self, bank):
        return True
    def sleep (self,t):
        time.sleep(t* self.delayCoefficient);
        return
    def input_answer(self,answer):
        pass
    def exitFun (str):
        time.sleep(10);
        # exit(str);
        return
     ##可能加载慢
    def quit(self):
        try:
            self.driver.close()
            self.driver.quit()
        except Exception:
            pass
        self.is_quit = True
        # self.c_service.stop()
        if self.chrome_process and self.chrome_process.is_running():
            self.chrome_process.kill()
        if self.chrome_driver_process and self.chrome_driver_process.is_running():
            self.chrome_driver_process.kill()
        return
    def print_d(self,log):
        try:
            from config import Config
            if (Config.DEBUG_LOG):
                orderNo = 'init';
                if self.order_no and self.order_no is not None:
                    orderNo = self.order_no
                self.logger.warning(self.__class__.__name__+"|"+orderNo+"|"+str(log))
                print(self.__class__.__name__+'['+datetime.now().strftime('%H-%M-%S')+']' +str(log))
        except Exception:
            pass
        return
    def screen(self,name = None):
        if (None == name):
            if self.order_no is None:
                name = "init-" + datetime.now().strftime("%H-%M-%S")
            else:
                name = self.order_no+"-"+datetime.now().strftime("%H-%M-%S") #datetime.now().strftime("%H:%M:%S");
        try:
            from config import Config
            if ( Config.SCREEN is None ):
                return
            picture_url = self.driver.save_screenshot(Config.SCREEN+name+'.png')
            self.print_d("%s ：截图成功！！！" % picture_url)
        except BaseException as msg:
            self.print_d("%s ：截图失败！！！" % msg)
        return name
    def save_html(self,message=None):
        if(self.order_no and self.order_no is not None):
            name = self.order_no+"-"+datetime.now().strftime("%H-%M-%S")
        else:
            name = "init-" + datetime.now().strftime("%H-%M-%S")
        try:
            from config import Config
            if ( Config.HTML is None ):
                return
            path = Config.HTML+name+'.txt'
            # print(path)
            f = open(path, "a")
            msg = self.driver.page_source
            if( message is not None):
                f.write(message)
            f.write('\n\r')
            f.write('-------------\n\r')
            f.write(msg)
            f.close()
            self.print_d("%s ：保存源码！！！" % name)
        except BaseException as msg:
            self.print_d("%s ：保存源码失败！！！" % msg)
        return name

    def save_captcha(self, imageCode):
        if(self.order_no and self.order_no is not None):
            name = self.order_no+"-"+datetime.now().strftime("%H-%M-%S")
        else:
            name = "init-" + datetime.now().strftime("%H-%M-%S")
        try:
            from config import Config
            import requests, os
            from PIL import Image
            if ( Config.CAPTCHA is None ):
                return
            path = Config.CAPTCHA+name+'.png'

            left = imageCode.location['x']
            top = imageCode.location['y']
            right = imageCode.size['width'] + left
            down = imageCode.size['height'] + top

            screen_name = self.screen(None)
            screen_path = Config.SCREEN + screen_name + '.png'
            image = Image.open(screen_path)
            captcha_image = image.crop((left, top, right, down))
            captcha_image.save(path)

            # 删除截图
            if os.path.exists(path):
                os.remove(screen_path)

            self.print_d("%s ：保存验证码！！！" % name)
        except BaseException as msg:
            self.print_d("%s ：保存验证码失败！！！" % msg)
        return path

    def img_base64(self, img_path):
        image_base64 = None
        try:
            import base64, os
            with open(img_path, 'rb') as f:
                image = f.read()
                image_base64 = 'data:image/png;base64,'+str(base64.b64encode(image), encoding='utf-8')
            self.print_d("验证码转换base64成功！！！")

            # 删除验证码
            if os.path.exists(img_path):
                os.remove(img_path)
        except BaseException as msg:
            self.print_d("验证码转换base64失败！！！" % msg)
        return image_base64

    # 处理千分位金额
    def format_amount(self, amount):
        try:
            from re import sub
            return float(sub(r'[^\d.]', '', amount))
        except BaseException as msg:
            self.print_d("%s ：转换金额失败！！！" % msg)
        return ''

    def claim(self, lun, orderNo,logger=None):
        self.print_d("认领窗口")
        # self.loginPassword = lpsw;
        self.loginUserName = lun;
        self.order_no = orderNo;
        self.delayCoefficient = 1;
        self.session_time = time.time();
        if (logger is not None):
            print(logger)
            self.logger = logger
        # self.print_d("%d"%self.session_time)

    def get_session_time(self):
        if self.session_time :
            return time.time() - self.session_time
        else:
            return 0
    # 输入用户名
    def input_user_name(self,user_name = None):
        pass
    #返回用户名输入
    def back_input_name(self):
        pass
    # 异步操作-检查安全问题点击 yes 预先查找密码输入
    def check_and_find_psw(self):
        pass
    # 输入密码并提交
    def input_psw_and_submit(self, userName, psw):
        pass
    #登录
    def login(self):
        return ;

    def goto_transfer(self):
        return

    def account_list(self):
        return
    def goto_account(self, is_force):
        pass
    # 到账户的转账列表页
    def goto_account_transfer(self,accountNum):
        pass
    # 取转账列表
    def get_transfer_list(self):
        pass
    # 选择转账帐号
    def select_tranfer_info(self, account_number):
        pass
     # 输入转账方信息并到发送验证码
    def input_transfer_info(self, info):
        pass
    def  sendStatus(self,order_no,status):
        from utils.client import Client
        return Client.sendStatus(order_no,status,self.status_path)
    def is_session_timeout(self,auto_quit):
       pass
    def get_tranfer_list_status(self):
        return self.tranfer_list_status;
    def refresh(self):
        self.driver.refresh();