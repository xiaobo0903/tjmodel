# -*- coding: utf-8 -*-
'''
把评分模型的数据，装入到mongo中 collection = model；
'''
import pymongo
import datetime
import time
import os
import hashlib

root = os.path.dirname(os.path.realpath(__file__))
spath = my_dict = root+'/dict/'
file = spath + "/model.txt"
conn = pymongo.MongoClient('mongodb://myuser:123456@192.168.0.244:27017/')
db = conn["tingjian"] 
model_collect = db['model']

m = hashlib.md5()
#model = {mclass: main, sclass: subclass, tag:"tag1 tag2..."}
def load_data():

    ds = {}
    #读取文件内容；
    fdatas = open(file , 'r', encoding='utf_8').readlines()
    for line in fdatas:
        t = time.time()
        m.update(str(t).encode(encoding='utf-8'))
        id = m.hexdigest()
        sd = line.split("||")
        if len(sd) != 6:
            continue
        ds["_id"] = id
        ds["mclass"] = sd[0]
        ds["mname"] = sd[1]        
        ds["sclass"] = sd[2]
        ds["sname"] = sd[3]
        ds["tag"] = sd[4]                 
        ds["stag"] = sd[5].strip("\n")
        model_collect.insert(ds)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    load_data()
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 