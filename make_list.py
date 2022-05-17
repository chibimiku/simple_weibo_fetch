#根据搜索结果生成fetch_list

import time,requests
from urllib import parse

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

def output_file(content, target_file):
    wfp = open(target_file, 'w', encoding="utf-8")
    wfp.write(content)
    wfp.close()
        
def load_cosp_search_page(page, saving_path, search_char_id, search_max_page):
    my_headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    my_headers["Content-Type"] = 'utf-8'  #编码设置，这个不用动
    my_headers['Referer'] = 'http://cosp.jp/'
    cookie = init_cookie('cosp')
    save_file = saving_path + '/' + 'cosp_' + search_char_id + ".txt"

    wfp = open(save_file, 'w+', encoding='utf-8')
    for i in range(1, search_max_page):
        search_parm_str = '40,' + str(i) + ',23700,1,0,,,10514,' + str() + ',,,,,,,,1,1,0,0,0,0,0,0'
        get_url = page + "&p=" + search_parm_str
        print ("get list url:" + get_url)
        r = requests.get(get_url, data={}, timeout = 15, headers=my_headers)
        html = r.text
        output_file(html, 'debug.html')
        urls = find_betweens(html, '<a href="/view_photo.aspx?', '" ')
        for url in urls:
            wfp.write('http://cosp.jp/view_photo.aspx?' + url)
            wfp.write('\n')
        print (str(len(urls)) + " result(s) in "+ str(i) + " pages for " + str(search_max_page) + " in total.")
        time.sleep(1)
    wfp.close()
    
        
def load_bcy_search_page(page, saving_path, search_query_key, search_query_value, search_page_key, search_max_page):
    my_headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; HUAWEI NXT-AL10 Build/HUAWEINXT-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/043804 Mobile Safari/537.36'}
    my_headers["Content-Type"] = 'utf-8'  #编码设置，这个不用动
    cookie = init_cookie('bcy')
    my_headers["Cookie"] = cookie
    save_file = saving_path + '/' + 'bcy_' + search_query_value + ".txt"
    wfp = open(save_file, 'w+', encoding='utf-8')
    for i in range(1, search_max_page):
        get_url = page + "&" + search_query_key + '=' + search_query_value + '&' + search_page_key + '=' + str(i)
        print ("get list url:" + get_url)
        r = requests.get(get_url, data={}, timeout = 15, headers=my_headers)
        html = r.text
        output_file(html, 'debug.html')
        content_temp = find_between(html, '<ul class="searchList l-clearfix">', '</ul>')
        details = find_betweens(content_temp, '<a href="/coser/detail/', '" ')
        #print (details)
        for line in details:
            wfp.write('https://bcy.net/coser/detail/' + line)
            wfp.write('\n')
        time.sleep(2)
    wfp.close()
        

load_cosp_search_page('http://cosp.jp/photo_proxy.aspx?t=search&k=', 'data/lists/', '86447', 593)
#load_bcy_search_page('https://bcy.net/search/home?', 'data/lists/', 'k', '小泉花阳', 'p', 143)