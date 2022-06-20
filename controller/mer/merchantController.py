import json

from controller.m2u.m2uController import all_drives_pool, all_web_drivers
from dao.Status import Status
from model.BankType import BankType
from model.Result import Reqult
from flask import Blueprint, request,session,jsonify

merchantModule = Blueprint('merchantModule', 'web_service')

# @merchantModule.route('/tranfer_list',methods=['POST'])
# def tranfer_list():
#     try:
#         data = json.loads(request.get_data(as_text=True))
#         accountNum = data['accountNum']
#         userName = data['userName'];
#         passWord = data['passWord'];
#         bankName = data['bankName'];
#     except Exception:
#         return Reqult.fail_para();
#     bank_type = None
#     bank = None
#     for bank in BankType.Bank:
#         if (bank['val'] == bankName):
#             bank_type = bank;
#             break
#     if (bank_type is None):
#         return Reqult.fail_des(820, 'bank-error');
#     try:
#         pool = all_drives_pool[bank_type['class']]
#     except Exception:
#         return Reqult.fail_des(810, '会话找不到');  # 资源找不到
#     if (len(pool) == 0):
#         return Reqult.fail_des(900, '会话池为空，请稍后再试')
#     try:
#         bank = all_web_drivers[accountNum]
#         print('已有窗口')
#     except Exception:
#         bank = pool[0];
#         del pool[0];
#         # 认领窗口
#         print('认领窗口')
#         bank.claim(userName, accountNum);
#         all_web_drivers[accountNum] = bank;
#     else:
#         if( not bank or bank is None):
#             # 认领窗口
#             print('认领窗口')
#             bank.claim(userName, accountNum);
#             all_web_drivers[accountNum] = bank;
#     result = Reqult.success()
#     tranfer_status = bank.get_tranfer_list_status();
#     list =[]
#     data = {}
#     #输入用户名
#     if(0 == tranfer_status):
#         actionStatus = bank.input_user_name();
#         if (actionStatus['actionCode'] == Status.l110['actionCode']):
#             bank.check_and_find_psw();
#         else:
#             data = actionStatus
#     print(tranfer_status)
#     if( 2 > tranfer_status):
#         # 输入密码登录
#         actionStatus = bank.input_psw_and_submit(userName, passWord)
#         if (actionStatus['actionCode'] == Status.l130['actionCode']):
#             # 到账户转账页面
#             action = bank.goto_account_transfer(accountNum);
#             if(action):
#                 list = bank.get_transfer_list();
#             else:
#                 print('没找到对应账户')
#                 data['msg'] = '没找到对应账户'
#         else:
#             data = actionStatus
#     elif( 2 == tranfer_status):
#         # 到账户转账页面
#         action = bank.goto_account_transfer(accountNum)
#         if (action):
#             list = bank.get_transfer_list()
#         else:
#             print('没找到对应账户')
#             data['msg'] = '没找到对应账户'
#     elif(3 == tranfer_status):
#         #重新到 account 并查询
#         bank.goto_account(True)
#         action = bank.goto_account_transfer(accountNum);
#         if (action):
#             list = bank.get_transfer_list()
#             data = Status.t280
#         else:
#             print('没找到对应账户')
#             data['msg'] = '没找到对应账户'
#     data['accountNum'] = accountNum
#     data['tranferList'] = list
#     result['data'] = data
#     return result

@merchantModule.route('/logout',methods=['POST'])
def logout():
    try:
        data = json.loads(request.get_data(as_text=True));
        accountNum = data['accountNum'];
    except Exception as e:
        return Reqult.fail_para();
    else:
        if ( not accountNum ):
            return Reqult.fail_para();
    bank = None;
    try:
        bank = all_web_drivers[accountNum];
    except Exception:
        return Reqult.fail_des(810, '会话找不到');  # 资源找不到
    if (bank is None):
        return Reqult.fail_des(810,'会话找不到');  # 资源找不到
    success = Reqult.success();
    try:
        result = bank.logout();
    except Exception:
        actionStatus = Status.o500
        bank.screen(None)
        bank.save_html(None)
        success.update({'data': data})
        bank.quit()
        return success;
    if (result['actionCode'] == 402):
        del all_web_drivers[accountNum];
        bank.quit()
    success.update({'data': result});
    return success;