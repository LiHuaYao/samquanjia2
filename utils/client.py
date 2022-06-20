import requests
import json
from threading import Thread
import logging
from requests import ConnectTimeout
from requests.exceptions import ProxyError, TooManyRedirects, HTTPError, Timeout,ConnectionError

from config import Config


def post_requests(status,path):
    try:
        requests.post(url=Client.host+path, headers=Client.headers, data=json.dumps(status))
    except ConnectTimeout:
        print((Client.host+path)+':ConnectTimeout-连接超时')
        logging.warning((Client.host+path)+':ConnectTimeout-连接超时')
    except ConnectionError:
        print((Client.host+path)+':未知的服务器')
        logging.warning((Client.host+path)+':ConnectionError-未知的服务器')
    except ProxyError:
        print((Client.host+path)+':ProxyError-代理连接不上')
        logging.warning((Client.host + path) + ':ProxyError-代理连接不上')
    except TooManyRedirects:
        logging.warning((Client.host+path)+':TooManyRedirects-请求超过了设定的最大重定向次数')
    except HTTPError:
        logging.warning((Client.host+path)+':HTTPError-HTTP请求返回了不成功的状态码')
    except Timeout:
        logging.warning((Client.host+path)+':Timeout-请求超时')


class Client:
    ## headers中添加上content-type这个参数，指定为json格式
    headers = {'Content-Type': 'application/json','Connection':'close'}
    host = Config.BG_HOST
    # host = 'http://pj6twh.natappfree.cc'
    update_status_url = host+'/mmb/notify';
    account_list_url = host+'/account';

    @staticmethod
    def sendStatus(order_no,status,path):
        status.update({"orderNo": order_no});
        ## post,转换成json格式。
        update_status_path = path;
        post = Thread(target=post_requests, args=[status,path]);
        post.start();
        # print(post);
        return status;
    @staticmethod
    def send_account_list(order_no,account_list):
        account_list.update({"orderNo": order_no});
        print(account_list);
        ## post,转换成json格式。
        try:
            requests.post(url=Client.account_list_url, headers=Client.headers, data=json.dumps(account_list))
        except ConnectTimeout :
            print('ConnectTimeout-连接超时')
            logging.warning('ConnectTimeout-连接超时')
        except ConnectionError:
            print('未知的服务器')
            logging.warning('ConnectionError-未知的服务器')
        except ProxyError:
            print('ProxyError-代理连接不上')
        except TooManyRedirects:
            logging.warning('TooManyRedirects-请求超过了设定的最大重定向次数')
        except HTTPError:
            logging.warning('HTTPError-HTTP请求返回了不成功的状态码')
        except Timeout:
            logging.warning('Timeout-请求超时')
