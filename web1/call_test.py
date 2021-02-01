# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : predict.py
# @Time    : 2021-01-14 14:30

import time
import datetime
import os
import json
import sys
from pathlib import Path
import requests

current_folder = Path(__file__).absolute().parent
os.chdir(str(current_folder))
v = Path.cwd()
sys.path.append(v)

url = "http://127.0.0.1:5000/tj_predict/get_tag"

root = os.path.dirname(os.path.realpath(__file__))

tpath = root+'/test'

def request_tag(file):

    fdatas = open(file , 'r', encoding='utf_8').readlines()

    drs = {}
    drs["id"] = file
    drs["time"] = str(datetime.datetime.now())
    vrs = []
    for line in fdatas:
        ds = {}
        sd = line.split("] ")
        if len(sd) != 2:
            continue
        st = sd[0].replace("[", "")
        ss = sd[1].replace(".","").replace(",","").replace("?","").replace("。","").replace("，","").replace("？","").replace(" ", "").replace("\n", "")
        
        if len(ss) < 5:
            continue
        ds["timestamp"] = st
        ds["text"] = ss
        vrs.append(ds)
    drs["detail"] = vrs
    data = json.dumps(drs)
    #字符串格式
    res = requests.post(url=url,data=data)
    nfile = file.replace(".txt","_pred.json")
    json.dump(res.json(), open(nfile, "w"),ensure_ascii=False)
    #再写一遍文本文件
    nfile1 = file.replace(".txt","_pred.text")
    jdata = res.json() 
    detail = jdata["detail"]
    f = open(nfile1 , 'w')
    for d in detail:
        nline = "["+d["timestamp"]+"] "+ d["text"]
        if d["mflag"] > 0:
            for match in d["match"]:
                nline = nline +"|"+match["tag"]+"("+",".join(match["regex"])+")"
        f.writelines(nline+"\n")

def filetag():
    
    for file in os.listdir(tpath):
        file_path = os.path.join(tpath, file) 

        if os.path.isdir(file_path):  
            continue

        if str.lower(file_path.split('.')[len(file_path.split('.'))-1]) != "txt":
            continue

        if file_path.find("_pred")>0:
            continue
        
        request_tag(file_path)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    filetag()
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 