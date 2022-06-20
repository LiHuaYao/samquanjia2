import json
import os
import random
import time
import logging
from flask import request,Blueprint
import pymysql
from threading import Thread
from config import Config
from dao.Status import Status
from model.IPPool import IPPool
from model.Result import Reqult
from model.Order import Order
from model.BankType import BankType
from plus.Personification import Personification
from plus.Maybank import Maybank
from plus.HLB import HLB
from plus.PBe import PBe
from plus.CIMB import CIMB
from plus.Krungsri import Krungsri
from plus.Kasikorn import Kasikorn
from plus.KTB import KTB
from plus.Bangkok import Bangkok
from plus.Scbeasy import Scbeasy

m2uModule = Blueprint('m2uModule', 'web_service')

all_web_drivers = {};  #已经有 web 连接的全记录
all_drives_pool = {};  #会话池中还是空闲的全记录
last_proxy_index = {}  #
sub_class_list = Personification.__subclasses__();

def create_one_push_drives_pool(sub_class_list,create_class_name,and_to_list=True,proxy_index=0,order_no=None):
    type_list = Config.ININ_TYPE_LIST
    # print("type=%d"%type)
    for b_class in sub_class_list:
        # 获取子类的类名
        class_name = b_class.__name__
        # print('class_name=%s'%class_name)
        # print('create_class_name=%s'%create_class_name)
        if ( ( create_class_name is not None ) and (create_class_name != class_name) ):
            continue
        # print("-------")
        # print(class_name)
        # print(BankType.Bank[type])
        # print(BankType.Bank[type]['class'])
        # 导入model模块
        model_module = __import__('plus.%s' % class_name)

        for type in type_list:
            if (class_name == BankType.Bank[type]['class']):
                m_py = getattr(model_module, class_name)
                # 根据子类名称从m.py中获取该类
                obj_class_name = getattr(m_py, class_name)
                # 实例化对象
                last_proxy_index[class_name] = proxy_index
                if len(IPPool.ip_list) > proxy_index :
                    pass
                else:
                    proxy_index = None
                bank = obj_class_name(proxy_index,order_no)
                if bank.open_code == Status.o403['actionCode']:
                    if proxy_index is not None:
                        IPPool.refresh_ips(proxy_index)
                    bank = obj_class_name(proxy_index)
                # if (bank is not None and bank.is_open) :
                if and_to_list :
                    all_drives_pool[class_name].append(bank)
                    break
                else:
                    return bank

    return None
                # print('may_drives_pool=%d'%len(all_drives_pool[class_name]))
def status_push():
    print("status_push_job..");
def may_tran(may_obj):
    may_obj.is_goto_transfer = may_obj.goto_transfer();
def async_back_tran(may_obj):
    may_obj.go_transfer_continue();
def finish_check(may_obj):
    may_obj.check_and_find_psw();
def befor():
    pass

@m2uModule.route('/pool',methods=['GET','POST'])
def pool():
    result = Reqult.success();
    result['pool_count'] = len(all_drives_pool)
    result['pool_useed'] = len(all_web_drivers)
    return result

@m2uModule.route('/init',methods=['GET','POST'])
def init():
    logging.warning('*********************************')
    logging.warning('***********init******************')
    logging.warning('*********************************')
    #获取代理端口
    IPPool.get_proxies()
    logging.warning('代理列表：%d'%len(IPPool.ip_list))
    logging.warning(IPPool.ip_list)
    MAX_DRIVER = Config.MAX_DRIVER
    # 获取所有子类
    # sub_class_list =
    # sub_class_list
    # print("0-len=%d" % len(sub_class_list))
    type_list = Config.ININ_TYPE_LIST
    for type in type_list:
        class_name = BankType.Bank[type]['class']
        last_proxy_index[class_name] = 0
    print(last_proxy_index)
    #连接池和会话对象
    for bank in BankType.Bank :
        b_drives_pool = [];
        key = bank['class'];
        all_drives_pool.update({key:b_drives_pool})
    proxy_len = len(IPPool.ip_list)
    proxy_index = 0;
    #先创建最大容量的会话
    for i in range(0,MAX_DRIVER):
        if proxy_len > 1 :
            proxy_index = i%proxy_len
        # print('proxy_index=%d'%proxy_index)
        cidp = Thread(target=create_one_push_drives_pool,args=[sub_class_list,None,True,proxy_index])
        cidp.start();
    path = Config.HTML
    if( not os.path.exists(path) ):
        os.makedirs(path)
    return Reqult.success();

