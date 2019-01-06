# coding: utf-8
# python 3.7.1
# 
# name: scu jwc rss email
# author: t
# func: judge whether scu jwc is updated and post news to me
#       and send news to self email
# created: 2019.1.6
#
# maintain logs:
# 2019.1.6  - [ Add ] first build 
#

from urllib import request
from html.parser import HTMLParser
import re
import os

import smtplib
import email.mime.text
import email.mime.multipart

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import toml

def send_email(subject, content):
    private_infos = toml.load('conf.toml')
    smtpHost = private_infos['fromStmp'] 
    sendAddr = private_infos['fromEmail']
    password = private_infos['fromPassword']
    receiver = private_infos['toEmail']

    msg = MIMEMultipart()
    msg["from"] = sendAddr
    msg["to"] = receiver
    msg["Subject"] = subject

    txt = MIMEText(content, "plain", "utf-8")
    msg.attach(txt)  # 添加邮件正文

    server = smtplib.SMTP(smtpHost, 25)    # SMTP协议默认端口为25
    # server.set_debuglevel(1)             # 出错时可以查看

    print('正在发送邮件 [' + subject + ']')
    server.login(sendAddr, password)
    server.sendmail(sendAddr, receiver, str(msg))
    server.quit()

def is_updated(date):
    try:
        date_in_file = toml.load('conf.toml')['jwc_modified_date']
        return date_in_file != date
    except:
        write_date(date)
        print('[LOG] created a new date record')
        return True
    finally:
        print('[LOG] reading date record finished')

def write_date(date):
    try:
        dateinfo = '\njwc_modified_date = \'' + date + '\'\n'
        with open('conf.toml', mode='r', encoding='utf-8') as f:
            filecontent = f.readlines()
        for i in filecontent:
            if 'jwc_modified_date' in i:
                i = dateinfo
                break
        else:
            filecontent.append(dateinfo)
        with open('conf.toml', mode='w', encoding='utf-8') as f:
            f.writelines(filecontent)
    except:
        print('[ERROR] outstream error when writing date record')
    finally:
        print('[LOG] writing date record finished')

def read_list():
    try:
        news = toml.load('conf.toml')['jwc_news']
    except:
        news = []
        print('[ERROR] instream error when reading news record')
    finally:
        print('[LOG] reading news records finished')
        return news

def write_list(list):
    try:
        newsinfo = '\n' + toml.dumps({'jwc_news': list})
        with open('conf.toml', mode='r', encoding='utf-8') as f:
            filecontent = f.readlines()
        for i in filecontent:
            if 'jwc_news' in i:
                i = newsinfo
                break
        else:
            filecontent.append(newsinfo)
        with open('conf.toml', mode='w', encoding='utf-8') as f:
            f.writelines(filecontent)
    except:
        print('[ERROR] outstream error when writing news list')
    finally:
        print('[LOG] writing news records finished')

class MyHTMLParser(HTMLParser):
    li_flag = False     # title
    li_data = []
    em_flag = False     # date
    em_data = []
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for (variable, value) in attrs:
                if variable == "href":
                    self.links.append(value)
        if tag == "span":
            self.li_flag = True
        if tag == "em":
            self.em_flag = True
    def handle_endtag(self, tag):
        if tag == "span":
            self.li_flag = False
        if tag == "em":
            self.em_flag = False
    def handle_data(self, data):
        if data == "【置顶】":
            return
        if self.li_flag:
            self.li_data.append(data)
        if self.em_flag:
            self.em_data.append(data)

# start
#
# proc.1: request
def getResponse(url):
    req = request.Request(url)
    try:
        response = request.urlopen(req)
    except:
        print('[ERROR] connecting failed')
    finally:
        return response

response = getResponse('http://jwc.scu.edu.cn/')

# proc.2: updated?
url_info = response.info().as_string()
last_modified_date = re.search('Last-Modified:.*GMT', url_info)     # re filtering date info
last_modified_date = last_modified_date.group(0)
if not is_updated(last_modified_date):
    print('[LOG] modifying date seems unchanged')

# proc.3: html
html_source_code = response.read().decode('utf-8')

# proc.4: parse
parsed_html = re.search('<ul class="list-llb-s">.*</ul></div>', html_source_code, re.S).group(0)    #re.S解决了.无法跨行的问题
                       
hp = MyHTMLParser()
hp.feed(parsed_html)
hp.close()

titles = hp.li_data
dates = hp.em_data
links = hp.links

# proc.5: diff and out
old_titles = read_list()

def sendnews(old_titles, titles):
    sth_new = False

    sendtitles = []
    sendlinks = []

    for i in range(len(titles)):
        try:
            old_titles.index(titles[i])
            continue
        except ValueError:
            sendtitles.append('[{}]: '.format(i) + titles[i] + '\t' + dates[i])
            sendlinks.append(links[i])
            sth_new = True
    if not sth_new:
        print('[LOG] no latest news!')
    else:
        content = ""
        for i in range(len(sendtitles)):
            content += '[{}] '.format(i) + sendtitles[i] + '\n' + sendlinks[i] + '\n\n'
        send_email('来自服务器：jwc有' + str(len(sendtitles)) + '条新公告', content)

    # proc.6: save
    write_date(last_modified_date)
    write_list(titles)

sendnews(old_titles, titles)