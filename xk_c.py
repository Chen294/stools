import requests 
from PIL import Image
import io
import json
import time
#XK函数
#选中一门课后需要在course中移除
def XK():
    print("hahaha")
#全局变量
id="2017141461215"
pwd="XXXXXX"
course=[{"zxjxjhh":"2018-2019-2-1","skxq":"4","skjc":"1","kch":"105396020","skjs":"王雁鸿"},
{"zxjxjhh":"2018-2019-2-1","skxq":"4","kch":"304053020"},
{"zxjxjhh":"2018-2019-2-1","skxq":"5","kch":"999005030"}]
#初始化
session=requests.Session()
response=session.get("http://zhjw.scu.edu.cn/img/captcha.jpg")
image = Image.open(io.BytesIO(response.content))
image.show()
yzm=input("请输入验证码：")
data={"j_username":id,"j_password":pwd,"j_captcha":yzm}
headers={"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6)Gecko/20091201 Firefox/3.5.6"}
response=session.post("http://zhjw.scu.edu.cn/j_spring_security_check",data=data,headers=headers)
#选课
while(len(course)>0):
    for i in range(0,len(course)):
        response=session.post("http://zhjw.scu.edu.cn/student/integratedQuery/course/courseSchdule/courseInfo",data=course[i],headers=headers)
        xc_json=json.loads(response.text)
        print(xc_json["list"]["records"][0]["bkskyl"])
        if(xc_json["list"]["records"][0]["bkskyl"]>0):
            XK()
        time.sleep(5)   #初步估计查询限制5s/次