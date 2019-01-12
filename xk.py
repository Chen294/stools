#-- coding:utf-8 --
# python 3.7.1

# NOTE: 
# 1. You need to finish function `recognizeCaptcha` yourself, or invalid after several POSTs
# 2. Every N times script pretends to relogin. Using `/%` in vim to find N
# 3. Other settings (like id number, password or something) are edited in `conf.toml`
# 4. Script is friendly to server
# 5. No sharing, just for study

import http.cookiejar
import urllib.request
import re
import time
import random
import toml

########################################################################
# func

def getEncodedPost(json_info):
    return urllib.parse.urlencode(json_info).encode()

# [FIXME] This part is not open-source. Finish it by your on way, please.
def recognizeCaptcha(data):
    return ''

def queryKyl(course_code, course_no):
    postjson = getEncodedPost({
        'searchtj': course_code,
        'xq': '0',
        'jc': '0',
        'kyl': '0',
        'kclbdm': ''
    })
    try:
        response = urllib.request.urlopen("http://202.115.47.141/student/courseSelect/freeCourse/courseList", postjson)
        search_list = re.findall(r'bkskyl.*sflbdm', response.read().decode('utf-8'))
        for cour in search_list:
            if course_no == re.findall(r'(?<="kxh\\":\\").*?(?=\\)', cour)[0]:
                remain = re.findall(r'(?<=bkskyl\\":).*?(?=,)', cour)[0]
                return remain > '0'    # includes minus number
        else:
            return False
    except:
        return False

# select
def applySelection(course_code, course_no):
    # token
    token = getToken()
    if not token:
        return (False, 'No token.')
    # captcha
    try:
        response = urllib.request.urlopen('http://202.115.47.141/student/courseSelect/selectCourse/getYzmPic')
        captcha = recognizeCaptcha(response.read())
    except:
        return (False, 'Captcha recognition failed.')
    # posting
    try:
        postjson = getEncodedPost({
            'dealType' : '5',
            'kcIds': course_code + '_' + course_no + '_' + term + '-1',  # course id
            'kcms': '',         # course name (can be ignored)
            'fajhh': '3623',
            'sj': '0_0',
            'searchtj': course_code,     # search keyword (can be ignored)
            'kclbdm': '',
            'inputCode': captcha,
            'tokenValue': token
        })
        response = urllib.request.urlopen("http://202.115.47.141/student/courseSelect/selectCourse/checkInputCodeAndSubmit", postjson)
        if 'ok' not in response.read().decode('utf-8'):
            return (False, 'Captcha post failed.')
        postjson = getEncodedPost({
            'dealType' : '5',
            'kcIds': course_code + '_' + course_no + '_' + term + '-1',  # course id
            'kcms': '',         # course name (can be ignored)
            'fajhh': '3623',
            'sj': '0_0',
            'searchtj': course_code,     # search keyword (can be ignored)
            'kclbdm': ''
            # 'inputCode': '',
            # 'tokenValue': token
        })
        response = urllib.request.urlopen("http://202.115.47.141/student/courseSelect/selectCourses/waitingfor", postjson)
    except urllib.error.URLError:
        return (False, 'Server busy, when posting selection json.')
        # pass
    else:
        global username
        postjson = getEncodedPost({
            'kcNum': '1',
            'redisKey': str(username) + '5'
        })
        for _ in range(0, 4):
            time.sleep(interval)
            try:
                response = urllib.request.urlopen("http://202.115.47.141/student/courseSelect/selectResult/query", postjson)
                query_result = str(response.read().decode('utf-8'))
                if '成功' in query_result:
                    haha = ''.join([' ha' for ha in range(random.randint(2, 10))])
                    return (True, 'SELECTION SUCCEEDS! ('+ course_code + '_' + course_no + ') '+ haha + '!')
                elif '已经选择' in query_result:
                    return (True, 'This course has already selected.')
                elif '时间冲突' in query_result:
                    return (True, 'Time conflicts with the other course.')
                elif '余量' in query_result or '满' in query_result:
                    return (False, 'This course capacity is full.')
                elif 'esult' in query_result:
                    try:
                        return (False, query_result.split('"', 4)[3].split(':')[1])
                    except:
                        return (False, query_result)
                print('Still don\'t know success or not..')
            except:
                print('Server reset the connection. Likely selection failed.')
        return (False, 'Server is too busy to tell me success or not.')
        
# delete
def applyDeletion(course_code, course_no):
    token = getToken()
    if not token:
        return (False, 'No token.')
    postjson = getEncodedPost({
        'fajhh': '3623',
        'kch': course_code,
        'kxh': course_no,
        'tokenValue': token
    })
    try:
        response = urllib.request.urlopen("http://202.115.47.141/student/courseSelect/delCourse/deleteOne", postjson)
    except urllib.error.URLError:
        return (False, 'Server busy, when posting deleting json.')
        # pass
    else:
        # return result
        delete_result = str(response.read().decode('utf-8'))
        if '成功' in delete_result:
            return (True, 'DELETION SUCCEEDS! ('+ course_code + '_' + course_no + ')')
        elif not delete_result.strip():
            return (True, 'This course has already deleted.')
        else:
            return (False, delete_result)

