import json

from model.Result import Reqult
from flask import Blueprint, request,session,jsonify

indexModule = Blueprint('indexModule', 'web_service')

@indexModule.route('/')
def index():
    return Reqult.success();
@indexModule.route('/set')
def set():
    name = request.args['name'];
    print(name);
    session['name'] = name;
    return Reqult.success();

def may_login(may_obj):
    result = may_obj.login();
    print("_______%d_____"%result);
def account_list(may_obj):
    may_obj.account_list();
    return
@indexModule.route('/login')
def login():
    
    return jsonify(Reqult.success())

@indexModule.route('/goTranfer')
def goto_tran():
    return jsonify(Reqult.success())


@indexModule.route('/account_list')
def accountList():
    return jsonify(Reqult.success())

@indexModule.route('/get', methods=['POST','GET'])
def get():
    # username + psw + amount
    form = request.form;
    valus = request.values;
    data = request.data;
    args = request.args;
    print(form);
    print(valus);
    print(data);
    print(args);
    name = session.get('name');
    print("name=%s"%name)

    return jsonify(Reqult.data(200,name))

@indexModule.route('/sms_code', methods=['POST'])
def sms_code():
    #username + code
    data = request.get_data();
    if not data:
        return jsonify(Reqult.fail());
    json_data = json.loads(data.decode('utf-8'))
    return jsonify(json_data)