@m2uModule.route('/subscribe',methods=['POST'])
def subscribe():
    logger = None
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        bankName = data['bankName'];
        logger = logging.getLogger(orderNo)
        handler = logging.FileHandler(Config.LOG_PATH+orderNo+".log")
        handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.warning('-------subscribe|%s|%s------------'%(orderNo,bankName))
    except Exception as e:
        print( e )
        logging.warning(e)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not bankName):
            logger.warning('501-fail-参数异常')
            return Reqult.fail_para();
    success = Reqult.success()
    try:
        # 检查订单号是否存在、重复、状态
        o = Order.query.filter(Order.order_no == orderNo).first()
        pool = [];
        bank = None
        pool_type = 2;
        # if ( o is None or (o is not None and o.status == 0 )):
        if ( o is not None ):
            logger.warning('610-fail-订单操作重复')
            return  Reqult.fail_des(610, '订单操作重复');
        if(o is None):
            o = Order(order_no=orderNo,bank_type=bankName,status=1);
            Order.add(o);
        else:
            o.status = 1
        Order.commit()
        print('会话预约')
        bank_type = None
        for bank in BankType.Bank:
            if (bank['val'] == bankName):
                bank_type = bank;
                break
        if (bank_type is None):
            logger.warning('820-fail-bank-error')
            return Reqult.fail_des(820, 'bank-error');
        try:
            pool = all_drives_pool[bank_type['class']]
        except Exception:
            logger.warning('810-fail-会话找不到')
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if( len(pool) == 0 ):
            #没有预加载窗口了就当作是预约新建窗口
            proxy_len = len(IPPool.ip_list)
            proxy_index = 0
            try:
                proxy_index = 1 + last_proxy_index[bank_type['class']]
            except Exception  as e:
                print(e)
                logger.warning('901-fail-银行可能未启用，请联系管理员')
                return Reqult.fail_des(901, '银行可能未启用，请联系管理员')
            if proxy_len > 0:
                proxy_index = proxy_index % proxy_len
            bank = create_one_push_drives_pool(sub_class_list,bank_type['class'],False,proxy_index,orderNo)
            # return Reqult.fail_des(900,'会话池为空，请稍后再试')
            if (bank is None) or not bank.is_open :
                logger.warning(Status.o002)
                return Reqult.status(Status.o002)
        else:
            #还有预加载窗口，则预约时就使用预加载的窗口
            bank = pool[0];
            del pool[0];
            if Config.MAX_DRIVER > 0 :
                MAX_DRIVER = Config.MAX_DRIVER
                MIN_DRIVER = Config.MIN_DRIVER
                INCREMENT_DRIVER = Config.INCREMENT_DRIVER
                plool_len = len(pool);
                print('MAX_DRIVER=%d'%MAX_DRIVER)
                print('MIN_DRIVER=%d'%MIN_DRIVER)
                print('INCREMENT_DRIVER=%d'%INCREMENT_DRIVER)
                print('plool_len=%d'%plool_len)
                if (plool_len <= MIN_DRIVER):
                    add_num = MAX_DRIVER - plool_len;
                    if (add_num >= INCREMENT_DRIVER):
                        add_num = INCREMENT_DRIVER
                    print('add_num=%d'%add_num)
                    proxy_len = len(IPPool.ip_list)
                    for i in range(0, add_num):
                        proxy_index = 1 + last_proxy_index[bank_type['class']]
                        if proxy_len > 0 :
                            proxy_index = proxy_index%proxy_len
                        cidp = Thread(target=create_one_push_drives_pool, args=[sub_class_list,bank_type['class'],proxy_index]);
                        cidp.start()
        # print(len(all_drives_pool[bank_type['class']]))
            if bank is None : #TODO
                logger.warning('901-fail-银行可能未启用，请联系管理员')
                return Reqult.fail_des(901, '银行可能未启用，请联系管理员')
        # 认领窗口
        bank.claim(None, orderNo,logger)
        all_web_drivers[orderNo] = bank
        # reqult = Reqult.success()
        if bank.is_open :
            success['data'] = Status.append_order_no(orderNo,Status.o001)
        else:
            success['data'] = Status.append_order_no(orderNo,Status.o002)
    except Exception as e:
        print(e)
        logger.warning(e)
        success.update({'data': Status.o500})
    return success

