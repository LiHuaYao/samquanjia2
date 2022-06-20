import urllib.request
from urllib.error import URLError

import logging
import requests

from config import Config
from urllib import request, parse
import json
import sys
import ssl

from model import BankType


class ProxyObj(object):
    def __init__(self, proxy=None, zone=None, port=None):
        self.proxy = proxy
        self.zone = zone
        self.port = port
        self.denied_count = 0
class IPPool:
    ip_list= []
    headers = {'Content-Type':'application/json'}
    def refresh_session(self):
        pass
    @staticmethod
    def is_use_proxy(bankName):
        if bankName == BankType.BankType.Bank[0]['val']:
            return  Config.Maybank.US_PROXY_SERVER
        elif bankName == BankType.BankType.Bank[1]['val']:
            return Config.Hlb.US_PROXY_SERVER
        elif bankName == BankType.BankType.Bank[2]['val']:
            return Config.CIMB.US_PROXY_SERVER
        elif bankName == BankType.BankType.Bank[3]['val']:
            return Config.PBebank.US_PROXY_SERVER
        elif bankName == BankType.BankType.Bank[4]['val']:
            return Config.KTB.US_PROXY_SERVER
    @staticmethod
    def move_proxy(del_proxy_index):
        del IPPool.ip_list[del_proxy_index]
    @staticmethod
    def get_proxies():
        proxies_url = str(Config.LPM_HOST) +':'+ str(Config.LPM_PORT) + '/api/proxies_running'
        print("proxies_url=%s" %proxies_url)
        try:
            rep = urllib.request.urlopen(proxies_url)
        except URLError :
            return
        json_str = rep.read().decode('utf-8')
        # print(json_str)
        proxies = json.loads(json_str)
        IPPool.ip_list = []
        for pro in proxies:
            try:
                if pro['proxy_type'] == 'persist':
                    print (pro)
                    pb = ProxyObj(str(Config.LPM_HOST) +':'+ str(pro['port']),pro['zone'],pro['proxy_port'])
                    IPPool.ip_list.append(pb)
            except Exception as e:
                print(e)
                continue

    @staticmethod
    def refresh_ips(proxy_index):
        # logging.warning('refresh_ips')
        proxy = IPPool.ip_list[proxy_index]
        refresh_ips_url = 'https://luminati.io/api/zone/ips/refresh'
        if type(proxy) != ProxyObj:
            # print('refresh_ips：参数类型不对')
            return
        del_proxy_index=proxy_index
        print('refresh_ips-del_proxy_index=%d'%del_proxy_index)
        logging.warning('refresh_ips-del_proxy_index=%d'%del_proxy_index)
        del IPPool.ip_list[del_proxy_index]
        data = {"customer":Config.LUM_CUSTOMER,"zone":proxy.zone}
        # print(data)
        try:
            response = requests.post(url=refresh_ips_url, headers=IPPool.headers, data=json.dumps(data),auth=(Config.LUM_USERNAME,Config.LUM_PASSWORD))
            # print(response)
            info = response.json()
            logging.warning(info)
            new_ip = None
            if info and info['new_ips']:
                new_ip = info['new_ips'][0]
                print('new_ip=%'%new_ip)
                logging.warning('new_ip=%'%new_ip)
                proxy.denied_count = 0
                IPPool.ip_list.append(proxy)
        except Exception:
            pass
        #curl -X POST "https://luminati.io/api/zone/ips/refresh" -H "Content-Type: application/json" -d '{"customer":"hl_f11c6075","zone":"zone1"}' -u "someoneda30@gmail.com:zaq12WSX"

    @staticmethod
    def test_proxies():
        import urllib.request
        ctx = ssl.create_default_context()
        ctx.verify_flags = ssl.VERIFY_DEFAULT
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({'http': 'http://13.228.170.102:24004'}),
            urllib.request.HTTPSHandler(context=ctx))
        print(opener.open('https://lumtest.com/myip.json').read())
if __name__ == '__main__':
    IPPool.test_proxies()