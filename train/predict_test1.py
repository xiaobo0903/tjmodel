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
from pathlib import Path
from cal_distance import *
current_folder = Path(__file__).absolute().parent
os.chdir(str(current_folder))
v = Path.cwd()
sys.path.append(v)

RESULT_NUM = 4
SLEN = 5

root = os.path.dirname(os.path.realpath(__file__))

tpath = root+'/test'

def predict_tag(file):

    nfile = file.replace(".txt","_pred.txt")
    f = open(nfile , 'w')
    
    fdatas = open(file , 'r', encoding='utf_8').readlines()

    for line in fdatas:
        ds = {}
        sd = line.split("] ")
        if len(sd) != 2:
            continue
        st = sd[0].replace("[", "")
        ss = sd[1].replace(".","").replace(",","").replace("?","").replace("。","").replace("，","").replace("？","").replace(" ", "").replace("\n", "")
        
        if len(ss) < SLEN:
            continue
        
        catalog = get_catalog(ss)

        if len(catalog) == 0:
            continue

        line = "[" +st+"]|"+sd[1].strip("\n")+"|"+" ".join(catalog)+"\n"
        f.writelines(line)

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