@m2uModule.route('/userName',methods=['POST'])
def input_user_name():
    print("***userName***")
    try:
        data = json.loads(request.get_data(as_text=True))
        print(data)
        orderNo = data['orderNo'];
        userName = data['content'];
        bankName = data['bankName'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------userName|%s|%s-----' % (orderNo, bankName))
    except Exception :
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not userName or not bankName):
            return Reqult.fail_para()
    reqult = Reqult.success();
    try:
        # 检查订单号是否存在、重复、状态
        o = Order.query.filter(Order.order_no == orderNo).first()
        pool = [];
        bank = None
        pool_type = 2;
        if ( o is None or (o is not None and o.status == 0 )):
            if(o is None):
                o = Order(order_no=orderNo,bank_type=bankName);
                Order.add(o);
            else:
                o.status = 1
            Order.commit();
            print('新输入用户名，认领会话')
            bank_type = None
            for bank in BankType.Bank:
                if (bank['val'] == bankName):
                    bank_type = bank;
                    break
            if (bank_type is None):
                return Reqult.fail_des(820, 'bank-error')
            try:
                pool = all_drives_pool[bank_type['class']]
            except Exception:
                return Reqult.fail_des(810, '会话找不到');  # 资源找不到
            proxy_len = len(IPPool.ip_list)
            if len(pool) == 0 :
                try:
                    proxy_index = 1 + last_proxy_index[bank_type['class']]
                except Exception:
                    return Reqult.fail_des(901, '银行可能未启用，请联系管理员')
                if proxy_len > 0 :
                    proxy_index = proxy_index % proxy_len
                bank = create_one_push_drives_pool(sub_class_list,bank_type['class'],False,proxy_index)
                # return Reqult.fail_des(900,'会话池为空，请稍后再试')
            else:
                bank = pool[0];
                del pool[0];
            if bank is None :
                return Reqult.fail_des(901, '银行可能未启用，请联系管理员')
            # 认领窗口
            bank.claim(userName, orderNo);
            all_web_drivers[orderNo] = bank;
        else:
            # if( o.action_code >= Status.l130['actionCode'] ):
            #     return Reqult.fail(610);
            # else:
            print('修改用户名，找回会话')
            bank_type = None
            for bk in BankType.Bank:
                if (bk['val'] == o.bank_type):
                    bank_type = bk
                    break
            if ( bank_type is None):
                return Reqult.fail_des(820, 'bank-error')
            wait_index = 0
            while wait_index < 20 :
                try:
                    bank = all_web_drivers[orderNo]
                except Exception as e:
                    print(e )
                    time.sleep(0.5)
                    wait_index+=1
                else:
                    wait_index = 20
                    break
            # print(bank)
            logger.warning(bank)
            if (bank is None) or (not bank.is_open):
                thread = Thread(target=refresh_ip_reopen, args=[bank,orderNo,userName]);
                thread.start()
                success = Reqult.success()
                success['data'] = Status.append_order_no(orderNo,Status.o910)
                logger.warning(success)
                return success  # 页面加载超时
            bank.back_input_name(userName)
            time.sleep(0.4);
        # 去输入
        try:
            actionStatus = bank.input_user_name(userName)
        except Exception as e:
            actionStatus = Status.o500
            bank.print_d(str(e))
            bank.screen(None)
            bank.save_html(str(e))
            reqult.update({'data': actionStatus});
            return reqult;
        o.action_code = actionStatus['actionCode'];
        o.action_msg = actionStatus['actionMsg'];
        o.action_type = actionStatus['actionType'];
        if(actionStatus['actionCode'] == Status.l110['actionCode']):
            o.status = 1;
            # 预先check
            tran_thread = Thread(target=finish_check, args=[bank]);
            tran_thread.start();
        else:
            bank.screen(None)
            bank.save_html(str(actionStatus))
            o.status = 2
            # bank.quit()
            # del all_web_drivers[orderNo]
        Order.commit()
        reqult.update({'data': actionStatus})
    except Exception as e:
        reqult.update({'data': Status.append_order_no(orderNo,Status.o500)})
        print(e)
        logger.warning(e)
    logging.warning('userName-result='+str(reqult))

    # 部分银行需要返回图形验证码
    try:
        captcha_base64 = bank.captcha_base64();
        # print(captcha_base64)
    except Exception as e:
        reqult['data'].update({'captcha': ''});
    else:
        reqult['data'].update({'captcha': captcha_base64});

    return reqult

