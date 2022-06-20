class Status :
    @staticmethod
    def append_order_no(orderNo , status):
        status['orderNo'] = orderNo
        return status
    o000 = {"actionType":"opening","actionCode": 0,"actionMsg": "页面加载中","bankMsg":""}
    o001 = {"actionType":"opening","actionCode": 1,"actionMsg": "页面加载成功","bankMsg":""}
    o002 = {"actionType":"opening","actionCode": 2,"actionMsg": "页面加载异常","bankMsg":""}

    o005 = {"actionType":"opening","actionCode": 5,"actionMsg": "刷新ip后页面加载成功","bankMsg":""}
    o006 = {"actionType":"opening","actionCode": 6,"actionMsg": "刷新ip后页面加载异常","bankMsg":""}
    o007 = {"actionType": "opening", "actionCode": 7, "actionMsg": "强制代理后页面加载成功","bankMsg":""}
    # o008 = {"actionType": "opening", "actionCode": 8, "actionMsg": "强制代理后页面加载异常","bankMsg":""}
    o008 = {"actionType": "opening", "actionCode": 8, "actionMsg": "异步处理逻辑待开发","bankMsg":""}

    o910 = {"actionType":"opening","actionCode": 910,"actionMsg": "页面打开超时","bankMsg":""}
    o940 = {"actionType":"opening","actionCode": 940,"actionMsg": "代理列表为空","bankMsg":""}
    o941 = {"actionType":"opening","actionCode": 941,"actionMsg": "代理列表全部不可用","bankMsg":""}

    # 登录
    l108 = {"actionType": 'login',"actionMsg": '输入用户名',"actionCode":108,"bankMsg":"","bankMsg":""}
    l109 = {"actionType": 'login',"actionMsg": '用户名输入错误',"actionCode":109,"bankMsg":""}
    l110 = {"actionType": 'login',"actionMsg": '用户名输入成功',"actionCode":110,"bankMsg":""}
    l111 = {"actionType": 'login', "actionMsg":'需要验证(Is your security phrase ?)',"actionCode": 111,"bankMsg":""}
    l112 = {"actionType": 'login', "actionMsg": '验证失败',"actionCode":112,"bankMsg":""}
    l113 = {"actionType": 'login', "actionMsg": '验证通过',"actionCode":113,"bankMsg":""}
    l119 = {"actionType": 'login', "actionMsg": '找不到密码输入',"actionCode":119,"bankMsg":""}
    l120 = {"actionType": 'login', "actionMsg": '开始输入密码',"actionCode":120,"bankMsg":""}
    l121 = {"actionType": 'login', "actionMsg": '输入密码异常',"actionCode":121,"bankMsg":""}
    l122 = {"actionType": 'login', "actionMsg": '输入密码成功',"actionCode":122,"bankMsg":""}
    l130 = {"actionType": 'login', "actionMsg": '登录成功',"actionCode":130,"bankMsg":""}
    l131 = {"actionType": 'login', "actionMsg": '登录失败（可能用户名密码错误）',"actionCode":131,"bankMsg":""}
    l132 = {"actionType": 'login', "actionMsg": '登录验证不通过（可重试）',"actionCode":132,"bankMsg":""}
    l140 = {"actionType": 'login', "actionMsg": 'security question detected',"actionCode":140,'question':'captcha',"bankMsg":""}
    l143 = {"actionType": 'login', "actionMsg": '准备输入安全问题',"actionCode":143,"bankMsg":""}
    l144 = {"actionType": 'login', "actionMsg": '找不到安全问题输入',"actionCode":144,"bankMsg":""}
    l150 = {"actionType": 'login', "actionMsg": '找不到图形验证码',"actionCode":150,"bankMsg":""}
    l151 = {"actionType": 'login', "actionMsg": '开始输入图形验证码',"actionCode":151,"bankMsg":""}
    l152 = {"actionType": 'login', "actionMsg": '输入图形验证码异常',"actionCode":152,"bankMsg":""}
    l153 = {"actionType": 'login', "actionMsg": '输入图形验证码成功',"actionCode":153,"bankMsg":""}
    l154 = {"actionType": 'login', "actionMsg": '图形验证码错误',"actionCode":154,"bankMsg":""}

    # 转账
    t200 = {"actionType": 'transfer', "actionMsg":'到支付和转账页面',"actionCode":200,"bankMsg":""}
    t209 = {"actionType": 'transfer', "actionMsg":'还没到转账页面',"actionCode":209,"bankMsg":""}
    t210 = {"actionType": 'transfer', "actionMsg":'到转账页面',"actionCode":210,"bankMsg":""}
    t211 = {"actionType": 'transfer', "actionMsg":'准备选择转账帐号',"actionCode":211,"bankMsg":""}
    t212 = {"actionType": 'transfer', "actionMsg":'没找到指定帐号',"actionCode":212,"bankMsg":""}
    t213 = {"actionType": 'transfer', "actionMsg":'成功选择帐号',"actionCode":213,"bankMsg":""}
    t220 = {"actionType": 'transfer', "actionMsg":'选择转账类型',"actionCode":  220,"bankMsg":""}
    t221 = {"actionType": 'transfer', "actionMsg":'选择转账类型异常',"actionCode":  221,"bankMsg":""}
    t230 = {"actionType": 'transfer', "actionMsg":'选择转账银行成功',"actionCode":230,"bankMsg":""}
    t231 = {"actionType": 'transfer', "actionMsg":'选择转出银行异常',"actionCode":231,"bankMsg":""}
    t235 = {"actionType": 'transfer', "actionMsg":'进入添加账号',"actionCode":235,"bankMsg":""}
    t236 = {"actionType": 'transfer', "actionMsg":'添加账号异常',"actionCode":236,"bankMsg":""}
    t237 = {"actionType": 'transfer', "actionMsg":'添加账号成功',"actionCode":237,"bankMsg":""}
    t240 = {"actionType": 'transfer', "actionMsg":'输入 Account Number',"actionCode":240,"bankMsg":""}
    t241 = {"actionType": 'transfer', "actionMsg":'输入 Transfer Amount',"actionCode":241,"bankMsg":""}
    t242 = {"actionType": 'transfer', "actionMsg":'输入 Reference',"actionCode": 242,"bankMsg":""}
    t243 = {"actionType": 'transfer', "actionMsg":'输入转账信息异常',"actionCode": 243,"bankMsg":""}
    t244 = {"actionType": 'transfer', "actionMsg":'输入转账信息成功',"actionCode": 244,"bankMsg":""}
    t245 = {"actionType": 'transfer', "actionMsg":'转账账号不在列表中，需要添加',"actionCode": 245,"bankMsg":""}
    t250 = {"actionType": 'transfer', "actionMsg":'点击 TRANSFER',"actionCode":250,"bankMsg":""}
    t260 = {"actionType": 'transfer', "actionMsg":'成功生成转账订单',"actionCode":260,"bankMsg":""}
    t261 = {"actionType": 'transfer', "actionMsg":'生成转账订单异常',"actionCode":261,"bankMsg":""}
    t280 = {"actionType": 'transfer', "actionMsg":'生成转账订单成功',"actionCode":280,"bankMsg":""}
    t271 = {"actionType": 'transfer', "actionMsg":'需要输入付款手机号码',"actionCode":271,"bankMsg":""}
    t272 = {"actionType": 'transfer', "actionMsg":'输入付款手机号码异常',"actionCode":272,"bankMsg":""}
    t273 = {"actionType": 'transfer', "actionMsg":'输入付款手机号码成功',"actionCode":273,"bankMsg":""}
    t291 = {"actionType": 'transfer', "actionMsg":'需要输入验证码',"actionCode":291,"bankMsg":""}
    t292 = {"actionType": 'transfer', "actionMsg":'输入验证码异常',"actionCode":292,"bankMsg":""}
    t293 = {"actionType": 'transfer', "actionMsg":'输入验证码成功',"actionCode":293,"bankMsg":""}

    # 验证
    v290 = {"actionType": 'verify', "actionMsg":'在手机上完成 TAC 验证',"actionCode": 290,"bankMsg":""}
    v300 = {"actionType": 'verify', "actionMsg":'选择验证方式为 SMS TAC(Secure Verification)',"actionCode": 300,"bankMsg":""}
    v310 = {"actionType": 'verify', "actionMsg":'点击 REQUEST',"actionCode": 310,"bankMsg":""}
    v315 = {"actionType": 'verify', "actionMsg":'准备发送验证码',"actionCode": 315,"bankMsg":""}
    v319 = {"actionType": 'verify', "actionMsg":'发送验证码失败',"actionCode": 319,"bankMsg":""}
    v320 = {"actionType": 'verify', "actionMsg":'发送验证码成功',"actionCode": 320,"bankMsg":""}
    v321 = {"actionType": 'verify', "actionMsg":'准备开始输入验证码',"actionCode": 321,"bankMsg":""}
    v322 = {"actionType": 'verify', "actionMsg":'查找验证码输入异常',"actionCode": 322,"bankMsg":""}
    v330 = {"actionType": 'verify', "actionMsg":'准备输入验证码',"actionCode":330,"bankMsg":""}
    v331 = {"actionType": 'verify', "actionMsg":'查找转账确认异常',"actionCode":331,"bankMsg":""}
    v332 = {"actionType": 'verify', "actionMsg":'点击确认转账',"actionCode":332,"bankMsg":""}
    v333 = {"actionType": 'verify', "actionMsg":'输入验证码异常',"actionCode":333,"bankMsg":""}
    v334 = {"actionType": 'verify', "actionMsg":'输入验证码成功',"actionCode":334,"bankMsg":""}
    v339 = {"actionType": 'verify', "actionMsg":'转账失败（未知原因）',"actionCode":339,"bankMsg":""}
    v340 = {"actionType": 'verify', "actionMsg":'Your transfer is success',"actionCode":340,"bankMsg":""}
    v341 = {"actionType": 'verify', "actionMsg":'转账失败（验证码错误）',"actionCode":341,"bankMsg":""}

    v342 = {"actionType": 'verify', "actionMsg":'再次输入验证码',"actionCode":342,"bankMsg":""}
    v343 = {"actionType": 'verify', "actionMsg":'再次转账',"actionCode":343,"bankMsg":""}
    v344 ={"actionType": 'verify', "actionMsg":'Your transfer is success',"actionCode":344,"bankMsg":""}
    v345 ={"actionType": 'verify', "actionMsg":'转账失败',"actionCode":345,"bankMsg":""}
    v350 ={"actionType": 'verify', "actionMsg":'转账信息拒绝',"actionCode":350,"bankMsg":""}

    #其他
    o400 ={"actionType": 'other', "actionMsg":'准备退出',"actionCode":400,"bankMsg":""}
    o401 ={"actionType": 'other', "actionMsg":'主动退出异常',"actionCode":401,"bankMsg":""}
    o402 ={"actionType": 'other', "actionMsg":'主动退出成功',"actionCode":402,"bankMsg":""}
    o403 ={"actionType": 'other', "actionMsg":'被拒绝连接',"actionCode":403,"bankMsg":""}
    o404 ={"actionType": 'other', "actionMsg":'System Downtime',"actionCode":404,"bankMsg":""}
    o410 ={"actionType": 'other', "actionMsg":'session过期退出',"actionCode":410,"bankMsg":""}
    o420 ={"actionType": 'transfer', "actionMsg": 'The status of your order is incorrect', "actionCode": 420,"bankMsg":""}
    o430 ={"actionType": 'other', "actionMsg":'不可逆异常',"actionCode":430,"bankMsg":""}
    o500 ={"actionType": 'other', "actionMsg":'系统异常',"actionCode":500,"bankMsg":""}
    o501 ={"actionType": 'other', "actionMsg":'需要更换ip，但未启用代理',"actionCode":501,"bankMsg":""}

    #附加
    p610 = {"actionType": 'plus', "actionMsg":'订单操作重复',"actionCode":610,"bankMsg":""}
    p710 = {"actionType": 'plus', "actionMsg":'订单号不存在',"actionCode":710,"bankMsg":""}
    p810 = {"actionType": 'plus', "actionMsg":'资源找不到',"actionCode":810,"bankMsg":""}
    p820 = {"actionType": 'plus', "actionMsg":'bank-error',"actionCode":820,"bankMsg":""}
    p830 = {"actionType": 'plus', "actionMsg":'to-bank-error',"actionCode":830,"bankMsg":""}
