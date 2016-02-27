import os
import csv
import time
from operator import itemgetter
from bs4 import BeautifulSoup
import requests
import datetime as dt


def get_tse_data(date_str):
    f = dict()
    payload = {
            'download': '',
            'qdate': date_str,
            'selectType': 'ALLBUT0999'
        }
    url = 'http://www.twse.com.tw/ch/trading/exchange/MI_INDEX/MI_INDEX.php'
    page = requests.post(url, data=payload)

    soup = BeautifulSoup(page.text.encode('utf-8'), "html.parser")

    if len(soup.select('h1')) == 2:
        return None
    else:
        for table in soup.select('table')[1:2]:
            for tb in table.select('tbody'):
                for tr in tb.select('tr')[44:]:
                    f[tr.select('td')[0].text.strip()] = [tr.select('td')[5].text]
                    f[tr.select('td')[0].text.strip()].append(tr.select('td')[6].text)
                    f[tr.select('td')[0].text.strip()].append(tr.select('td')[7].text)
        return f

def get_otc_data(date_str):
    f=dict()
    url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}'.format(date_str)
    page = requests.get(url)
    soup = page.json()

    if soup['reportDate'] != date_str or soup['iTotalRecords'] == 0:
        return None
    else:
        for table in soup['aaData'][1:]:
            del table[1:2]
            f[table[0]] = [table[3]]
            f[table[0]].append(table[4])
            f[table[0]].append(table[5])
        return f


原始盤中 = []
排序後盤中 = []
盤中結果 = []
原始開午 = []
排序後開午 = []
開午結果 = []
全部盤中 = []
全部開午 = []
原始隔日沖 = []
排序後隔日沖 = []
隔日沖結果 = []
全部隔日沖 = []
原始波段 = []
排序後波段 = []
波段結果 = []
全部波段 = []
temp = ''


in_csv = input("請輸入要分析的CSV檔資料夾: ")
in_csv = in_csv.strip('"')


