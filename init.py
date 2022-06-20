from config import Config
import urllib.request
import time
class Init():
    @staticmethod
    def window():
        time.sleep(4);
        url = 'http://127.0.0.1:' + str(Config.WEB_PORT) + '/m2u/init'
        print("init-url=%s"%url)
        urllib.request.urlopen(url)

if __name__ == '__main__':
    Init.window();