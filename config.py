import os

class Config(object):
    JOBS = [{
        'id': 'session_check',  # 检查跟银行会话窗口是否有过期，有的话就关闭
        'func': '__main__:session_check',
        'args': None,
        'trigger': 'interval',
        'seconds': 60
    },{
        'id': 'update_proxy_server_list',  # 更新代理服务列表
        'func': '__main__:update_proxy_server_list',
        'args': None,
        'trigger': 'interval',
        'seconds': 100
    },
    # {
    #     'id': 'check_proxy_server',  # 检查端口代理服务是否正常可用
    #     'func': '__main__:check_proxy_server',
    #     'args': None,
    #     'trigger': 'interval',
    #     'seconds': 120
    # }
    ]  # 任务
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    SCHEDULER_API_ENABLED = True
    MAX_DRIVER = 0  #最大预会话窗口数（会话池中空闲的最大会话数）
    INCREMENT_DRIVER = 1 #每次新增会话窗口数
    MIN_DRIVER = 1 #最小会话窗口数，（会话池中空闲的会话数）小于、等于此值的时候按 INCREMENT_DRIVER 新增
    SESSION_VALID_TIME = 300 #单位秒 小于零时表示session不过期，尽量不要跟 session_check 一样或太接近倍数，定时job执行可能会有几秒的偏差
    LINUX_KILL_ENABLED = False  # 启用linux下进程清理
    LINUX_KILL_RUN_TIME = 600  # linux下运行时间达到LINUX_KILL_RUN_TIME并且占用 CPU 时间达到LINUX_KILL_USE_CPU_TIME的进程会被清理
    #linux下运行时间达到LINUX_KILL_RUN_TIME并且[平均每秒]占用 CPU 时间达到LINUX_KILL_USE_CPU_TIME_RATIO（表示进程已经活跃过）的进程会被清理
    LINUX_KILL_USE_CPU_TIME_RATIO = 0.2  # 取值接近25-30/LINUX_KILL_RUN_TIME
    BAI_DU_ACCESS_TOKEN = "24.10d6644271da9fc5db462f30f4a35e5c.2592000.1606301612.282335-22877972" #百度 API token 目前 scb汇商键盘识别使用，有效期一个月

    # mysql+pymysql://用户名称:密码@localhost:端口/数据库名称
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.getenv('DB_USERNAME', 'root') + ':' + os.getenv('DB_PASSWORD', '') + '@' + os.getenv(
    #     'DB_HOST', 'localhost') + ':3306/' + os.getenv('DB_NAME', 'm2u')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.getenv('DB_USERNAME', 'root') + ':' + os.getenv('DB_PASSWORD', '123456') + '@' + os.getenv(
        'DB_HOST', '127.0.0.1') + ':3306/' + os.getenv('DB_NAME', 'm2u')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # mqsql 关联修改

    WEB_PORT = os.getenv('WEB_PORT', 8080)  # web 服务的端口
    CHROME_DRIVER = os.getenv('CHROME_DRIVER', '/usr/local/bin/chromedriver')  # chromedriver 路径
    DEBUG = True  # web 服务的调试模式
    SECRET_KEY = 'm_service_plus'  # web 服务的SECRET_KEY
    # BG_HOST = 'http://127.0.0.1:8081' #回调host
    BG_HOST = os.getenv('BG_HOST', 'http://kmih9n.natappfree.cc')  # 回调host

    DEBUG_LOG = True  # 是否输出调试日志
    ININ_TYPE_LIST = [4,5,6,9,10]  # 初始化会话窗口类型 0：Maybank，1：Hlb，2：CIMB，3：PBebank，4:Krungsri,5:Kasikorn,6:KTB,9:bangkokbank   #BankType.py BankType.Bank 的下标
    SCREEN = './screen/'  # 异常时截图目录
    HTML = './html/'  # 异常时html保存目录
    LOG_PATH = './logs/'  # 日志文件
    CAPTCHA = './captcha/'    # 验证码

    #LPM
    LPM_HOST = os.getenv('LPM_HOST', 'http://127.0.0.1')  # lpm服务的地址
    LPM_PORT = os.getenv('LPM_PORT', 22999)  # lpm服务的端口
    MAX_DENIED_COUNT = os.getenv('MAX_DENIED_COUNT', 2)  # 一个代理端口最大拒绝次数（被 denied 几次后换ip）
    #Luminati
    LUM_CUSTOMER = 'hl_f11c6075'
    LUM_USERNAME = 'someoneda30@gmail.com'
    LUM_PASSWORD = 'zaq12WSX'

    INVALID_WINDOW_AUTO_CLOSE = True   #打开页面不成功的窗口是否自动关闭

    CHECK_OPEN_URL = "https://www.cimbclicks.com.my/clicks/#/" #检查测试代理是否可用的链接
    CHECK_OPEN_NO_IMAGE = True      #检查测试使用无图模式 无图省流量

    class Maybank:
        OPEN_URL = "https://www.maybank2u.com.my/home/other/common/login.do"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        TRANSACTION_TYPE = -1  # 0:Funds Transfer 1:Credit Card   2:Loan Payment（-1时默认）  3:Hire Purchase
        TRANSFER_MODE = -1  # 0:Instant Transfer（-1时默认）  1:Interbank GIRO
        US_PROXY_SERVER = False  #  是否使用代理访问
        OPEN_TIME_OUT = 20 #打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 50 #查找用户名输入超时时间 （秒）

    class Hlb:
        OPEN_URL = "https://s.hongleongconnect.my/rib/app/fo/login"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        ACCOUNT_TYPE = -1   # 0:Current/Savings（-1时默认）, 1:Credit Card, 2:Loan, 3:'Share Margin Financing']
        US_PROXY_SERVER = False  # 是否使用代理访问
        OPEN_TIME_OUT = 5  # 打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 10  # 查找用户名输入超时时间 （秒）
        RETURN_SAFETY_PIC = False # 读取预留图片
        AFTER_INPUT_NAME_TIME_OUT = 8 #输入用户名后操作超时时间 （秒）

    class CIMB:
        OPEN_URL = "https://www.cimbclicks.com.my/clicks/#/"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        TRANSFER_METHOD = 1 # 0:Normal Transfer, 1:Instant Transfer(默认，目前仅支持Instant，Normal方式需要开发)
        PAYMENT_TYPE  = 0 #setAccountInfo接口传参，这里配置无效 0:Funds Transfer ,1:Credit Card ,2: Loans
        US_PROXY_SERVER = True  # 是否使用代理访问
        OPEN_TIME_OUT = 20  # 打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 30  # 查找用户名输入超时时间 （秒）

    class PBebank:
        OPEN_URL = "https://www2.pbebank.com/myIBK/apppbb/servlet/BxxxServlet?RDOName=BxxxAuth&MethodName=login"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  # 是否使用代理访问
        OPEN_TIME_OUT = 60  # 打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 10  # 查找用户名输入超时时间 （秒）

    #大成银行
    class Krungsri:
        OPEN_URL = "https://www.krungsrionline.com/BAY.KOL.WebSite/Common/Login.aspx?language=EN"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  # 是否使用代理访问
        OPEN_TIME_OUT = 60  # 打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 10  # 查找用户名输入超时时间 （秒）
        USE_NO_IMAGE = True  # 是否使用无图模式

    #开泰银行
    class Kasikorn:
        OPEN_URL = "https://online.kasikornbankgroup.com/K-Online/login.jsp?lang=EN"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  # 是否使用代理访问
        OPEN_TIME_OUT = 20  # 打开初始url 超时时间（秒）

    # 泰京银行
    class KTB:
        OPEN_URL = "https://www.ktbnetbank.com/consumer"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  #  是否使用代理访问
        OPEN_TIME_OUT = 20 #打开初始url 超时时间（秒）

    # 盘古银行
    class Bangkok:
        OPEN_URL = "https://ibanking.bangkokbank.com/SignOn.aspx"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  #  是否使用代理访问
        OPEN_TIME_OUT = 20 #打开初始url 超时时间（秒）

    #汇商银行
    class Scbeasy:
        OPEN_URL = "https://www.scbeasy.com/v1.4/site/presignon/index_en.asp"  # 初始url
        STATUS_PATH = '/mmb/notify'  # 状态异步更新地址
        US_PROXY_SERVER = False  # 是否使用代理访问
        OPEN_TIME_OUT = 60  # 打开初始url 超时时间（秒）
        FIND_USER_NAME_TIME_OUT = 10  # 查找用户名输入超时时间 （秒）
        USE_NO_IMAGE = False  # 是否使用无图模式
        USE_NO_FLASH = False  # 禁用 flash
