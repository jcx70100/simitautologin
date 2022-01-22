import urllib.request
import http.cookiejar
import random
import json
import time
import subprocess
import platform
import traceback


def sleep(seconds):
    for _ in range(seconds):
        time.sleep(1)

def getTimeStr():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

def getRandomString(n = 32):
    _char = 'abcdefghijklmnopqrstuvwxyz0123456789'.upper()
    return ''.join((_char[random.randint(0, len(_char)-1)] for _ in range(n)))

def login(username, password):
    if username is None or password is None:
        raise IncompleteFieldException()
    
    url = 'http://172.16.1.28:8080/PortalServer/Webauth/webAuthAction!login.action'
    data = {'userName': username,
            'password': password,
            'hasValidateCode': 'false',
            'validCode': '',
            'hasValidateNextUpdatePassword': 'true'}
    postdata = urllib.parse.urlencode(data).encode('utf-8')
    header = {'Accept': '*/*',
              'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'JSESSIONID': getRandomString(32),
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62'}

    request = urllib.request.Request(url, postdata, header)
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    response = opener.open(request)
    result = response.read().decode('utf-8')
    result_obj = json.loads(result)
    return result_obj

def sync(ipAddr, sessionID, XSRF_TOKEN):
    url = 'http://172.16.1.28:8080/PortalServer/Webauth/webAuthAction!syncPortalAuthResult.action'
    data = {'clientIp': ipAddr,
            'browserFlag': 'zh'}
    postdata = urllib.parse.urlencode(data).encode('utf-8')
    header = {'Accept': '*/*',
              'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
              'JSESSIONID': getRandomString(32),
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62',
              'X-Requested-With': 'XMLHttpRequest',
              'X-XSRF-TOKEN': XSRF_TOKEN,
              'Cookie': 'JSESSIONID='+sessionID+'; '+'XSRF_TOKEN='+XSRF_TOKEN}
    request = urllib.request.Request(url, postdata, header)
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    response = opener.open(request)
    result = response.read().decode('utf-8')
    result_obj = json.loads(result)
    return result_obj
    
if __name__ == '__main__':

    DEBUG = False
    
    print('''
本工具可实现研究所内网络自动登录
为防止任何可能的不利结果（包括但不限于中毒、数据丢失等）
请安装并及时更新安全防护工具！
===============================================
成功登陆后，请保持本窗开启，最小化即可！
版本信息 v0.2
开源地址 https://github.com/jcx70100/simitautologin.git
    
    ''')
    print(getTimeStr(), 'SIMIT Auto Loginer has started.')
    sleep(1)
    USERNAME = str(input(getTimeStr()+" Plz input your account: "))
    PASSWORD = str(input(getTimeStr()+" Plz input your password: "))

    if DEBUG:
        print(getTimeStr(), 'Run in Debug Mode.')
        
    while True:
        try:
            ping_command = ('ping -W 1 -c 1 ', 'ping -w 1000 -n 1 ')['Windows' in platform.system()]
            domain_name = 'www.qq.com'
            s = subprocess.Popen(ping_command + domain_name,
                                 shell=True,
                                 stdout=(subprocess.PIPE, None)[DEBUG],
                                 stderr=(subprocess.PIPE, None)[DEBUG])
            s.wait()
            sleep(5)
            if s.returncode == 0 and not DEBUG:
                pass
            else:
                print(getTimeStr(), 'Authenticating...')
                login_result = login(USERNAME, PASSWORD)
                if DEBUG:
                    print(login_result)
                try:
                    message = login_result['message']
                    IP = login_result['data']['ip']
                    sessionID = login_result['data']['sessionId']
                    token = login_result['token'][6:]
                except TypeError:
                    print(getTimeStr(), message)
                    continue
                for i in range(15):
                    print(getTimeStr(), 'Synchronizing... ', end=' ')
                    sync_result = sync(IP, sessionID, token)
                    if DEBUG:
                        print(sync_result)
                    try:
                        status = sync_result['data']['portalAuthStatus']
                    except TypeError:
                        print(getTimeStr(), message)
                        continue
                    if status == 0:
                        print('Waiting...')
                    elif status == 1:
                        print('Connected.')
                        break
                    elif status == 2:
                        print('Auth Failed!')
                        break
                    else:
                        errorcode = sync_result['data']['portalErrorCode']
                        if errorcode == 5:
                            print('Exceed maximum device capacity!')
                        elif errorcode == 101:
                            print('Passcode error!')
                        elif errorcode == 8000:
                            print('Radius relay auth failed, errorcode =', errorcode - 8000)
                        else:
                            print('Auth Failed!')
                        break
                    sleep(3)
        except Exception as e:
            print(getTimeStr(), 'Unhandled Exception!')
            print(getTimeStr(), repr(e))
            traceback.print_exc()