# over handler
def over(code):
    print('\nTerminated. Press any key to exit..')
    input()
    exit(code)

# give a random UserAgent
def give_me_a_useragent():
    import random
    uas = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0', 
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/62.0', 
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/63.0', 
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/64.0', 
           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
           'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko',
           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0',
           'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; rv:11.0) like Gecko',
           'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
           'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.26 Safari/537.36 Core/1.63.5680.400 QQBrowser/10.2.1852.400',
           'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; Core/1.63.5680.400 QQBrowser/10.2.1852.400; rv:11.0) like Gecko'
    ]
    return random.sample(uas, 1)[0]

# get token
def getToken():
    page_with_token = ""
    try:
        # open delete courses page to find token
        response = urllib.request.urlopen('http://202.115.47.141/student/courseSelect/courseSelect/index')
        page_with_token = response.read().decode('utf-8')
    except urllib.error.HTTPError:
        print('Getting token failed..')
        pass
    except urllib.error.URLError:
        print('Network offline! Connect it quickly!')
        pass
    try:
        # return re.findall(r"(?<=tokenValue':').*(?=')", page_with_token)[0]    # re get token
        token = re.findall(r'(?<=tokenValue\" value=\").*(?="/>)', page_with_token)[0]    # re get token(revised2019.1.8-19:35)
        # print(token)
        return token
    except IndexError:
        print('It\'s not the time..')
        return ""

# func - end
########################################################################

# main process
def process():
    # print courses list
    print('\n===============[Interval: {}s]===============\n'.format(interval) +
    '\n'.join(str(i) for i in courses) + '\n')

    try:
        postjson = getEncodedPost({
            'j_username': username, 
            'j_password': password, 
            'j_captcha1': 'error'
        })
        response = urllib.request.urlopen("http://202.115.47.141/j_spring_security_check", postjson)
        ret_code = response.getcode()
        response.close()
    except urllib.error.URLError:
        input('Logging in failed. Maybe network or wrong password.\n\nPress any key to exit..')
        exit(-2)
    except http.client.RemoteDisconnected:
        input('FATAL: YOU ARE FORBIDDEN TO LOGIN NOW! Check it as soon as possible!\n\nPress any key to exit..')
        exit(-3)

    if str(ret_code) == '200':
        print('Login successfully.')
    else:
        print('Server busy, when logging in.')
        time.sleep(interval)
        process()

    # start
    global exec_time
    if 'exec_time' not in globals():
        exec_time = 1
    while True:
        if len(courses) == 0:
            input('ALL FINISHED!\n\nPress any key to congratulate..')
            exit(0)

        print('\n[Execution Cycle {}]'.format(exec_time))
        for i in courses:
            i_splits = i.split(' ')
            print('Processing item: ' + i)
            # select
            if i_splits[0] == 'a':
                if queryKyl(i_splits[1], i_splits[2]):
                    result, message = applySelection(i_splits[1], i_splits[2])
                    print(message)
                    if result: courses.remove(i)    # remove item if success
                else:
                    print('Full capacity, or wrong course number.')
            # delete
            elif i_splits[0] == 'd':
                result, message = applyDeletion(i_splits[1], i_splits[2])
                print(message)
                if result: courses.remove(i)
            # unknown
            else:
                print('Cannot understand this.')
                courses.remove(i)
                continue
            time.sleep(interval)

        exec_time += 1
        if exec_time % 20 == 0:     # every many times relogin
            break
        time.sleep(interval)

if __name__ == '__main__':
    # get all configurations
    try:
        conf = toml.load('conf.toml')
        global username; username = conf['idnumber']
        password = conf['idpasswd']
        global term; term = conf['xk_term']
        global interval; interval = float(conf['xk_interval'])
        global courses; courses = conf['xk_list']
    except:
        input('\"conf.toml\" file read failed.\n\nPress any key to exit..')
        exit(-1)

    # urllib settings
    header = {
        'Host': '202.115.47.141',
        'User-Agent': give_me_a_useragent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://202.115.47.141/login',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '59',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    cookie_jar = http.cookiejar.CookieJar()
    global html_opener
    html_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    headers_list = []
    for key, value in header.items():
        elem = (key, value)
        headers_list.append(elem)
    html_opener.addheaders = headers_list
    urllib.request.install_opener(html_opener)  # global opener

    global exec_time
    exec_time = 1
    while True:
        process()
        urllib.request.urlopen("http://202.115.47.141/logout") 
        print('\nWait to relogin..')
