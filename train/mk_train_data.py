# -*- coding: utf-8 -*-
'''
生成训练的数据，
'''
import os
import hashlib
import pymongo
import time
import datetime
import jieba

m = hashlib.md5()

root = os.path.dirname(os.path.realpath(__file__))
#jieba加载自定义的词典；
my_dict = root+'/dict/mydict.txt'
tpath = root+'/test'
jieba.load_userdict(my_dict)

train_data = root+'/train_data.txt'
tdata = open(train_data , 'w')

conn = pymongo.MongoClient('mongodb://myuser:123456@127.0.0.1:27017/')
db = conn["tingjian"] 
audio_info_collect = db['audio_info'] 
audio_detail_collect = db["audio_detail"]
model_collect = db['model']

model_collect.create_index([('stag', 'text')])

#读取audio_detail的内容，生成train_data的数据内容
def mk_train_data():

    for rec in audio_detail_collect.find():
        asr = rec["asr"]
        nasr = []
        for s in asr:
            sentence = s["sentence"].replace(".","").replace(",","").replace("?","").replace("。","").replace("，","").replace("？","")
            js = jieba.lcut(sentence)
            js1 = jieba.lcut(sentence,cut_all=False)
            njs = ""
            for mjs in js:
                if len(mjs) < 2:
                    continue
                njs = njs + mjs + " "
            tag = {}
            for i in model_collect.find({"$text":{"$search": njs}},{"score":{"$meta":"textScore"}}):
                tag[i["tag"]] = i["score"]
                print(i["score"])
            for key, value in tag.items():

                ts = key+ ", "+" ".join(js1)+"\n"
                train_data1 = root+'/train_data/'+key+'.txt'
                tdata1 = open(train_data1 , 'a+')                
                tdata1.writelines(ts)            
        #rec["asr"] = nasr
        #audio_detail_collect.save(rec)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    mk_train_data()
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 