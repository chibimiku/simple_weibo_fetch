# -*- coding: utf-8 -*-
#抓取单条mobile微博上的图片

import requests
import shutil
import os
import time
import imghdr
import json
import io,sys


#有效的站点类型
good_type = ['weibo', 'bcy']

def init_cookie(site_name):
    #从cookie.txt里读取cookie
    #这个可以从chrome浏览器f12，然后在console里打document.cookie来显示当前cookie
    #注意cookie不是一直有效的，每次跑之前手动更新吧
    cookie=''
    with open("data/" + site_name + "_cookies.txt", 'r', encoding="utf8") as fp:
        cookie = fp.readlines()
    cookie = str(cookie)
    print ("Loaded cookies:" + cookie)
    #headers["Cookie"] = cookie
    return cookie

def find_betweens(s, first, last):
    ret_list = []
    probe = 0 #标示从哪里开始找
    next_find_sign = True
    while(next_find_sign):
        try:
            start = s.index(first, probe) + len(first)
            end = s.index(last, start)
            ret_list.append(s[start:end])
            probe = end + len(last) #从上一个结束的位置继续往下找
        except Exception as e:
            next_find_sign = False
    return ret_list

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except Exception as e:
        print (e)

#下载图片到某个路径下面
def download_image(url, headers, path, prefix = '', suffix = ''):
    save_path = path + "/" + prefix + url.split("/")[-1] + suffix
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as fp:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, fp)
        #判断图片格式
        filetype = imghdr.what(save_path)
        final_name = save_path + "." + filetype
        os.rename(save_path, final_name)
        print ("[INFO]got from " + url + ", saving to: " + final_name)
    else:
        print ("[ERROR]cannot get from " + url)
        
def new_mkdirs(in_path):
    try:
        if(not os.path.exists(in_path)):
            print ("target dir " + in_path + "not exists. try to create new one...")
            os.makedirs(in_path)
            return True
    except Exception as e:
        print (e)
        return False

def write_log(content, error_log_name = "error.log"):
    my_time = time.strftime('%Y%m%d %H:%M:%S', time.localtime(time.time()))
    wfp = open(error_log_name, 'a+', encoding="utf-8")
    wfp.write('[' + my_time + ']' + str(content))
    wfp.close()
        
def output_file(content, target_file):
    wfp = open(target_file, 'w', encoding="utf-8")
    wfp.write(content)
    wfp.close()
        
def unicode_convert(in_str):
    return in_str.encode('utf-8').decode('unicode_escape')
        
def get_datas_from_status(html):
    pass

#万能入口，解析url并选择合适的load方法.    
def load_page(page, saving_path, common_headers, real_download_image = True):
    if('weibo.com' in page):
        return load_weibo_page(page, saving_path + 'weibo/', common_headers)
    elif('weibo.cn' in page):
        return load_weibo_page(page, saving_path + 'weibo/', common_headers)
    elif('bcy.net' in page):
        return load_bcy_page(page, saving_path + 'bcy/', common_headers)
    else:
        print ("[WARNING]cannot found entry for url:" + page)
        
