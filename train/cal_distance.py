# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : predict.py
# @Time    : 2021-01-22 09:11
import re
import os
import jieba
import datetime
import math

#设定匹配通过率
RATE = 0.51
#jieba加载自定义的词典；
root = os.path.dirname(os.path.realpath(__file__))
my_dict = root+'/dict/mydict.txt'
template = root+'/dict/template.txt'

#模版列表的dict
ltemplate = []
fdatas = open(template , 'r', encoding='utf_8').readlines()
for line in fdatas:
    sdict = {}
    sline = line.split("|")
    sdict["sname"] = sline[0]
    sdict["stag"] = sline[1]
    sdict["sentence"] = sline[2]
    #把分词后的内容也存入到dict中；
    sn = jieba.lcut(sline[2],cut_all=False)
    sdict["sn"] = sn
    ltemplate.append(sdict)

def get_catalog(sentence):

    #首先需要对于sentence内容做切割
    asentence = re.split("。|，|？|\.|\?|,", sentence)
    max = 0
    catalog = []
    for s in asentence:
        for t1 in ltemplate:
            sn = t1["sn"]
            diff = count_distance(s, sn)
            if diff > max:
                max = diff

            if diff > RATE:
                catalog.append(t1["sname"])
    
    print(max)
    print(catalog)
    return catalog

#sentence 是长句，bsa是例句； sentence需要分割为短句；计算两个句子之间的距离；
def count_distance(sentence, bsa):

    bsp = jieba.lcut(sentence,cut_all=False)
    mwords = set(bsp).union(set(bsa))
    word_dict = dict()
    i = 0
    for word in mwords:
        word_dict[word] = i
        i += 1        
    s1_cut_code = [word_dict[word] for word in bsp]
    #print(s1_cut_code)
    s1_cut_code = [0]*len(word_dict)

    for word in bsp:
        s1_cut_code[word_dict[word]]+=1
    #print(s1_cut_code)

    s2_cut_code = [word_dict[word] for word in bsa]
    #print(s2_cut_code)
    s2_cut_code = [0]*len(word_dict)
    for word in bsa:
        s2_cut_code[word_dict[word]]+=1
    #print(s2_cut_code)
    result = compute_cos(s1_cut_code, s2_cut_code)
    #print(result)
    return result

#子句与标准化的语句合成一个全词组的内容；
def merge_word(bsp, bsa):

    words = []
    for ch in bsa:
        words.append(ch)
    for ch1 in bsp:
        if ch1 in words:
            continue
        words.append(ch1)
    
    return words

def compute_cos(v1, v2):
    sum = 0
    sq1 = 0
    sq2 = 0
    for i in range(len(v1)):
        sum += v1[i] * v2[i]
        sq1 += pow(v1[i], 2)
        sq2 += pow(v2[i], 2)
 
    try:
        result = round(float(sum) / (math.sqrt(sq1) * math.sqrt(sq2)), 2)
    except ZeroDivisionError:
        result = 0.0
    return result

if __name__ == '__main__':
    
    start = datetime.datetime.now()    
    get_catalog("在驾驶模式只有在停车的时候才能不是驾驶当中可以选，越野模式超过一定时速就看不见了")
    end = datetime.datetime.now()
    print(str(end-start)+" 秒") 
