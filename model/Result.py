import logging


class Reqult:
    @staticmethod
    def success():
        logging.warning('200-success-调用成功')
        return {'code':200, 'msg':'success','des':'调用成功'};
    @staticmethod
    def fail(code):
        print('code=%d'%code)
        logging.warning('fail-code=%d'%code)
        return Reqult.data(code,'fail','')
    @staticmethod
    def fail_des(code,des):
        logging.warning('fail-code:%d-des:%s'%(code,des))
        return Reqult.data(code,'fail',des)
    @staticmethod
    def status(status):
        #{"actionType":"opening","actionCode": 2,"actionMsg": "页面加载异常"}
        logging.warning('fail-code:%d-des:%s'%(status['actionCode'],status['actionMsg']))
        return Reqult.data(status['actionCode'],'fail',status['actionMsg'])
    @staticmethod
    def fail_para():
        logging.warning('501-fail-参数异常')
        return Reqult.data(501,'fail','参数异常');
    @staticmethod
    def data(code,msg,des):
        logging.warning('code:%d-msg:%s-des:%s'%(code,msg,des))
        return {'code':code, 'msg':msg,'des':des}


