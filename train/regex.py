# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : regex.py
# @Time    : 2021-01-14 14:30

import re
import os
import datetime

root = os.path.dirname(os.path.realpath(__file__))
spath = my_dict = root+'/dict/'
mfile = spath + "/model.txt"

mvec = []

def str_regex(str, reg):
    line = str.replace(",","").replace("，","").replace("。","").replace("?", "").replace("？","").replace("\n", "")
    res = re.findall(reg, line, re.M|re.I)
    print(res)

#导入模型的提取方程
def load_reg_mod():

    fdatas = open(mfile , 'r', encoding='utf_8').readlines()
    for line in fdatas:
        mdict = {}
        sd = line.split("||")
        if len(sd) != 6:
            continue
        mdict["mname"] = sd[0]
        mdict["mclass"] = sd[1] 
        mdict["sname"] = sd[2]
        mdict["sclass"] = sd[3] 
        mdict["tag"] = sd[4]                       
        mdict["regex"] = sd[5].strip("\n")
        mvec.append(mdict)

#一个字符串，通过比对mdict中的正则来判断其所归类的标签
def str_tag_regex(rstr):

    tag = []
    for vec in mvec:
        res = re.findall(vec["regex"], rstr)
        if not res:
            continue
        vec["match"] = res
        tag.append(vec)
    
    ret = ""
    for t in tag:
        mlen = 0
        for m in t["match"]:
            mlen = len(m) + mlen
        ret = ret + t["sname"]+":"+str(mlen)+" "
    return ret

#读取文件内容，打内容标签
def file_tag(file):

    load_reg_mod()
    nfile = file.replace(".txt","_pred.txt")
    f = open(nfile , 'w')
    #把文件的内容加载到mongo库中；
    fdatas = open(file , 'r', encoding='utf_8').readlines()
    for line in fdatas:
        tv = line.split("]")
        tv[0] = tv[0].replace("[", "")
        line1 = tv[1].replace(",","").replace("，","").replace("。","").replace("?", "").replace("？","").replace("\n", "")
        ret = str_tag_regex(line1)        
        if ret is None:
            f.writelines(line)
            continue
        nline = ret +" , "+line
        f.writelines(nline)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    #file_tag("./train/test/benz.txt")
    
    #str_regex("如果你不着急的话，大概得30万，我刚出来", "\d+?")
    nstr = "您好是王女士吧"
    reg = "(您好|你好|先生|女士|叔叔|阿姨|欢迎|光临)(.*)(您好|你好|先生|女士|叔叔|阿姨|欢迎|光临)"
    # reg = "((总共|总计|总价|都办完|优惠完|全下来|优惠下|全齐了|办下来|落地|裸车|落下来|办齐|最低也|开票价|开票金额|大概)(.*)(\d+\d(?!(个|分))))"
    # line = nstr.replace(",","").replace("，","").replace("。","").replace("?", "").replace("？","").replace("\n", "")
    res = re.findall(reg, nstr, re.M|re.I)
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 