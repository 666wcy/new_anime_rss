# -*- coding: utf-8 -*-
import requests
import feedparser
import json
import os
import sys
import qbittorrentapi
os.chdir(os.path.dirname(__file__))


def ping():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            conf = json.loads(f.read())
            f.close()
    except:
        print("读取config失败")
        return
    QB_host = conf["QB_host"]
    QB_password = conf["QB_password"]
    QB_username = conf["QB_username"]
    QB_port = conf["QB_port"]
    qbt_client = qbittorrentapi.Client(host=QB_host, port=QB_port, username=QB_username, password=QB_password)
    try:
        print(qbt_client.auth_log_in())
        print("ssuccess!!! qb连接成功，配置正确")
    except Exception as e:
        print(f"error!!! qb配置不正确，请检查配置,错误信息：{e}")


def qb_addurl(fileurl,name,category):
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            conf = json.loads(f.read())
            f.close()
    except:
        print("读取config失败")
        return
    QB_host = conf["QB_host"]
    QB_password = conf["QB_password"]
    QB_username = conf["QB_username"]
    QB_port = conf["QB_port"]
    QB_download = conf["QB_download"]
    qbt_client = qbittorrentapi.Client(host=QB_host, port=QB_port, username=QB_username, password=QB_password)
    qbt_client.torrents_add(urls=fileurl,save_path=f"{QB_download}{name}/",category=category)


def creat_json():
    if os.path.exists('rss.json')==False:
        none_list=[]
        with open('rss.json', 'w') as f:
            json.dump(none_list, f)
        f.close()

def read_json():
    # 读取存储于json文件中的列表

    with open('rss.json', 'r') as f_obj:
        rss_list = json.load(f_obj)
    f_obj.close()
    return rss_list

def save(rss_list):
    with open('rss.json', 'w') as f_obj:
        json.dump(rss_list, f_obj)
    f_obj.close()


def checkrss(name,rssurl,season):
    global num,text
    rss_list = read_json()
    print(f"开始Rss:{name}")
    try:
        d = feedparser.parse(rssurl)
    except:
        return 
    print(f"Rss获取完成:{name}")


    for a in d.entries:
        pan = 0
        title = str(a["title"])
        title = title.replace("\\", " ").replace("/", " ").replace("&", " ").replace("​", "")
        title.lstrip()
        url = str(a["links"][1]["href"])

        for b in rss_list:
            if b["url"] == url:
                pan = 1

        if pan == 0:
            info_dict = {"title": title, "url": url}

            print(f"添加：{title}")
            text=text+f"\n推送下载:`{title}`\n"
            qb_addurl(fileurl=url,name=name,category=season)

            rss_list.append(info_dict)

            num = num + 1
    save(rss_list)

if __name__ == '__main__':

    creat_json()
    text="检查到更新"
    num=0
    print(len(sys.argv))
    if len(sys.argv)==1:
        print("无参数，默认直接运行")
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                conf = json.loads(f.read())
                f.close()
        except:
            print("读取config失败")
            exit()
        rss_url_list = list(conf["rss_list"])
        Telegram_bot_api=conf['Telegram_bot_api']
        Telegram_user_id=conf['Telegram_user_id']
        for a in rss_url_list:
            checkrss(name=a['name'],rssurl=a['rss_url'],season=a['season'])

    else:
        key=sys.argv[1]
        print(key)
        if key == "qb":
            ping()


    print("更新%d磁力" % num)
    if num!=0 and Telegram_bot_api!="" and Telegram_user_id!="":
        send_url=f"https://api.telegram.org/bot{Telegram_bot_api}/sendMessage"
        params={
            "chat_id":Telegram_user_id,
            "text":text,
            "parse_mode":"MarkdownV2"

        }
        requests.get(url=send_url,params=params)

