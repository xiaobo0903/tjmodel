# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : predict.py
# @Time    : 2021-01-20 09:00

import os
import hashlib
import json
import fasttext
import sys, os
import jieba
import pymongo

RESULT_NUM = 4
RATE=0.45

root = os.path.dirname(os.path.realpath(__file__))
#jieba加载自定义的词典；
my_dict = root+'/dict/mydict.txt'
jieba.load_userdict(my_dict)

my_lable = root+'/dict/mylable.txt'

# 加载模型
model = fasttext.load_model(root+'/model/tingjian.bin')

lable = {}
#从dict目录的mylable.txt中导入用户标签
ldata = open(my_lable , 'r', encoding='utf_8').readlines()
for line in ldata:
    sd = line.rstrip("\n").split("|")
    if len(sd) != 2:
        continue
    lable[sd[1]] = sd[0]

#接收web传入的内容进行预测
def predict(jlist):

    result = []
    for s in jlist:
        #因为传入的字符串格式为[20:11:0000] AABBCCCVVV,需要把时间戳与内容分离出来
        sp = s.split("]")
        if len(sp) != 2:
            continue
        #对于小于7个字的内容进行排除
        if len(sp[1].replace(" ", "")) < 7:
            continue
        sentence = sp[1].replace(".","").replace(",","").replace("?","").replace("。","").replace("，","").replace("？","").replace(" ", "")
        js = jieba.lcut(sentence,cut_all=False)
        nstr = " ".join(js)
        if len(nstr) < 1:
            continue

        res1 = model.predict(nstr, RESULT_NUM)
        slabel = get_label(res1)

        if slabel == "":
            continue

        line = sp[0] +"] "+sp[1]+"|"+slabel
        result.append(line)

    return result

#根据模型预测返回的内容进行处理是否打标签
def get_label(res):

    slabel = []
    for i in range(RESULT_NUM):
        #如果l的匹配值小于0.4，则不进行匹配
        if res[1][i] < RATE:
            continue
        slabel1 = lable[res[0][i]]
        slabel.append(slabel1)
    if len(slabel) > 0:
        return ' '.join(slabel)
    return ""