@m2uModule.route('/login',methods=['POST'])
def login():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'] ;
        userName = data['userName'];
        passWord = data['passWord'];
        toBank = data['toBank'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------login|%s|%s-----' % (orderNo, userName))
    except Exception:
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if ( not orderNo or not userName or not passWord ):
            return Reqult.fail_para();
    captcha = None;
    try:
        captcha = data['captcha'];
    except Exception:
        pass
    reqult = Reqult.success();
    try:
        # 检查订单号是否存在、状态
        o = Order.query.filter(Order.order_no == orderNo).first()
        if (o is None):
            try:
                bankName  = data['bankName']
            except Exception:
                pass
            if (bankName is None):
                return Reqult.fail_des(820, 'bank-error');
            else:
                o = Order(order_no=orderNo, bank_type=bankName);
        elif(o.action_code == Status.l120['actionCode']):
            return Reqult.fail_des(610, '订单操作重复');
        # elif(o.action_code > Status.l132['actionCode']):
        #     return Reqult.fail_des(720, '订单已经完成登录');
        o.action_code = Status.l120['actionCode']
        o.action_msg = Status.l120['actionMsg'];
        o.action_type = Status.l120['actionType'];
        Order.commit()
        #去登录
        bank = None;
        web_drivers = {};
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None):
            return Reqult.fail_des(820, 'bank-error');
        try:
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810, '会话找不到');#资源找不到
        if (not bank.to_bank(toBank)):
            return Reqult.fail_des(830, 'to-bank-error');
        # reqult = Reqult.success();
        try:
            if (captcha is  None):
                actionStatus = bank.input_psw_and_submit(userName, passWord)
            else:
                if((bank_type['class'] == 'KTB') or (bank_type['class'] == 'Kasikorn') or (bank_type['class'] == 'Krungsri')):
                    actionStatus = bank.input_psw_and_submit(userName,passWord, captcha)
                else:
                    actionStatus = bank.input_psw_and_submit(userName, passWord)
            # 用户名密码输入重置
            bank.user_name_input = None;
            bank.psw_input = None;
        except Exception as e:
            actionStatus = Status.o500
            bank.screen(None)
            bank.save_html(str(e))
            reqult.update({'data': actionStatus})
            return reqult;
        o.action_code = actionStatus['actionCode'];
        o.action_msg = actionStatus['actionMsg'];
        o.action_type = actionStatus['actionType'];
        Order.commit()
        if(actionStatus['actionCode'] ==  Status.l130['actionCode']):
            #用户名密码输入重置
            bank.user_name_input = None;
            bank.psw_input = None;
            reqult = login_befor(bank,bank.get_order_no(),reqult)
        elif( actionStatus['actionCode'] ==  Status.o403['actionCode'] ):
            thread = Thread(target=refresh_ip_relogin, args=[bank,userName, passWord]);
            thread.start()
        else :
            reqult.update({'data': actionStatus});
            # bank.screen(None)
            # bank.save_html(str(actionStatus))
            # bank.quit()
            # del all_web_drivers[orderNo];
    except NameError:
        reqult.update({'data': Status.append_order_no(orderNo,Status.o500)})
    logging.warning(reqult)
    return reqult

def refresh_ip_reopen(bank,orderNo,userName):
    wait_loading_index = 0
    while (bank is None) and wait_loading_index < 16:
        try:
            bank = all_web_drivers[orderNo]
        except Exception:
            time.sleep(0.5)
            wait_loading_index += 1
        else:
            wait_loading_index = 20
    if bank is None:
        # bank.sendStatus(bank.get_order_no(), Status.o006)
        return
    # 如果有使用代理，则刷新当前使用代理端口的ip
    if bank.is_use_proxy() and (bank.get_proxy_index() is not None):
        # 刷新当前使用代理端口的ip
        IPPool.refresh_ips(bank.get_proxy_index())
        time.sleep(0.5)
        actionResult = Status.l110
        # 重新打开登录页，输入用户名
        bank.open_and_init()
        if not bank.is_open:
            actionResult = bank.sendStatus(bank.get_order_no(), Status.o006)
            if Config.INVALID_WINDOW_AUTO_CLOSE:
                bank.print_d('-----刷新IP后页面打开异常，INVALID_WINDOW_AUTO_CLOSE=True 直接关闭窗口-----')
                bank.quit()
            else:
                bank.print_d('-----刷新IP后页面打开异常，INVALID_WINDOW_AUTO_CLOSE=False 不需要关闭窗口-----')
            return
        time.sleep(0.5)
        actionStatus = bank.input_user_name(userName)
        time.sleep(0.5)
        # 输入用户名成功
        if actionStatus['actionCode'] == Status.l110['actionCode']:
            actionResult = bank.sendStatus(bank.get_order_no(), Status.o005)
        # 如果代理列表空或者代理的其他问题，异步返回 （"actionCode": 940,"actionMsg": "代理列表为空"|"actionCode": 941,"actionMsg": "代理列表全部不可用"）
        if len(IPPool.ip_list) < 1:
            actionResult = bank.sendStatus(bank.get_order_no(), Status.o940)
    else:
        # 没有使用代理的话异步返回 008
        time.sleep(1)
        actionResult = bank.sendStatus(bank.get_order_no(), Status.o008)
    if actionResult['actionCode'] != Status.l110['actionCode'] :
        if Config.INVALID_WINDOW_AUTO_CLOSE:
            bank.print_d('-----刷新IP后页面打开异常，INVALID_WINDOW_AUTO_CLOSE=True 直接关闭窗口-----')
            bank.quit()
        else:
            bank.print_d('-----刷新IP后页面打开异常，INVALID_WINDOW_AUTO_CLOSE=False 不需要关闭窗口-----')
