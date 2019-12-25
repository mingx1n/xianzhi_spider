# -*- coding: UTF-8 -*-
import os
import time
import requests
import random
import re
import html2text
from tqdm import tqdm
from bs4 import BeautifulSoup
useragents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
]
# 初始化
print("[+] ------------------欢迎使用先知社区爬虫------------------\n")


def get_url(url):
    stop = 0
    headers = {'User-Agent': random.choice(useragents)}
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    pages = int(soup.select('.disabled')[1].a.string[2:])
    print('[-] 开始爬取文章链接')
    if os.path.exists("./older.cache"):
        a = open("./older.cache", "r")
        url_old = a.read()
        a.close()
    else:
        url_old = ""
    f = open("url_list.txt", "w", encoding="utf-8")
    for i in tqdm(range(1, pages + 1), ncols=100):
        # print(" [*] 正在读取第%d页的链接" % (i))
        url = "https://xz.aliyun.com/?page=" + str(i)
        # print(url)
        headers = {'User-Agent': random.choice(useragents)}
        html = requests.get(url, headers=headers).text
        url_list = re.findall(r"\"topic-title\" href=\".+?\">", html)
        if i == 1:
            url_new = url_list[0]
            rel_url = "https://xz.aliyun.com" + url_new[20:].split('"')[0]
            a = open("./older.cache", "w")
            a.write(rel_url)
            a.close
        for i in url_list:
            rel_url = "https://xz.aliyun.com" + i[20:].split('"')[0]
            if rel_url == url_old:
                stop = 1
                break
            # print(rel_url)
            f.write(rel_url + "\n")
        if stop == 1:
            break
    f.close()
    print("[-] 爬取链接完毕\n------------------\n[+] 开始爬取博文")


def xianzhi_spider(url):
    headers = {
        'User-Agent': random.choice(useragents),
    }
    # # 获取网页主体
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'html.parser')
    dirpath = os.getcwd() + '/output/'  # 获取当前的文件路径
    tmp = soup.select('.label-default')
    dirpath = dirpath + tmp[0].a.string + '/' + tmp[1].a.string + '/'
    title = soup.find_all('title')[0].get_text()
    time_t = soup.select(".info-left")
    time_tmp = re.findall(r"\d{4}\-\d{2}\-\d{2}", str(time_t))
    time = time_tmp[0].replace("-", "")
    article = str(
        soup.find_all("div", class_="topic-content markdown-body")[0])

    # print(article)
    title = "[" + time + "]" + title.replace('*', '-').replace(
        '|', '-').replace('=', '-').replace(':', '-').replace(
            '\'', '-').replace('"', '-').replace('：', '-').replace(
                '】', '-').replace('【', '-').replace('/', '-').replace(
                    '\\', '-').replace('[', '').replace(']', '').replace(
                        '<', '').replace('>', '').replace('!', '').replace(
                            '_', '').replace(' ', '').replace('-', '')[0:30]
    write2md(dirpath, title, article)
    # print(html)


def write2md(dirpath, title, article):
    # # 创建转换器
    h2md = html2text.HTML2Text()
    h2md.ignore_links = False
    # # 转换文档
    article = h2md.handle(article)
    # # 写入文件
    if not os.path.exists(dirpath):  # 判断目录是否存在，不存在则创建新的目录
        os.makedirs(dirpath)
    if not os.path.exists(dirpath + '/img/'):  # 判断目录是否存在，不存在则创建新的目录
        os.makedirs(dirpath + '/img/')
    pic_list = re.findall(r"!\[\]\(.+?\)", article)  # 找到了所有文件
    # print(pic_list)
    for pic in pic_list:
        pic_url = pic[4:].split('\)')[0].replace(")", "")
        # print(pic_url)
        new_pic = str(hash(pic_url)) + '.png'
        new_pic = new_pic.replace("-", "")
        try:
            article = model_picture_download(pic_url,
                                             dirpath + '/img/' + new_pic,
                                             article, new_pic)
        except Exception as e:
            print(e)
        continue

    # 创建md文件
    with open(dirpath + title + '.md', 'w', encoding="utf8") as f:
        lines = article.splitlines()
        for line in lines:
            if line.endswith('-'):
                f.write(line)
            else:
                f.write(line + "\n")
    # print(title + "下载完成....")


def model_picture_download(pic_url, file_dir, text, new_pic):
    headers = {
        'User-Agent': random.choice(useragents),
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':
        'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2,',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    model_picture_downloaded = False
    err_status = 0
    while model_picture_downloaded is False and err_status < 10:
        try:
            html_model_picture = requests.get(pic_url,
                                              headers=headers,
                                              timeout=1)
            with open(file_dir, 'wb') as file:
                file.write(html_model_picture.content)
                model_picture_downloaded = True
                text = text.replace(pic_url, "./img/" + new_pic)
                # print('下载成功！图片 = ')
                return text
        except Exception as e:
            err_status += 1
            random_int = 4
            time.sleep(random_int)
            print(e)
            print('出现异常！睡眠 ' + str(random_int) + ' 秒')
            return text
        continue
    return text


def main():
    url = "https://xz.aliyun.com/"
    get_url(url)
    file = open("url_list.txt")
    lines = file.readlines()
    print('[*] 开始爬取文章')
    for i in tqdm(range(len(lines) - 2, 0, -1), ncols=100):
        line = lines[i].strip('\n')
        try:
            # print(line)
            xianzhi_spider(line)
        except Exception as e:
            raise e
    file.close()
    print("[-] 爬取博文完毕")
    # get_pic()


def get_pic():
    pwd = os.getcwd() + "/output/"

    for root, dirs, files in os.walk(pwd):
        for dir in dirs:
            if dir == "img":
                continue
            pro_dir = os.path.join(root, dir)
            dir_tmp = os.listdir(pro_dir)
            img_path = dir_tmp + "./img"
            if (os.path.exists(img_path)):
                print('[-] ' + img_path + "文件夹已经存在-正在更换图床\n")
            else:
                print('[-] ' + img_path + "文件夹不存在-新建文件夹中ing\n")
                os.makedirs(img_path)
                print('[-] ' + "./output/img文件夹已经存在-正在更换图床\n")
            for file in tqdm(dir_tmp, ncols=100):

                f = open(pro_dir + file, "r+", encoding='utf-8')
                text = f.read()
                f.close()
                print(file)
                # print(text)
                pic_list = re.findall(r"!\[\]\(.+?\)", text)  # 找到了所有文件
                for pic in pic_list:
                    pic_url = pic[4:].split('\)')[0].replace(")", "")
                    # print(pic_url)
                    new_pic = str(hash(pic_url)) + '.png'
                    new_pic = new_pic.replace("-", "")
                    try:
                        text = model_picture_download(
                            pic_url, pro_dir + 'img/' + new_pic, text, new_pic)
                        print(pic_url)
                        print(new_pic)
                    except Exception as e:
                        print(e)
                    continue

                f = open(pro_dir + file, "w+", encoding='utf-8')
                f.write(text)
                f.close()


# def test():
#     url = "https://xz.aliyun.com/t/6971"
#     con = requests.get(url).text
#     soup = BeautifulSoup(con, "lxml")
#     time = soup.select(".info-left")
#     time = re.findall(r"\d{4}\-\d{2}\-\d{2}", str(time))
#     time = time[0].replace("-",""))

main()
