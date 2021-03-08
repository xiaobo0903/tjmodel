# -*- coding: utf-8 -*-
# @Author  : xiaobo
# @Email   : xiaobo@cdvcloud.com
# @File    : tj_regextag.py
# @Time    : 2021-01-29 09:30
# 对于输入的识别内容进行标签的识别，输入的内容为json格式：
# json_data={'id':'111111111122222222223333333','time':'2021-03-01 12:00:12', 'detail': [{'timestamp':"[00:00.000]", "text":"您拜托了这么了。"},{'timestamp':'[00:02.750]', "text":"行了，您来这给你张名片，小王。"....'}]}
# 输入一个ID号和时间点；所有识别的内容都放入到detail中；
# detail 的格式为：timestamp:时间戳 + text:文本内容 


import datetime
import os
import re

# 设置mvec全局变量，把全部的正则匹配模型都装进数组中，这样可以加快处理的速度，如果需要更新内容，则需要重新加载
mvec = []
root = os.path.dirname(os.path.realpath(__file__))
spath = my_dict = root + '/model/'
mfile = spath + "/model.txt"


class TJ_Tag:
    rdict = {}
    def __init__(self):
        if not mvec:
            self.load_reg_mod()

    def str_regex(self, str, reg):
        line = str.replace(",","").replace("，","").replace("。","").replace("?", "").replace("？","").replace("\n", "")
        res = re.findall(reg, line, re.M|re.I)
        print(res)

    #导入模型的提取方程
    def load_reg_mod(self):

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
    def str_tag_regex(self, rstr):

        tag = []
        rstr1 = rstr.replace(",","").replace("，","").replace("。","").replace("?", "").replace("？","").replace("\n", "")
        for vec in mvec:
            vdict = {}
            res = re.findall(vec["regex"], rstr1)
            if not res:
                continue

            list1 = []
            for r in res:
                lres = [r1 for r1 in r if r1 != '']
                list1.append("".join(lres))

            vdict["sname"] = vec["sname"]
            vdict["match"] = ",".join(list1)
            tag.append(vdict)

        return tag

    #根据传入的json内容进行匹配标签处理
    def matchTag(self, jdata):

        start = datetime.datetime.now()
        request_debug = False
        if "debug" in jdata:
            request_debug = jdata["debug"]  # type: bool

        detail_v = jdata["detail"]
        rdetail_v = []
        for r in detail_v:
            rdict = {}
            rdict["bg"] = r["bg"]
            rdict["onebest"] = r["onebest"]
            tag = self.str_tag_regex(r["onebest"])
            if not tag:
                if request_debug:
                    rdict["mflag"] = False
                    rdetail_v.append(rdict)
                continue
            rdict["mflag"] = True
            rv = []
            # tag可是一个数组类型，其可能会匹配多个标签，而每个标签又会有多个内容符合匹配要求(findall)，所以返回的内容需要整理成一个dict类型：
            # [{"tag":"首次到店", "regex":[{"aaa","bbbb,bbb,bbb","cccc"}]},{"tag":"首次到店", "regex":[{"aaa","bbbb,bbb,bbb","cccc"}]}...]
            for t in tag:
                tdict = {"tag": t["sname"], "regex": t["match"]}
                rv.append(tdict)
            rdict["match"] = rv
            rdetail_v.append(rdict)
        jdict = {"id": jdata["id"], "detail": rdetail_v, "code": 0}
        if request_debug:
            jdict["begin-time"] = str(start)
            end = datetime.datetime.now()
            jdict["end-time"] = str(end)
            utime = str(end - start) + "秒"
            jdict["use-time"] = utime
        return jdict

    # 读取文件内容，打内容标签
    def file_tag(self, file):

        self.load_reg_mod()
        nfile = file.replace(".txt", "_pred.txt")
        f = open(nfile, 'w')
        # 把文件的内容加载到mongo库中；
        fdatas = open(file, 'r', encoding='utf_8').readlines()
        for line in fdatas:
            tv = line.split("]")
            tv[0] = tv[0].replace("[", "")
            line1 = tv[1].replace(",", "").replace("，", "").replace("。", "").replace("?", "").replace("？", "").replace(
                "\n", "")
            ret = self.str_tag_regex(line1)
            if ret is None:
                f.writelines(line)
                continue
            nline = ret + " , " + line
            f.writelines(nline)


if __name__ == '__main__':
    start = datetime.datetime.now()
    mvec = []
    jsontext = "{\"id\":\"111111111122222222223333333\",\"debug\":false,\"detail\":[{\"bg\":1990,\"onebest\":\"行没问题，就如果说您订不了的话，后期我再联系，你，有活动的话我再通知您\"},{\"bg\":6640,\"onebest\":\"然后您也可以关注咱们魔比商城，要是价格有变动的话，呢您在家里拿手机一看就一目了然了\"}]}"

    tj_tag = TJ_Tag()
    tj_tag.matchTag(jsontext)
    # file_tag("./train/test/benz.txt")

    end = datetime.datetime.now()
    print(str(end - start) + " 秒")