def refresh_ip_relogin(bank,userName, passWord):
    reqult = Reqult.success()
    # 换 ip 重新登录
    # print(bank.get_proxy_index())
    # print(bank.get_order_no())
    if (bank.get_proxy_index() is None):
        # reqult.update({'data': Status.o501})
        bank.sendStatus(bank.get_order_no(), Status.o501)
        return
    # 刷新 ip
    IPPool.refresh_ips(bank.get_proxy_index())
    # 重新打开
    bank.open_and_init()
    time.sleep(0.5)
    actionStatus = bank.input_user_name(userName)
    time.sleep(0.5)
    # 输入用户名成功
    if (actionStatus['actionCode'] == Status.l110['actionCode']):
        bank.check_and_find_psw()
        time.sleep(0.5)
        actionStatus = bank.input_psw_and_submit(userName, passWord)
        # 登录成功
        if (actionStatus['actionCode'] == Status.l130['actionCode']):
            reqult = login_befor(bank, bank.get_order_no(), reqult)
        else:
            # 登录失败
            reqult = actionStatus
    else:
        # 输入用户名失败
        reqult = actionStatus
    if (reqult['actionCode'] != Status.l130['actionCode']):
        bank.screen(None)
        bank.save_html('刷新ip重新登录:'+str(actionStatus))
        bank.quit()
        del all_web_drivers[bank.get_order_no()]
    bank.sendStatus(bank.get_order_no(), actionStatus)

def login_befor(bank,orderNo,reqult):
    # 取帐号列表
    accountList = [];
    try:
        accountList = bank.account_list();
    except Exception as e :
        print(e);
    if (accountList is None) or len(accountList) == 0:
        logging.warning('帐号列表为空')
        bank.screen(None)
        bank.save_html('帐号列表为空')
    data = {}
    data.update({"orderNo": orderNo})
    data.update({"accountList": accountList})
    data.update({'actionType': 'login'})
    data.update({'actionCode': 130})
    data.update({'actionMsg': '登录成功'})
    reqult.update({'data': data})
    # 预先到转账页
    # bank.goto_transfer();
    tran_thread = Thread(target=may_tran, args=[bank]);
    tran_thread.start();
    return reqult
@m2uModule.route('/m2u/toBePaid',methods=['POST'])
def toBePaid():
    data = json.loads(request.get_data(as_text=True))
    try:
        orderNo = data['orderNo'] ;
        userName = data['userName'];
        passWord = data['passWord'];
    except Exception as e :
        return Reqult.fail_para();
    else:
        if ( not orderNo or not userName or not passWord ):
            return Reqult.fail_para();
    #检查订单号是否存在、重复、状态
    o = Order.query.filter(Order.order_no == orderNo).first()
    if ( o is not None):
        return Reqult.fail(610);

    o = Order(order_no=orderNo);
    #去登录
    bank = None;
    if ( len(all_drives_pool) == 0 ):
        init_thread = Thread(target=init);
        init_thread.start();
        bank = Maybank();
    else:
        bank = all_drives_pool[0];
        del all_drives_pool[0];
        MAX_DRIVER = Config.MAX_DRIVER;
        MIN_DRIVER = Config.MIN_DRIVER;
        INCREMENT_DRIVER = Config.INCREMENT_DRIVER;
        plool_len = len(all_drives_pool);
        if (plool_len <= MIN_DRIVER):
            add_num = MAX_DRIVER - plool_len;
            if (MAX_DRIVER - plool_len > INCREMENT_DRIVER):
                add_num = INCREMENT_DRIVER;
            for i in range(0,add_num):
                cidp = Thread(target=create_one_push_drives_pool,args=[sub_class_list]);
                cidp.start();
        bank.claim(userName, passWord, orderNo);
    # m = Maybank(userName, passWord, orderNo);
    all_web_drivers[orderNo] = bank;
    actionStatus = bank.login();

    reqult = Reqult.success();

    if(actionStatus['actionCode'] == 130):

        o.status = 1;
        o.action_code = actionStatus['actionCode'];
        o.action_msg = actionStatus['actionMsg'];
        o.action_type = actionStatus['actionType'];
        # db.session.add(o);
        # db.session.commit();
        Order.add(o);
        Order.commit();
        #取帐号列表
        accountList = bank.account_list();
        # "actionType": "loading",
        # "actionCode": 000,
        # "actionMsg": "页面加载中",

        data = {}
        data.update({"orderNo": orderNo});
        data.update({"accountList": accountList});
        data.update({'actionType':'login'})
        data.update({'actionCode': 130})
        data.update({'actionMsg':'登录成功'})
        reqult.update({'data':data})
        #预先到转账页
        tran_thread = Thread(target=may_tran, args=[bank])
        tran_thread.start();
        # m.goto_transfer();
    else:
        bank.quit();
        del all_web_drivers[orderNo];
        reqult.update({'data':actionStatus});
    return reqult;

