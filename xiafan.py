from DrissionPage import Chromium
from DrissionPage import ChromiumPage
from datetime import datetime
import csv
import time
import os
import pandas as pd

# 收集所有数据，最后统一写入
all_data = []

dy = Chromium().latest_tab
dy.listen.start("/comment/list")
dy.get('https://www.douyin.com/user/self?from_tab_name=main&modal_id=7574396223752520866&showTab=like')
#要换的链接
#初始化浏览器并监听

try:
    for page in range(1,4):
        #如果要增加就修改成(1,你要的数值)
        #目前抖音是1:10的数据量
        data=dy.listen.wait()
        js_data=data.response.body
        #print(js_data) #整体数据
        comments=js_data["comments"]

        for index in comments:
            shijian=index["create_time"]
            keys=index.keys()
            if "ip_label" in index:
                ip_label=index["ip_label"]
            else:
                ip_label="未知"
            dit={
                "时间":str(datetime.fromtimestamp(shijian)),
                "名字":index["user"]["nickname"],
                "地区":ip_label,
                "内容":index["text"]
            }
            all_data.append(dit)
            print(dit) #comments数据
            tmp=dy.ele('css:.ETuXBjRi')
            dy.scroll.to_see(tmp)
        time.sleep(1)
    
    # 保存为UTF-8格式的data.csv
    with open('data.csv', mode='w', encoding='utf-8', newline='') as f:
        csv_data=csv.DictWriter(f, fieldnames=['时间', '名字', '地区', '内容'])
        csv_data.writeheader()
        csv_data.writerows(all_data)
    
    # 保存为GBK格式的抖音.csv，处理特殊字符
    def clean_text_for_gbk(text):
        """清理文本，移除GBK不支持的特殊字符"""
        if not isinstance(text, str):
            return text
        # 移除emoji和其他特殊字符，保留中文、英文、数字、基本标点
        cleaned = ''.join(char for char in text if ord(char) < 0x10000 and char not in ['➖', '➕', '✨', '🔥', '❤️', '💕', '👍', '🎉', '🎊', '💯'])
        return cleaned
    
    # 清理数据中的特殊字符
    cleaned_data = []
    for item in all_data:
        cleaned_item = {
            "时间": item["时间"],
            "名字": clean_text_for_gbk(item["名字"]),
            "地区": clean_text_for_gbk(item["地区"]),
            "内容": clean_text_for_gbk(item["内容"])
        }
        cleaned_data.append(cleaned_item)
    
    with open('抖音.csv', mode='w', encoding='gbk', newline='') as f_gbk:
        csv_data_gbk=csv.DictWriter(f_gbk, fieldnames=['时间', '名字', '地区', '内容'])
        csv_data_gbk.writeheader()
        csv_data_gbk.writerows(cleaned_data)
    
    print(f"数据采集完成！共采集 {len(all_data)} 条评论")
    print("已保存为 data.csv (UTF-8格式)")
    print("已保存为 抖音.csv (GBK格式)")
    
except Exception as e:
    print(f"程序出错: {e}")
    # 如果出错，将已采集的数据保存
    if all_data:
        with open('data.csv', mode='w', encoding='utf-8', newline='') as f:
            csv_data=csv.DictWriter(f, fieldnames=['时间', '名字', '地区', '内容'])
            csv_data.writeheader()
            csv_data.writerows(all_data)
        print(f"已保存部分数据到 data.csv，共 {len(all_data)} 条")

finally:
    time.sleep(10)
    # 关闭浏览器
    dy.close()
    print("已关闭浏览器")
    #程序结束