for root, dirs, files in os.walk(in_csv):
    # print(root)
    for ff in files:
        temp = os.path.join(root, ff)
        print(os.path.join(root, ff))

        # 撈資料
        nowY = int(temp[len(temp) - 12:len(temp) - 8])
        nowM = int(temp[len(temp) - 8:len(temp) - 6])
        nowD = int(temp[len(temp) - 6:len(temp) - 4])
        searchdate = dt.datetime(nowY, nowM, nowD)

        stock_info = dict()
        searchdate = searchdate + dt.timedelta(days = 1)
        date_str = str(searchdate.year-1911) + '/'+str(searchdate.month).zfill(2)+ '/' + str(searchdate.day).zfill(2)
        stock_info = get_tse_data(date_str)
        while stock_info == None:
            searchdate = searchdate + dt.timedelta(days = 1)
            date_str = str(searchdate.year-1911) + '/'+str(searchdate.month).zfill(2)+ '/' + str(searchdate.day).zfill(2)
            stock_info = get_tse_data(date_str)
        stock_info.update(get_otc_data(date_str))

        f = open(os.path.join(root, ff), 'r')
        f_reader = csv.reader(f)
        header = next(f_reader)
        for row in f_reader:
            del(row[1])
            del(row[2])
            del(row[4])
            del(row[4])
            row[3] = time.strptime(row[3], "%H:%M:%S")
            row[4] = row[4][0:len(row[4]) - 1]
            if row[5][2] == "波":
                原始波段.append(row)
            elif row[5][4] == "開":
                原始開午.append(row)
            elif row[5][4] == "午":
                原始開午.append(row)
                ll = row[:]
                原始隔日沖.append(ll)
            else:
                原始盤中.append(row)

        排序後盤中 = sorted(原始盤中, key=itemgetter(1, 3))
        排序後開午 = sorted(原始開午, key=itemgetter(1, 3))
        排序後隔日沖 = sorted(原始隔日沖, key=itemgetter(1, 3))
        排序後波段 = sorted(原始波段, key=itemgetter(1, 3))

        # 盤中
        count = 0
        flag = 0
        x = 0
        while count < len(排序後盤中):
            # 第一筆資料
            if count == 0:
                tmp = 排序後盤中[count]
                flag = 0
            # 最後一筆資料
            elif count == len(排序後盤中) - 1:
                if 排序後盤中[count][1] == tmp[1]:
                    x = abs(round(float(排序後盤中[count][4]) - float(tmp[4]), 2))
                    tmp.append(x)
                    盤中結果.append(tmp)
                else:
                    tmp.append("X")
                    盤中結果.append(tmp)
                    tmp = 排序後盤中[count]
                    tmp.append("X")
                    盤中結果.append(tmp)
            # 商品名稱改變
            elif 排序後盤中[count][1] != tmp[1]:
                if flag == 1:
                    x = abs(
                        round(float(排序後盤中[count - 1][4]) - float(tmp[4]), 2))
                    tmp.append(x)
                    盤中結果.append(tmp)
                else:
                    tmp.append("X")
                    盤中結果.append(tmp)
                tmp = 排序後盤中[count]
                flag = 0
            # 商品名稱不變
            elif 排序後盤中[count][1] == tmp[1]:
                flag = 1
            count += 1

        # 開盤午後
        count = 0
        flag = 0
        x = 0
        while count < len(排序後開午):
            # 第一筆資料
            if count == 0:
                tmp = 排序後開午[count]
                flag = 0
            # 最後一筆資料
            elif count == len(排序後開午) - 1:
                if 排序後開午[count][1] == tmp[1]:
                    x = abs(round(float(排序後開午[count][4]) - float(tmp[4]), 2))
                    tmp.append(x)
                    開午結果.append(tmp)
                else:
                    tmp.append("X")
                    開午結果.append(tmp)
                    tmp = 排序後開午[count]
                    tmp.append("X")
                    開午結果.append(tmp)
            # 商品名稱改變
            elif 排序後開午[count][1] != tmp[1]:
                if flag == 1:
                    x = abs(
                        round(float(排序後開午[count - 1][4]) - float(tmp[4]), 2))
                    tmp.append(x)
                    開午結果.append(tmp)
                else:
                    tmp.append("X")
                    開午結果.append(tmp)
                tmp = 排序後開午[count]
                flag = 0
            # 商品名稱不變
            elif 排序後開午[count][1] == tmp[1]:
                flag = 1
            count += 1

        # 隔日沖
        count = 0
        flag = 0
        x = 0
        stock = None
        while count < len(排序後隔日沖):
            # 第一筆資料
            if count == 0:
                tmp = 排序後隔日沖[count]
                stockID = tmp[1][len(tmp[1])-5:len(tmp[1])-1]
                getin = float(tmp[2])
                nextdayopen = float(stock_info[stockID][0])
                nextdayhighest = float(stock_info[stockID][1])
                nextdaylowest = float(stock_info[stockID][2])
                # 作多
                if '-' not in tmp[4]:
                    x1 = nextdayopen - getin
                    x2 = nextdayhighest - getin
                # 作空
                else:
                    x1 = getin - nextdayopen
                    x2 = getin - nextdaylowest
                y1 = round(x1*100 / getin , 1)
                y2 = round(x2*100 / getin , 1)

                tmp.append(nextdayopen)
                tmp.append(nextdayhighest)
                tmp.append(nextdaylowest)
                tmp.append(x1)
                tmp.append(x2)
                tmp.append(str(y1)+'%')
                tmp.append(str(y2)+'%')
                隔日沖結果.append(tmp)
            # 商品名稱改變
            elif 排序後隔日沖[count][1] != tmp[1]:
                tmp = 排序後隔日沖[count]
                stockID = tmp[1][len(tmp[1])-5:len(tmp[1])-1]
                getin = float(tmp[2])
                nextdayopen = float(stock_info[stockID][0])
                nextdayhighest = float(stock_info[stockID][1])
                nextdaylowest = float(stock_info[stockID][2])
                # 作多
                if '-' not in tmp[4]:
                    x1 = nextdayopen - getin
                    x2 = nextdayhighest - getin
                # 作空
                else:
                    x1 = getin - nextdayopen
                    x2 = getin - nextdaylowest
                y1 = round(x1*100 / getin , 1)
                y2 = round(x2*100 / getin , 1)

                tmp.append(nextdayopen)
                tmp.append(nextdayhighest)
                tmp.append(nextdaylowest)
                tmp.append(x1)
                tmp.append(x2)
                tmp.append(str(y1)+'%')
                tmp.append(str(y2)+'%')
                隔日沖結果.append(tmp)
            count += 1


        #波段
        count = 0
        flag = 0
        x = 0
        while count < len(排序後波段):
            # 第一筆資料
            if count == 0:
                tmp = 排序後波段[count]
                波段結果.append(tmp)
                flag = 0
            # 最後一筆資料
            elif count == len(排序後波段) - 1:
                if 排序後波段[count][1] == tmp[1]:
                    tmp = 排序後波段[count]
                    波段結果.append(tmp)
                else:
                    波段結果.append(tmp)
                    tmp = 排序後波段[count]
                    波段結果.append(tmp)
            # 商品名稱改變
            elif 排序後波段[count][1] != tmp[1]:
                if flag == 1:
                    波段結果.append(tmp)
                tmp = 排序後波段[count]
                波段結果.append(tmp)
                flag = 0
            # 商品名稱不變
            elif 排序後波段[count][1] == tmp[1]:
                tmp = 排序後波段[count]
                flag = 1
            count += 1


        for i in 盤中結果:
            i[3] = time.strftime("%H:%M:%S", i[3])
            i[4] = i[4] + "%"
            i[6] = str(i[6]) + "%"
            i.append(temp[len(temp) - 12:len(temp) - 4])
            全部盤中.append(i)

        for i in 開午結果:
            i[3] = time.strftime("%H:%M:%S", i[3])
            i[4] = i[4] + "%"
            i[6] = str(i[6]) + "%"
            i.append(temp[len(temp) - 12:len(temp) - 4])
            全部開午.append(i)

        for i in 隔日沖結果:
            i[3] = time.strftime("%H:%M:%S", i[3])
            i[4] = i[4] + "%"
            i.append(temp[len(temp) - 12:len(temp) - 4])
            全部隔日沖.append(i)

        for i in 波段結果:
            i[3] = time.strftime("%H:%M:%S", i[3])
            i[4] = i[4] + "%"
            i.append(temp[len(temp) - 12:len(temp) - 4])
            全部波段.append(i)

        原始盤中 = []
        排序後盤中 = []
        盤中結果 = []
        原始開午 = []
        排序後開午 = []
        開午結果 = []
        原始隔日沖 = []
        排序後隔日沖 = []
        隔日沖結果 = []
        原始波段 = []
        排序後波段 = []
        波段結果 = []
        f.close()