@m2uModule.route('/submitSecurityAnswer',methods=['POST'])
def submitSecurityAnswer():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        # securityQuestion = data['securityQuestion'];
        securityAnswer = data['securityAnswer'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------submitSecurityAnswer|%s|%s-----' % (orderNo, securityAnswer))
    except Exception :
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not securityAnswer):
            return Reqult.fail_para();

    # 检查订单号是否存在、重复、状态
    o = Order.query.filter(Order.order_no == orderNo).first()
    if (o is None):
        return Reqult.fail(710);
    if ( o.status != 1 or ( o.action_code < (Status.l130['actionCode']) ) ):
        return Reqult.fail(720);
    bank = None;
    web_drivers = {};
    bank_type = None
    for type in BankType.Bank:
        if (type['val'] == o.bank_type):
            bank_type = type
            break
    if ( bank_type is None ):
        return Reqult.fail_des(820, 'bank-error');
    try:
        bank = all_web_drivers[orderNo];
    except Exception:
        return Reqult.fail_des(810, '会话找不到');  # 资源找不到
    if (bank is None):
        return Reqult.fail_des(810,'会话找不到');#资源找不到
    reqult = Reqult.success();
    try:
        actionStatus = bank.input_answer(securityAnswer)
    except Exception as e:
        actionStatus = Status.o500
        bank.screen(None)
        bank.save_html(str(e))
        reqult.update({'data': actionStatus})
        return reqult;
    o.action_code = actionStatus['actionCode'];
    o.action_msg = actionStatus['actionMsg'];
    o.action_type = actionStatus['actionType'];
    Order.commit()
    if(actionStatus['actionCode'] ==  Status.l130['actionCode']):
        #取帐号列表
        accountList = bank.account_list()

        data = {}
        data.update({"orderNo": orderNo})
        data.update({"accountList": accountList})
        data.update({'actionType':'login'})
        data.update({'actionCode': 130})
        data.update({'actionMsg':'登录成功'})
        reqult.update({'data':data})
        #预先到转账页
        # bank.goto_transfer();
        tran_thread = Thread(target=may_tran, args=[bank]);
        tran_thread.start();
    else:
        bank.screen(None)
        bank.save_html(str(actionStatus))
        #不关闭了，留着重试
        # bank.quit()
        # del all_web_drivers[orderNo];
        reqult.update({'data':actionStatus});
    logging.warning(reqult)
    return reqult

#输入转账信息转账操作
@m2uModule.route('/setAccountInfo',methods=['POST'])
def setAccountInfo():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        payAccountNumber = data['payAccountNumber'];
        toAccountNumber = data['toAccountNumber'];
        amount = data['amount'];
        reference = data['reference'];
        toBank = data['toBank'];
        toAccountType = data['toAccountType'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------setAccountInfo|%s|-----' %orderNo)
        print(data)
    except Exception :
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not payAccountNumber or not toAccountNumber or not amount or not reference or not toBank):
            return Reqult.fail_para();
    result = Reqult.success()
    success = Reqult.success()
    try:
        # 检查订单号是否存在、重复、状态
        o = Order.query.filter(Order.order_no == orderNo).first()
        if (o is None):
            return Reqult.fail(710);
        # if ( o.status != 1 or ( o.action_code < (Status.l130['actionCode']) ) ):
        #     return Reqult.fail(720);
        bank = None;
        web_drivers = {};
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None ):
            return Reqult.fail_des(820, 'bank-error');
        try:
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');#资源找不到
        if( not bank.to_bank(toBank)):
            return Reqult.fail_des(830, 'to-bank-error');
        success = Reqult.success();
        #如果是 CIMB 需要
        if ( isinstance(bank,CIMB) or isinstance(bank,PBe)):
            paymentType = None
            try:
                paymentType = data['paymentType']
            except Exception:
                pass
            if( paymentType is None):
                return Reqult.fail_para();
        info = {"accountNumber":payAccountNumber,"toBank":toBank}
        try:
            # 选择从哪里转出账号
            result = bank.select_tranfer_info(info);
        except Exception as e:
            actionStatus = Status.o500
            actionStatus['orderNo'] = orderNo
            bank.screen(None)
            bank.save_html(str(e))
            result.update({'data': actionStatus})
            return result;
        if( result['actionCode'] != Status.t230['actionCode'] ):
            bank.screen(None)
            bank.save_html(str(result))
            success.update({'data': result})
            return success;
        time.sleep(1);
        try:
            #输入转入账号、转账金额、备注等信息
            result = bank.input_transfer_info(data);
        except Exception as e:
            bank.screen(None)
            bank.save_html(str(e))
        if (result['actionCode'] != Status.v320['actionCode'] and result['actionCode'] != Status.v290['actionCode'] and result['actionCode'] != Status.t245['actionCode']):
            bank.screen(None)
            bank.save_html(str(result))
        o.action_code = result['actionCode'];
        o.action_msg = result['actionMsg'];
        o.action_type = result['actionType'];
        # db.session.commit();
        Order.commit()
        success.update({'data': result})
    except Exception as e:
        bank.print_d(e)
        success.update({'data': Status.append_order_no(orderNo,Status.o500)})
    logger.warning(success)
    return success
