#抓取单条mobile微博上的图片

import requests
import shutil
import os
import time

#从cookie.txt里读取cookie
#这个可以从chrome浏览器f12，然后在console里打document.cookie来显示当前cookie
#注意cookie不是一直有效的，每次跑之前手动更新吧
with open("cookie.txt", 'r', encoding="utf8") as fp:
    cookie = fp.readlines()

saving_path = "d:/images/weibo/"
fetch_interval = 2 #抓取间隔多少秒
headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; HUAWEI NXT-AL10 Build/HUAWEINXT-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043804 Mobile Safari/537.36'}
headers["Content-Type"] = 'utf-8'  #编码设置，这个不用动

#urllist = ['https://m.weibo.cn/status/FBgBzvIlu']
urllist = []
with open('fetch_list.txt', 'r' , encoding="utf-8") as fp:
    for line in fp:
        line = line.strip()
        if(len(line) > 0):
            urllist.append(line)

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
        print ("[INFO]got from " + url + ", saving to: " + save_path)
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
    wfp = open(error_log_name, 'w+', encoding="utf-8")
    wfp.write('[' + my_time + ']' + str(content))
        
def load_page(page):
    try:
        r = requests.get(page, data={}, timeout = 15, headers=headers)
        html = r.text
        original_pic = find_between(html, '"original_pic": "', '"')
        user_name = find_between(html, '"screen_name": "', '"')
        final_save_dir = saving_path + user_name #保存位置
        #用mkdir一下新建目录，省得写入失败
        print ("use " + final_save_dir + " as target dir...")
        create_rs = new_mkdirs(final_save_dir)
        #print (create_rs)

        #解析数据
        pic_area = find_between(html, '"pic_ids": [', ']')
        #print (pic_area)
        pics = find_betweens(pic_area, '"', '"')
        #print (pics)
        front_url = 'http://' + original_pic.split("http://")[1].split("/")[0] + '/large/'

        #拼接url
        if(len(pics) > 0):
            for s_url in pics:
                download_image(front_url + s_url , headers, final_save_dir, user_name + "_", '.jpg')
                time.sleep(fetch_interval)
        else:
            download_image(original_pic, headers, final_save_dir, user_name + "_")
    except Exception as e:
        print (e)
        write_log("failed to load page:" + str(page))

count = 0
for page in urllist:
    load_page(page)
    count = count + 1
print ("task done. run for " + str(count) + " page(s).")

