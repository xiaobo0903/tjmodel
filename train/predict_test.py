# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : predict.py
# @Time    : 2021-01-14 14:30

import fasttext
import sys, os
import jieba
import pymongo
import datetime
from loadASR import *
from pathlib import Path
current_folder = Path(__file__).absolute().parent
os.chdir(str(current_folder))
v = Path.cwd()
sys.path.append(v)

RESULT_NUM = 4
RATE=0.45

root = os.path.dirname(os.path.realpath(__file__))
#jieba加载自定义的词典；
my_dict = root+'/dict/mydict.txt'
tpath = root+'/test'
jieba.load_userdict(my_dict)

# 加载模型
model = fasttext.load_model(root+'/model/tingjian.bin')

conn = pymongo.MongoClient('mongodb://myuser:123456@127.0.0.1:27017/')
db = conn["tingjian"] 
model_collect = db['model']

def predict_tag(file):

    nfile = file.replace(".txt","_pred.txt")
    f = open(nfile , 'w')
    #把文件的内容加载到mongo库中；
    fid = load_asr(file)
    #从mongo库中读取内容，并逐条进行预测
    result = get_detail(fid)
    if result is None:
        return "Data is Error!"
    asr = result["asr"]
    for s in asr:
        #对于小于7个字的内容进行排除    
        sentence = s["sentence"].replace(".","").replace(",","").replace("?","").replace("。","").replace("，","").replace("？","").replace(" ", "")
        if len(sentence) < 10:
            continue 
        js = jieba.lcut(sentence,cut_all=True)
        nstr = " ".join(js)
        if len(nstr) < 1:
            continue
        res1 = model.predict(nstr, RESULT_NUM)
        slabel = get_label(res1)

        if slabel == "":
            continue

        line = s["stime"] +"|"+str(s["sduration"])+"|"+s["sentence"]+"|"+slabel+"\n"
        f.writelines(line)

#根据模型预测返回的内容进行处理是否打标签
def get_label(res):

    slabel = []
    for i in range(len(res[1])):
        #如果l的匹配值小于0.4，则不进行匹配
        if res[1][i] < RATE:
            continue
        slabel1 = get_tag_name(res[0][i])
        slabel.append(slabel1)
    if len(slabel) > 0:
        return ' '.join(slabel)
    return ""

def predict():
    
    for file in os.listdir(tpath):
        file_path = os.path.join(tpath, file) 

        if os.path.isdir(file_path):  
            continue

        if str.lower(file_path.split('.')[len(file_path.split('.'))-1]) != "txt":
            continue

        if file_path.find("_pred")>0:
            continue
        
        predict_tag(file_path)

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    predict()
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 