@m2uModule.route('/addAccount',methods=['POST'])
def addAccount():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        accountNumber = data['accountNumber'];
        toBank = data['bank'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------addAccount|%s|-----' %orderNo)
        print(data)
    except Exception :
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not accountNumber or not toBank ):
            return Reqult.fail_para();
    try:
        accountName = data['accountName'];
    except Exception:
        data['accountName'] = accountNumber;

    result = Reqult.success()
    success = Reqult.success()
    try:
        # 检查订单号是否存在、重复、状态9550287203
        o = Order.query.filter(Order.order_no == orderNo).first()
        if (o is None):
            return Reqult.fail(710);
        if ( o.status != 1 or ( o.action_code < (Status.l130['actionCode']) ) ):
            return Reqult.fail(720);
        bank = None;
        web_drivers = {};
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None ):
            return Reqult.fail_des(820, 'bank-error');
        try:
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');#资源找不到
        if( not bank.to_bank(toBank)):
            return Reqult.fail_des(830, 'to-bank-error');
        success = Reqult.success();
        # result = Reqult.success()
        try:
            result = bank.add_account(data);
        except Exception as e:
            actionStatus = Status.o500
            actionStatus['orderNo'] = orderNo
            bank.screen(None)
            bank.save_html(str(e))
            result.update({'data': actionStatus})
            return result;
        if( result['actionCode'] != Status.t291['actionCode'] and result['actionCode'] != Status.t271['actionCode'] ):
            bank.screen(None)
            bank.save_html(str(result))
        o.action_code = result['actionCode'];
        o.action_msg = result['actionMsg'];
        o.action_type = result['actionType'];
        Order.commit()
        success.update({'data': result})
    except Exception:
        success.update({'data': Status.append_order_no(orderNo,Status.o500)})
    logger.warning(success)
    return success

# 设置用户手机信息
@m2uModule.route('/setUserMobile', methods = ['POST'])
def setUserMobile():

    try:
        data = json.loads(request.get_data(as_text = True))
        orderNo = data['orderNo'];
        userMobile = data['userMobile'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------setUserInfo|%s|-----' % orderNo)
        print(data)
    except Exception :
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not userMobile):
            return Reqult.fail_para();

    result = Reqult.success()
    success = Reqult.success()

    try:
        # 检查订单号是否存在、重复、状态9550287203
        o = Order.query.filter(Order.order_no == orderNo).first()

        if (o is None):
            return Reqult.fail(710);
        if (o.status != 1 or (o.action_code < (Status.l130['actionCode']))):
            return Reqult.fail(720);

        bank = None;
        web_drivers = {};
        bank_type = None

        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break

        if (bank_type is None):
            return Reqult.fail_des(820, 'bank-error');

        try:
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到

        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');#资源找不到

        if( not bank.to_bank(toBank)):
            return Reqult.fail_des(830, 'to-bank-error');

        success = Reqult.success();

        try:
            result = bank.set_user_mobile(userMobile);
        except Exception as e:
            actionStatus = Status.o500
            actionStatus['orderNo'] = orderNo
            bank.screen(None)
            bank.save_html(str(e))
            result.update({'data': actionStatus})
            return result;

        if (result['actionCode'] != Status.t291['actionCode']):
            bank.screen(None)
            bank.save_html(str(result))

        o.action_code = result['actionCode'];
        o.action_msg = result['actionMsg'];
        o.action_type = result['actionType'];
        Order.commit()
        success.update({'data': result})

    except Exception:
        success.update({'data': Status.append_order_no(orderNo, Status.o500)})

    logger.warning(success)
    return success

@m2uModule.route('/info',methods=['POST'])
def get_info_success():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        smsCode = data['smsCode'];
        # passWord = data['passWord'];
    except Exception as e:
        return Reqult.fail_para();
    else:
        if (not orderNo or not smsCode):
            return Reqult.fail_para();
    m = None;
    try:
        m = all_web_drivers[orderNo];
    except Exception as e:
        print(e);
    else:
        print(m);
    if (m is None):
        return Reqult.fail_des(810, '会话找不到');  # 资源找不到
    success = Reqult.success();
    result = m.test();
    success.update({'data': result});
    return success;

@m2uModule.route('/setSmsCode',methods=['POST'])
def setSmsCode():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        smsCode = data['smsCode'];
        # passWord = data['passWord'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------setSmsCode|%s|-----' % orderNo)
    except Exception as e:
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not smsCode):
            return Reqult.fail_para();
    success = Reqult.success();
    try:
        # 检查订单号是否存在、重复、状态
        o = Order.query.filter(Order.order_no == orderNo).first();
        if (o is None):
            return Reqult.fail(710);
        # if (o.status != 1 or o.action_code == Status.v340['actionCode']):
        if (o.action_code == Status.v340['actionCode']):
            return Reqult.fail(720);
        bank = None;
        web_drivers = {};
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None):
            return Reqult.fail_des(820, 'bank-error');
        try:
            # web_drivers = all_web_drivers[o.bank_type]
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');  # 资源找不到
        success = Reqult.success();
        try:
            result = bank.input_sms_code(smsCode);
        except Exception as e :
            actionStatus = Status.o500
            bank.screen(None)
            bank.save_html(str(e))
            success.update({'data': actionStatus})
            return success;
        if (result['actionCode'] != Status.v340['actionCode']):
            if ( not isinstance(result['actionMsg'],str) ):
                result['actionMsg'] = Status.v339['actionMsg']
            bank.screen(None)
            bank.save_html(str(result))
            o.status = 2
            #完成后[不主动]关闭窗口
            # bank.quit()
            # del all_web_drivers[orderNo];
        else:
            if (not isinstance(result['actionMsg'], str) ):
                result['actionMsg'] = Status.v340['actionMsg']
            bank.screen(None)
            bank.save_html(str(result))
            o.status = 3
        Order.commit()
        # db.session.commit();
        success.update({'data': result})
        logger.warning(success)
    except Exception:
        success.update({'data': Status.append_order_no(orderNo,Status.o500)})
    return success
