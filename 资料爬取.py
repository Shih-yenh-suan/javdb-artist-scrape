import pandas as pd
import os
import requests
import random
import time
import re
from lxml import etree

baseUrl = "https://javdb521.com/"
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0'}

def getArtistMainPage(artist):
    """获取演员主页"""
    url = baseUrl + "search?f=actor"
    query= {
        "q": artist
    }
    htmlData = requests.get(url=url,headers=header, params = query).text
    parsedHtmls = etree.HTML(htmlData)
    
    artistURL = parsedHtmls.xpath('//div[@class = "box actor-box"]/a/@href')
    artistURL = [baseUrl + artistURL for artistURL in artistURL]
    return artistURL[0]

# metaData
def getMetaData(url, page):
    """获取演员演出目录元数据，包括番号、标题、得分、发行日、网页"""
    query= {
        "page": page
    }
    
    htmlData = requests.get(url=url,headers=header, params = query).text
    parsedHtmls = etree.HTML(htmlData)
    
    empty = parsedHtmls.xpath('//div[@class = "empty-message"]/text()')
    
    if empty == []:
        bangou = parsedHtmls.xpath('//div[@class = "video-title"]/strong/text()') 
        title = parsedHtmls.xpath('//div[@class = "video-title"]/text()') 
        title = [re.sub(r'[\/:*?"<>| ]', "_", title) for title in title]
        score = parsedHtmls.xpath('//span[@class = "value"]/text()') 
        score = [re.sub(r'\s', "", score) for score in score]
        outtime = parsedHtmls.xpath('//div[@class = "meta"]/text()') 
        outtime = [re.sub(r'\s', "", outtime) for outtime in outtime]
        movieUrl = parsedHtmls.xpath('//div[@class = "item"]/a/@href') 
        movieUrl = [baseUrl + movieUrl for movieUrl in movieUrl]
        empty = parsedHtmls.xpath('//div[@class = "empty-message"]/text()')
        
        movieIndex = {
            '番号': bangou, 
            '标题': title, 
            "得分":score, 
            "发行日期":outtime, 
            "详情页": movieUrl,
        }
        return movieIndex
    else:
        return 0
     
   
def SaveData(path, artist, data):
    df = pd.DataFrame(data)
    df.to_csv(path, mode = 'a', header = 0, encoding = 'utf-8')
    
def getTorrent(url):
    """获取电影链接和更多信息"""
    htmlData = requests.get(url=url,headers=header).text
    parsedHtmls = etree.HTML(htmlData)
    timeLast = parsedHtmls.xpath("/html/body/section/div/div[4]/div[1]/div/div[2]/nav/div[3]/span/text()")
    timeLast = [re.sub(r'\s', "", timeLast) for timeLast in timeLast]
    torrents = parsedHtmls.xpath('//*[@id="magnets-content"]/div/div[1]/a/@href')
    torrentList = []
    for t in torrents:
        torrentList.append(t)
    tagsRow = parsedHtmls.xpath('//span[@class= "value"]/a/text()')
    tagsHref = parsedHtmls.xpath('//span[@class= "value"]/a/@href')
    tags = [tag for tag, href in zip(tagsRow, tagsHref) if href.startswith('/tags')]
    
    tagsList = []
    for t in tags:
        tagsList.append(t)

    return [timeLast, torrentList, tagsList]

    
def main():

    path = f"D:\ZZZMydocument\Codes\资料案例\爬虫资料"
    
    artist = input("想要爬取哪位？")
    page = 1

    csvPath = path + "\\" + artist + '.csv'
    if os.path.exists(csvPath):
        os.remove(csvPath)
    
    url = getArtistMainPage(artist)
    
    
    while True:
        print(f"开始爬取第{page}页")
        data = {}
        data = getMetaData(url, page)
                
        if data == 0:
            print(f"第{page}页不存在")
            break
        
        page += 1
        
        data["持续时间"] = []
        data["种子"] = []
        data["标签"] = []    
        for u in data["详情页"]:
            print(f"开始爬取：{u}")
            detailInfo= getTorrent(u)
            time.sleep(random.random())
            data["持续时间"].append(detailInfo[0])
            data["种子"].append(detailInfo[1])
            data["标签"].append(detailInfo[2])

        SaveData(csvPath, artist, data)
    
if __name__ == '__main__':
    main()
