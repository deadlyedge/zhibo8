import eel
import os
import re
import requests
import datetime

from jinja2 import Environment, FileSystemLoader

root = os.path.dirname(os.path.abspath(__file__))

templates_dir = os.path.join(root, "web/")
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('main_template.html')
eel.init(templates_dir)


def getHtml(url="https://www.zhibo8.cc/"):
    req = requests.get(url)

    if req.encoding == 'ISO-8859-1':
        encodings = requests.utils.get_encodings_from_content(req.text)
        if encodings:
            encoding = encodings[0]
        else:
            encoding = req.apparent_encoding

        encode_content = req.content.decode(encoding, 'replace')  # 如果设置为replace，则会用?取代非法字符；
        return encode_content
    else:
        return req.text


def reform(result):  # 整理比赛数据格式
    sort = [result[1], result[0], result[2]]
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    theDayAfterTomorrow = today + datetime.timedelta(days=2)
    listDay = sort[0][:10]
    listTime = sort[0][-5:]
    night = True if "00:00" <= listTime <= "05:00" else False
    if listDay == str(today):  # 判断时间是否需要替换为汉字
        sort[0] = "今天 " + listTime
    elif listDay == str(tomorrow) and night:  # 判断时间是否需要替换为汉字
        sort[0] = "今夜 " + listTime
    elif listDay == str(tomorrow):
        sort[0] = "明天 " + listTime
    elif listDay == str(theDayAfterTomorrow) and night:
        sort[0] = "明晚 " + listTime
    return sort


def splitTeamInfo(gameInfoList):
    nonTeam = ['欧联杯', '足球', '篮球', 'NBA', 'CBA', '英超', '西甲', '荷甲', '待定',
               '中超', '亚冠', '欧冠', '中甲', '足协杯', 'MLB', 'MLB常规赛', '英格兰橄榄球超级联赛']
    giveup = ['篮球', '足球', 'F1', '其他']
    gameInfo = gameInfoList.split(',')
    temp1 = [i for i in gameInfo if i not in nonTeam and i not in giveup]
    temp2 = [i for i in gameInfo if i in nonTeam and i not in giveup]
    gameInfoListSorted = [temp1] + [temp2]
    return gameInfoListSorted


def showTeam(*args):
    showList = listReady = []  # 预定义变量
    targetRE = '<li label="(.*?)" id="saishi.*?data-time="(.*?)".*?">(.*?)</a>'
    results = re.findall(targetRE, getHtml(), re.S)

    for result in results:
        resultReform = reform(result)
        for team in args:
            if team in resultReform[1] and resultReform not in showList:
                showList.append(resultReform)
    for game in range(len(showList)):  # 整理成分组的list，[第一组时间][第二组比赛信息][第三组转播信息]
        listReady[game] = [showList[game][0].split()] + [splitTeamInfo(showList[game][1])] + \
                          [showList[game][2].split()]
    return listReady


if __name__ == '__main__':
    showListReady = showTeam('国安', '利物浦', '阿森纳', '热刺', '勇士', 'F1', '皇家马德里')
    filename = os.path.join(templates_dir, 'index.html')
    with open(filename, 'w', encoding='UTF-8') as fh:
        output = template.render(showListReady=showListReady)
        fh.write(output)

    eel.start('index.html', size=(736, 730))
