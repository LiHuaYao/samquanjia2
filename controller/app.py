import logging
import os
import sys
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
import pymysql
sys.path.append('./')

from controller.m2u.m2uController import m2uModule, all_web_drivers
from controller.mer.merchantController import merchantModule
from controller.other.indexController import indexModule
from config import Config
from flask_apscheduler import APScheduler

from model.IPPool import IPPool
from model.Order import db
from plus.CheckTest import CheckTest
from progress import kill
import time

app = Flask("web_service");
# 将蓝图注册到app
app.register_blueprint( indexModule, url_prefix='/')
app.register_blueprint( m2uModule, url_prefix='/m2u')
app.register_blueprint( merchantModule, url_prefix='/mer')

app.config.from_object(Config)
db.init_app(app)
def check_proxy_server():
    proxy_server_len = len(IPPool.ip_list)
    if proxy_server_len > 0 :
        for index in range(0,proxy_server_len):
            checkThread = Thread(target=open_and_check, args=[index])
            checkThread.start();
#检查代理端口是否可以打开银行页面，并去掉不可用的代理端口
def open_and_check(proxy_index):
    bank = CheckTest(proxy_index)
    if (bank is not None and bank.is_open == False):
        IPPool.move_proxy(proxy_index)
def update_proxy_server_list():
    # 获取代理端口
    IPPool.get_proxies()
    proxy_server_len = len(IPPool.ip_list)
    # logging.warning('代理列表：%d' %proxy_server_len)
    # logging.warning(IPPool.ip_list)
    if proxy_server_len == 0 :
        #代理服务为空处理
        print('代理列表为空')
        logging.warning('代理列表为空，需要通知运营')
def session_check():
    print('session_check')
    SESSION_VALID_TIME = Config.SESSION_VALID_TIME
    if (len(all_web_drivers) == 0):
        return
    for order_no in list(all_web_drivers.keys()):
        try:
            driver = all_web_drivers[order_no]
        except Exception:
            pass
        else:
            if ( SESSION_VALID_TIME > 0 and driver is not None ):
                # 会话时间超时
                if  (driver.get_session_time() > SESSION_VALID_TIME ):
                    logging.warning('SESSION_VALID_TIME')
                    driver.quit()
                # 银行页面超时
                if driver.is_session_timeout(True):
                    logging.warning('session_timeout')
                    driver.quit()
                if driver.is_quit == True:
                    del all_web_drivers[order_no]
def clear_timeout_drivers():
    print("clear_timeout_drivers..");
    for order_no in list(all_web_drivers.keys()):
        driver = all_web_drivers[order_no];
        driver.is_session_timeout(True)

@app.route('/app')
def run_app():
    return "app"
if __name__ == '__main__':
    scheduler = APScheduler(BackgroundScheduler(timezone=Config.SCHEDULER_TIMEZONE))
    scheduler.init_app(app)  # 把任务列表放进flask
    scheduler.start()  # 启动任务列表
    log_path = Config.LOG_PATH
    log_name = "robot.log"
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    if not os.path.exists(log_path+log_name):
        f = open(log_path+log_name, 'w')
        f.close()
    logging.basicConfig(level=logging.WARNING,  # 控制台打印的日志级别
                    filename=log_path+log_name,
                    filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    # a是追加模式，默认如果不写的话，就是追加模式
                    format=
                    '%(asctime)s - [line:%(lineno)d] - %(message)s'
                    # 日志格式
                    )
    logging.warning('日志级别为WARNING。')
    app.run(host='0.0.0.0',port=Config.WEB_PORT,debug=Config.DEBUG);