@m2uModule.route('/setAddSmsCode',methods=['POST'])
def setAddSmsCode():
    try:
        data = json.loads(request.get_data(as_text=True))
        orderNo = data['orderNo'];
        smsCode = data['smsCode'];
        # passWord = data['passWord'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------setAddSmsCode|%s|-----' % orderNo)
    except Exception as e:
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if (not orderNo or not smsCode):
            return Reqult.fail_para();
    success = Reqult.success();
    try:
        # 检查订单号是否存在、重复、状态
        o = Order.query.filter(Order.order_no == orderNo).first();
        if (o is None):
            return Reqult.fail(710);
        # if (o.status != 1 or o.action_code > Status.t292['actionCode']):
        #     return Reqult.fail(720);
        bank = None;
        web_drivers = {};
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None):
            return Reqult.fail_des(820, 'bank-error');
        # if ( bank_type != BankType.Bank[5]['val']):
        #     return Reqult.fail_des(840, '该银行不支持此操作');
        try:
            # web_drivers = all_web_drivers[o.bank_type]
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');  # 资源找不到
        success = Reqult.success();
        try:
            result = bank.input_add_sms_code(smsCode);
        except Exception as e :
            actionStatus = Status.o500
            bank.screen(None)
            bank.save_html(str(e))
            success.update({'data': actionStatus})
            return success;
        if (result['actionCode'] == Status.t293['actionCode']):
            #成功，继续异步回到转账
            tran_thread = Thread(target=async_back_tran, args=[bank]);
        else:
            if (not isinstance(result['actionMsg'], str) ):
                result['actionMsg'] = Status.v340['actionMsg']
            bank.screen(None)
            bank.save_html(str(result))
            o.status = 3
        Order.commit()
        # db.session.commit();
        success.update({'data': result})
        logger.warning(success)
    except Exception:
        success.update({'data': Status.append_order_no(orderNo,Status.o500)})
    return success

@m2uModule.route('/logout',methods=['POST'])
def logout():
    try:
        data = json.loads(request.get_data(as_text=True));
        orderNo = data['orderNo'];
        # passWord = data['passWord'];
        logger = logging.getLogger(orderNo)
        logger.warning('-------logout|%s|-----' % orderNo)
    except Exception as e:
        logging.warning(data)
        return Reqult.fail_para();
    else:
        logger.warning(data)
        if ( not orderNo ):
            return Reqult.fail_para();
    success = Reqult.success();
    try:
        # 检查订单号是否存在、状态
        o = Order.query.filter(Order.order_no == orderNo).first();
        if (o is None):
            return Reqult.fail(710);
        if (o.status != 1 or o.action_code < 130):
            return Reqult.fail(720);
        bank = None;
        bank_type = None
        for type in BankType.Bank:
            if (type['val'] == o.bank_type):
                bank_type = type
                break
        if ( bank_type is None ):
            return Reqult.fail_des(820, 'bank-error');
        try:
            bank = all_web_drivers[orderNo];
        except Exception:
            return Reqult.fail_des(810, '会话找不到');  # 资源找不到
        if (bank is None):
            return Reqult.fail_des(810,'会话找不到');  # 资源找不到
        success = Reqult.success();
        try:
            result = bank.logout();
        except Exception:
            actionStatus = Status.append_order_no(orderNo,Status.o500)
            bank.screen(None)
            bank.save_html(None)
            success.update({'data': data})
            bank.quit()
            del all_web_drivers[orderNo]
            return success;
        if (result['actionCode'] == 402):
            del all_web_drivers[orderNo]
        o.action_code = result['actionCode'];
        o.action_msg = result['actionMsg'];
        o.action_type = result['actionType'];
        # db.session.commit();
        Order.commit()
        success.update({'data': result})
    except Exception:
        success.update({'data': Status.append_order_no(orderNo,Status.o500)})
    logger.warning(success)
    return success;
# @m2uModule.route('/test',methods=['GET','POST'])
# def test():
#     pass