def load_weibo_page(page, saving_path, my_headers, need_save_image = True):
    my_cookie = init_cookie('weibo')
    headers["Cookie"] = my_cookie
    try:
        print ("try to get url:" + page + " ...")
        write_log("[INFO]try to fetch..." + page)
        
        #如果不包含show?这种形式，然后又带个?的，会自动把问号后面的参数干掉
        if('?' in page):
            if(not 'show?' in page):
                split_temp = page.split("?")
                page = split_temp[0]
        
        if('//weibo.com/' in page):
            print ("web weibo detected, try to trans to wap...")
            #page = page.replace('//weibo.com', '//m.weibo.cn')
            #对型如weibo.com/xxxxx/yyyyy的形式操作
            rel_temp = page.split("/")
            page = "https://m.weibo.cn/statuses/show?id=" + rel_temp[4]
            
        #convert from status to statuses
        if('m.weibo.cn/status/' in page):
            page = page.replace('status/', 'statuses/show?id=')
        print ("final url:" + page)
        
        r = requests.get(page, data={}, timeout = 15, headers=headers)
        html = r.text
        output_file(html, 'debug.html')

        original_pic = unicode_convert(find_between(html, '"original_pic":"', '"'))
        original_pic = original_pic.replace("\/", "/")
        user_name = unicode_convert(find_between(html, '"screen_name":"', '"'))
        print ("got username:" + user_name)
        
        final_save_dir = saving_path + user_name #保存位置
        #用mkdir一下新建目录，省得写入失败
        print ("use " + final_save_dir + " as target dir...")
        create_rs = new_mkdirs(final_save_dir)
        #print (create_rs)

        #解析数据
        pic_area = find_between(html, '"pic_ids":[', ']')
        #print (pic_area)
        pics = find_betweens(pic_area, '"','"')
        print (pics)
        front_url = 'http://' + original_pic.split("http://")[1].split("/")[0] + '/large/'

        
        #拼接url
        if(len(pics) > 0):
            for s_url in pics:
                if (need_save_image):
                    download_image(front_url + s_url , headers, final_save_dir, user_name + "_")
                    time.sleep(fetch_interval)
                else:
                    print ('[img]' + front_url + s_url + '.jpg[/img]')
                
        else:
            if (need_save_image):
                download_image(original_pic, headers, final_save_dir, user_name + "_")
            else:
                print ('[img]' + original_pic + '.jpg[/img]')
        return True
    except Exception as e:
        print (e)
        write_log("failed to load page:" + str(page))
        return False

def non_gbk_filter(in_str):
    return in_str.replace("\\",'_').replace('?', '_').replace('\'', '_').replace('/', '_').replace('|', '_').replace('"', '_').replace('*', '_')
        
def load_bcy_page(page, saving_path, my_headers):
    my_cookie = init_cookie('bcy')
    my_headers["Cookie"] = my_cookie
    try:
        r = requests.get(page, data={}, timeout = 15, headers=my_headers)
        html = r.text
        output_file(html, 'data/debug.html')
        author_tmp = find_between(html, '<a class="_avatar', '>')
        author_name = non_gbk_filter(find_between(author_tmp, 'title="', '"'))
        author_uid = find_between(author_tmp, 'href="/u/', '"')
        title = non_gbk_filter(find_between(html, '<h1 class="js-post-title">', '</h1>').strip())
        img_lines = find_betweens(html, "<img class='detail_std detail_clickable' src='", "' />")
        print ("found " + str(len(img_lines)) + " pic(s) in " + page + " ...")
        final_save_dir = saving_path + author_name #保存位置
        #用mkdir一下新建目录，省得写入失败
        print ("use " + final_save_dir + " as target dir...")
        create_rs = new_mkdirs(final_save_dir)
        for img_line in img_lines:
            if('/w650' in img_line):
                img_line = img_line.replace('/w650', '')
            download_image(img_line, my_headers, final_save_dir, str(author_uid) + "_" + author_name + "_" + title + "_")
            time.sleep(fetch_interval)
    except Exception as e:
        print (e)
        write_log("failed to load page:" + str(page))
        return False
    return True

saving_path = "d:/images/"
fetch_interval = 2 #抓取间隔多少秒
headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; HUAWEI NXT-AL10 Build/HUAWEINXT-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043804 Mobile Safari/537.36'}
headers["Content-Type"] = 'utf-8'  #编码设置，这个不用动
urllist = []
with open('fetch_list.txt', 'r' , encoding="utf-8") as fp:
    for line in fp:
        line = line.strip()
        if(len(line) > 0):
            urllist.append(line)

count = 0
fail_count = 0

for page in urllist:
    rs = load_page(page, saving_path, headers, True)
    if(not rs):
        fail_count = fail_count + 1
    count = count + 1

print ("task done. run for " + str(count) + " page(s). " + str(fail_count) + " page(s) failed. check error log.")
