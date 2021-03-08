from flask import Flask, jsonify, request
import json
import os, sys
# from pathlib import Path
# current_folder = Path(__file__).absolute().parent
# os.chdir(str(current_folder))
# sys.path.append('..')
# import predict.predict as predict
import tj_regextag
import traceback

# 定义一个模版的全局变量，供其它类进行使用；
app = Flask(__name__)

@app.route('/tj_predict/get_tag', methods=['POST'])
# methods里面是POST就是post方式提交数据（浏览器不能显示return回来的数据），是GET就是get方式提交数据，默认是GET方式（浏览器可显示return回来的数据)
# json_data={'id':'111111111122222222223333333','time':'2021-03-01 12:00:12', 'detail': [{'timestamp':"[00:00.000]", "text":"您拜托了这么了。"},{'timestamp':'[00:02.750]', "text":"行了，您来这给你张名片，小王。"....'}]}
# return Error: ("status", "message", "result"), [0, 'error', '无'])
def get_tag():
    if request.method == 'POST':  # 判断是什么方式提交的数据
        data = request.get_json(force=True)  # 获取提交过来得数据，用get_json可忽略以application/json提交的headers
        print(type(data))
        regextag = tj_regextag.TJ_Tag()
        res = {}
        try:
            res = regextag.matchTag(data)
            if res is None:
                res["message"] = "程序处理异常, 未正常获取命中标签"
                res["code"] = 1
        except BaseException as e:
            traceback.print_exc()
            print('regex tag deal error ', e)
            res["code"] = 1
            res["message"] = "程序运行期异常, 请稍后再试"
        return jsonify(res)  # 返回json字串
    # elif request.method == 'GET': get方式


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=5000, debug=False)
