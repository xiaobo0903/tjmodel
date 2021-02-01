# -*- coding: utf-8 -*-
'''
把听鉴的ASR数据导入到mongo数据库中，方法是在把语音识别的文件放到data目录中。以txt的后缀结尾；
文件内容的格式是:
[10:00:11.233] 这是一个语音识别内容1
[10:00:11.233] 这是一个语音识别内容2
'''
import os
import hashlib
import pymongo
import time
import datetime

m = hashlib.md5()
root = os.path.dirname(os.path.realpath(__file__))
spath = my_dict = root+'/data/'

conn = pymongo.MongoClient('mongodb://myuser:123456@127.0.0.1:27017/')
db = conn["tingjian"] 
audio_info_collect = db['audio_info'] 
audio_detail_collect = db["audio_detail"]
model_collect = db['model']

#读取当前的数据目录文件
def getPathFile():

    for file in os.listdir(spath):
        file_path = os.path.join(spath, file) 

        if os.path.isdir(file_path):  
            continue

        if str.lower(file_path.split('.')[len(file_path.split('.'))-1]) != "txt":
            continue
        
        print(file_path)
        load_asr(file_path)

#导入ASR识别完成的文件内容；
def load_asr(file):

    fname = os.path.basename(file)
    t = time.time()
    b = (fname + str(t)).encode(encoding='utf-8')
    m.update(b)
    fid = m.hexdigest()
    sinfo = {}
    sinfo["_id"] = fid
    sinfo["oid"] = fname
    sinfo["filename"] = file
    sinfo["date"] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(1582173022))
    audio_info_collect.save(sinfo)
    start = datetime.datetime.now()    
    load_detail(file, fid)
    end = datetime.datetime.now()
    print(str(end-start)+" 秒")
    return fid   

def load_detail(file, fid):

    sid = {}
    sdetail = []
    #读取文件内容；
    fdatas = open(file , 'r', encoding='utf_8').readlines()
    t_b = 0
    for line in fdatas:
        ds = {}
        sd = line.split("] ")
        if len(sd) != 2:
            continue
        st = sd[0].replace("[", "")
        ss = sd[1].strip()
        ds["stime"] = st
        c_t = time_int(st)
        sduration = c_t - t_b
        t_b = c_t
        #如果ss的长度小于4个字，则丢弃
        if len(ss) < 4:
            continue        
        ds["sduration"] = sduration
        ds["sentence"] = ss
        ds["tag"] = ""
        sdetail.append(ds)
    sid["_id"] = fid
    sid["asr"] = sdetail
    audio_detail_collect.save(sid)
    
#根据ID获得audio_detail中的数据记录
def get_detail(did):
    result = audio_detail_collect.find_one({"_id":did})
    return result

def save_detail(result):
    audio_detail_collect.save(result)  

#根据标签取得mclass，和sclass值：
def get_tag_name(label):
    result = model_collect.find_one({"tag":label})
    if result is None:
        return ""
    #return result["mclass"]+"_"+result["sclass"]
    return result["sclass"]
#把[00:00.01]这种格式的字符串，变成整数毫秒；
def time_int(stime):
    s = stime.split(":")
    if len(s) < 2:
        return 0
    return int(int(s[0])*60000 + float(s[1])*1000)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    getPathFile()
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 