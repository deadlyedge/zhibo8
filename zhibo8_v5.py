import datetime
import os
import re

import requests
import wuy
from jinja2 import Environment, FileSystemLoader

root = os.path.dirname(os.path.abspath(__file__))

templates_dir = os.path.join(root, "web/")
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('main_template.html')
filename = os.path.join(templates_dir, 'index.html')


# def handleInput(teamInput):
#     return teamInput


def getHtml(url="https://www.zhibo8.cc/"):  # 设法消除非UTF-8网页编码带来的乱码
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
    now = datetime.datetime.now().strftime('%H:%M')

    # 优化由于睡眠时间产生的歧义
    today = datetime.date.today() - datetime.timedelta(days=1 if '00:00' < now < '05:00' else 0)

    tomorrow = today + datetime.timedelta(days=1)
    theDayAfterTomorrow = today + datetime.timedelta(days=2)
    listDay = sort[0][:10]
    listTime = sort[0][-5:]
    night = True if "00:00" <= listTime <= "05:00" else False

    # 判断时间是否需要替换为汉字 如果是明天凌晨转换为‘今夜’，同理后天凌晨转换为‘明晚’
    if listDay == str(tomorrow) and night:
        sort[0] = "今夜 " + listTime
    elif listDay == str(today):
        sort[0] = "今天 " + listTime
    elif listDay == str(tomorrow):
        sort[0] = "明天 " + listTime
    elif listDay == str(theDayAfterTomorrow) and night:
        sort[0] = "明晚 " + listTime
    else:
        sort[0] = sort[0][5:10] + ' ' + listTime  # 切掉年份
    return sort


def splitTeamInfo(gameInfoList):
    # 将以下字符归类为tags
    nonTeam = ['欧联杯', '足球', '篮球', 'NBA', 'CBA', '英超', '西甲', '荷甲', '待定',
               '中超', '亚冠', '欧冠', '中甲', '足协杯', 'MLB', 'MLB常规赛', '英格兰橄榄球超级联赛']

    # 定义需要消除的tags
    giveup = ['篮球', '足球', 'F1', '其他']

    gameInfo = gameInfoList.split(',')
    teams = [i for i in gameInfo if i not in nonTeam and i not in giveup]
    tags = [i for i in gameInfo if i in nonTeam and i not in giveup]
    return [teams] + [tags]


def showTeam(*args):
    showList = listReady = []  # 预定义变量
    targetRE = '<li label="(.*?)" id="saishi.*?data-time="(.*?)".*?">(.*?)</a>'
    results = re.findall(targetRE, getHtml(), re.S)
    for result in results:
        for team in args:
            if team in result[0] and result not in showList:
                showList.append(reform(result))
    for game in range(len(showList)):  # 整理成分组的list，[第一组时间][第二组比赛信息][第三组转播信息]
        listReady[game] = [showList[game][0].split()] + [splitTeamInfo(showList[game][1])] + \
                          [showList[game][2].split()]
    return listReady


def writeHTML(teamsInput):
    if not teamsInput:
        teamsInput = ['国安', '利物浦', '阿森纳', '热刺', '勇士', 'F1', '皇家马德里']
    with open(filename, 'w', encoding='UTF-8') as fh:
        output = template.render(showListReady=showTeam(*teamsInput))
        fh.write(output)


class index(wuy.Window):  # name the class as the web/<class_name>.html
    size = (750, 700)
    # name = None  # <- a placeholder

    def make(self, name):
        writeHTML(name)
        return name


if __name__ == '__main__':
    # showListReady = showTeam(*handleInput(teamInput=[]))
    index(port=8888)
    # if x.name:
    #     writeHTML(x.name)
    # else:
    #     writeHTML(None)
