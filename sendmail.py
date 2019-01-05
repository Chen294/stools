import smtplib
import email.mime.text
import email.mime.multipart

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import time
import sys

import tempfile
import toml

def get_type_file(keyword="."):  # 这里可以更改扩展名如.doc, .py, .zip等等
    # 打印当前的工作目录
    print("当前目录为: ", os.getcwd())

    # 列举当前工作目录下的文件名
    files = os.listdir()
    keyword = keyword
    filelist = []

    i = 0
    for file in files:
        if keyword in file and '7z' not in file and 'sendmail' not in file:
            i = i + 1
            # print(i, file)
            filelist.append(file)
    return filelist


def send_email(filelist, content=""):
    private_infos = toml.load('conf.toml')
    smtpHost = private_infos['fromStmp'] 
    sendAddr = private_infos['fromEmail']
    password = private_infos['fromPassword']
    receiver = private_infos['toEmail']
    if len(filelist) > 1:
        subject = '来自电脑：' + os.path.split(filelist[0])[1] + '等' + str(len(filelist)) + '个文件'
    else:
        subject = '来自电脑：' + os.path.split(filelist[0])[1] + '文件'
    content = '发送时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n' + '文件列表：' + str(filelist)

    msg = MIMEMultipart()
    msg["from"] = sendAddr
    msg["to"] = receiver
    msg["Subject"] = subject

    txt = MIMEText(content, "plain", "utf-8")
    msg.attach(txt)  # 添加邮件正文

    # 添加附件, 传送filelist列表里的文件
    filename = ""
    i = 0
    for file in filelist:
        i = i + 1
        filename = file
        print(str(i), filename)
        part = MIMEApplication(open(filename, "rb").read())
        part.add_header("Content-Disposition", "attachment", filename=('gbk', '', os.path.split(filename)[1]))
        msg.attach(part)

    server = smtplib.SMTP(smtpHost, 25)    # SMTP协议默认端口为25
    # server.set_debuglevel(1)             # 出错时可以查看

    print('正在发送[' + subject + ']')
    server.login(sendAddr, password)
    server.sendmail(sendAddr, receiver, str(msg))
    print("\n" + str(len(filelist)) + "个文件发送成功")
    server.quit()


def getCompressedFile(filelist):
    files = ''
    for file in filelist:
        files += '\"' + file + '\" '
    compressedFile = 't.' + os.path.split(filelist[0])[1] + '.7z'
    path7z = toml.load('conf.toml')['path7z']
    print('cmd /c \"' + path7z + '\" a \"' + compressedFile + '\" ' + files + ' -x!*7z* -x!sendmail*')
    os.system('cmd /c \"' + path7z + '\" a \"' + compressedFile + '\" ' + files + ' -x!*7z* -x!sendmail*')
    return compressedFile


def hasDirectory(filelist):
    for file in filelist:
        if os.path.isdir(file):
            return True
    return False

def main():
    if len(sys.argv) <= 1:
        # 发送当前目录下的文件
        filelist = get_type_file()
    else:
        # 有命令行参数
        filelist = sys.argv[1:]

    # 存在目录或者文件数大于2，就压缩
    isCompressed = False
    # if len(filelist) > 2 or hasDirectory(filelist):
    #     isCompressed = True
    #     filelist = [getCompressedFile(filelist)]

    send_email(filelist)
    if isCompressed:
        os.remove(filelist[0])
        print(filelist[0] + ' 临时压缩文件已删除')



main()
