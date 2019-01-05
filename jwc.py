# coding: utf-8
# 
# name: scu jwc getter
# author: t
# func: judge whether scu jwc is updated and post news to me.
# created: 2018.7.26
#
# maintain logs:
# 2018.8.28  - add retrying when connection fails
# 2018.8.28  - modify prompt expressions
# 2018.9.12  - re-structure (develop functional modules)
# 2019.1.6   - [Refactor] use toml config
#

# readme
#
# proc: request => updated? => html => parse => diff => out => save
#

from urllib import request
from html.parser import HTMLParser
import re
import os
import toml

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
        retry_choose = input('[PROMPT] retry once? ').lower()
        if retry_choose == 'y':
            # retry
            getResponse(url)
        else:
            exit(1)
    finally:
        return response

response = getResponse('http://jwc.scu.edu.cn/')

# proc.2: updated?
url_info = response.info().as_string()
last_modified_date = re.search('Last-Modified:.*GMT', url_info)     # re filtering date info
last_modified_date = last_modified_date.group(0)
if not is_updated(last_modified_date):
    print('[LOG] modifying date seems unchanged')
    continue_choose = input('[PROMPT] still continue? ').lower()
    if continue_choose != 'y':
        exit(0)

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

# 设计成function是方便后续重试
def showSthNew(old_titles, titles):
    sth_new = False
    for i in range(len(titles)):
        try:
            old_titles.index(titles[i])
            continue
        except ValueError:
            print('[{}]: '.format(i) + titles[i] + '\t' + dates[i])
            print(links[i])
            sth_new = True
    if not sth_new:
        print('[LOG] no latest news!')

    # proc.6: save
    flag = input('[PROMPT] save records? (or number to open link) ').lower()
    if flag == 'y':
        write_date(last_modified_date)
        write_list(titles)
    elif flag == 'n':
        exit(0)
    elif str.isdigit(flag):
        os.system('start ' + links[int(flag)])
        showSthNew(old_titles, titles)
    else:
        print('[ERROR] invalid input')
        showSthNew(old_titles, titles)

showSthNew(old_titles, titles)