out_csv1 = in_csv + "\盤中獲利分析.csv"
out_csv2 = in_csv + "\開盤午後獲利分析.csv"
out_csv3 = in_csv + "\隔日沖獲利分析.csv"
out_csv4 = in_csv + "\波段沖股票總合.csv"
f1 = open(out_csv1, 'w', newline='')
f2 = open(out_csv2, 'w', newline='')
f3 = open(out_csv3, 'w', newline='')
f4 = open(out_csv4, 'w', newline='')
盤中_writer = csv.writer(f1)
開午_writer = csv.writer(f2)
隔日沖_writer = csv.writer(f3)
波段_writer = csv.writer(f4)
盤中_writer.writerow(["腳本名稱", "商品", "成交", "時間", "漲幅", "訊息", "獲利", "日期"])
開午_writer.writerow(["腳本名稱", "商品", "成交", "時間", "漲幅", "訊息", "獲利", "日期"])
隔日沖_writer.writerow(["腳本名稱", "商品", "成交", "時間", "漲幅", "訊息", "隔日開盤價", "隔日最高價", "隔日最低價", "價差1", "價差2", '獲利1', "獲利2", "日期"])
波段_writer.writerow(["腳本名稱", "商品", "成交", "時間", "漲幅", "訊息", "日期"])
for i in 全部盤中:
    盤中_writer.writerow(i)

for i in 全部開午:
    開午_writer.writerow(i)

for i in 全部隔日沖:
    隔日沖_writer.writerow(i)

for i in 全部波段:
    波段_writer.writerow(i)
f1.close()
f2.close()
f3.close()
f4.close()
input("程式執行完成，按一下Enter鍵結束程式")
