from enum import auto
import sys
try:
    from selenium import webdriver
except:
    print('ERROR: Selenium WebDriver not found.\nPlease try: '+ sys.executable +' -m pip install selenium')
    exit(1)
try:
    import chromedriver_binary
except:
    print('ERROR: ChromeDriver not found.\nPlease try: '+ sys.executable +' -m pip install chromedriver_binary')
    exit(1)
try:
    import requests
except:
    print('ERROR: requests not found.\nPlease try: '+ sys.executable +' -m pip install requests')
    exit(1)
import time
import datetime
import selenium

import argparse
import random
import json

servers = {}
tool_version = '1.2'
auto_select = False

print(f"""*** RisuPu Speedtest CLI v{tool_version} ***
Copyright 2021 rspnet.jp, CyberRex
""")

parser = argparse.ArgumentParser(description='Measure your Internet speed using RisuPu Speedtest Servers.')
parser.add_argument('--list', help='Show the list of measure servers', action='store_true')
parser.add_argument('--server-id', help='Manually select server', type=int)
parser.add_argument('--save-image', help='Save result image', action='store_true')
parser.add_argument('--hide-isp', help='Don\'t show ISP name', action='store_true')

args = parser.parse_args()

if args.server_id is None:
    server_id = -1
    auto_select = True

driver_opt = webdriver.ChromeOptions()
driver_opt.add_argument('--headless')
driver_opt.add_argument('--no-sandbox')
driver_opt.add_argument('--disable-gpu')
driver_opt.add_argument("--disable-logging")
driver_opt.add_argument('--log-level=3')

try:
    driver = webdriver.Chrome(options=driver_opt)
except selenium.common.exceptions.WebDriverException as e:
    if 'PATH' in str(e):
        print('ERROR: ChromeDriver not found.\nPlease try: '+ sys.executable +' -m pip install chromedriver_binary')
        exit(1)
    elif 'Chrome binary' in str(e):
        print('ERROR: Chrome is not installed.')
    else:
        print('ERROR: An unknown error occured.')
        print(str(e))
        exit(1)

driver.implicitly_wait(10)

try:
    driver.get('https://librespeed.speedtest.jp.net/')
except selenium.common.exceptions.WebDriverException:
    print('ERROR: failed to load speedtest page.\nCheck your internet connection.')
    driver.quit()
    exit(1)

# サーバーリスト取得

tid = str(random.random()).replace('.', '')
try:
    driver.execute_script('var telm = document.createElement("div");telm.id="temp_pipe_element_'+tid+'";telm.innerHTML=JSON.stringify(window.SPEEDTEST_SERVERS);document.body.appendChild(telm);')
except:
    print('ERROR: failed to get servers infomation.')
    driver.quit()
    exit(1)

try:
    jsdata_obj = driver.find_element_by_id(f'temp_pipe_element_{tid}')
except:
    print('ERROR: failed to load servers infomation.')
    driver.quit()
    exit(1)

server_list = json.loads(jsdata_obj.text)

for i, server in enumerate(server_list):
    servers.update({
        server['name']: {'id': i}
    })

if args.list:
    print('Available servers:')
    for k, v in servers.items():
        print(f'\t{v["id"]}: {k}')
    print(f'\nIf you choose {list(servers.keys())[0]}, run this:')
    print(f'\t'+ sys.executable + f' ./run_speedtest.py --server-id {servers[list(servers.keys())[0]]["id"]}')
    driver.quit()
    exit()

if not auto_select:
    if args.server_id < 0:
        print('ERROR: server_id is invalid.')
        exit(1)

    if len(servers.keys()) < args.server_id:
        print(f'ERROR: ID {args.server_id} not found.')
        exit(1)

    server_id = args.server_id


# サーバー選択

if server_id == -1:

    # pingから自動選択

    spings = []
    
    for k ,v in servers.items():
        sid = v['id']
        tid = str(random.random()).replace('.', '')
        driver.execute_script('var telm = document.createElement("div");telm.id="temp_pipe_element_'+tid+'";telm.innerHTML=window.SPEEDTEST_SERVERS['+ str(sid) +'].server+window.SPEEDTEST_SERVERS['+ str(sid) +'].pingURL;document.body.appendChild(telm);')
        time.sleep(0.1)
        ub = driver.find_element_by_id('temp_pipe_element_'+tid)
        pingurl = ub.text
        
        t = time.time()
        r = requests.get(pingurl+'?cors=true&'+str(random.random()))
        pingtime = time.time() - t
        spings.append({
            'id': sid,
            'name': k,
            'ping': pingtime
        })
    
    s_spings = sorted(spings, key=lambda x: x['ping'])

    server_id = s_spings[0]['id']
    print('Automatically selected server: '+ s_spings[0]['name'])


try:
    driver.execute_script('s.setSelectedServer(SPEEDTEST_SERVERS['+ str(server_id) +'])')
except selenium.common.exceptions.JavascriptException:
    print('ERROR: failed to select server.')
    driver.quit()
    exit(1)
    
if not auto_select:
    print('Server: ' + list(servers.keys())[server_id])

# ISP取得
if not args.hide_isp:
    r = requests.get('https://librespeed.speedtest.jp.net/backend/getIP.php?cors=true&isp=true&distance=km')
    try:
        ispinfo = r.json()
        print(f'ISP: {ispinfo["rawIspInfo"]["org"]} ({ispinfo["rawIspInfo"]["country"]})')
    except:
        print('ISP: Unknown')


print('Running speedtest, please wait...')
start_button = driver.find_element_by_id('startStopBtn')
start_button.click()

# 結果が出るまで待機
while True:
    result_img = driver.find_element_by_id('resultsImg')
    src = result_img.get_attribute('src')
    if src:
        print('Test ended.')
        if args.save_image:
            print('Downloading image...', end='')
            r = requests.get(src)
            now = datetime.datetime.now()
            fname = 'speedtest_' + now.strftime('%Y-%m-%d_%H-%M-%S') + '.png'
            with open(fname ,'wb') as f:
                f.write(r.content)
            print('done')

        dlMeter = driver.find_element_by_id('dlText')
        upMeter = driver.find_element_by_id('ulText')
        pingMeter = driver.find_element_by_id('pingText')
        jitterMeter = driver.find_element_by_id('jitText')
        resultURL = driver.find_element_by_id('resultsURL')

        dlSpeed = dlMeter.text
        upSpeed = upMeter.text
        pingI = pingMeter.text
        jitterI = jitterMeter.text
        shareURL = resultURL.get_attribute('value')

        break
    time.sleep(1)

driver.quit()
print(f'\nPing: {pingI}ms / Jitter: {jitterI}ms')
print(f'DL: {dlSpeed}Mbps / UL: {upSpeed}Mbps')
print(f'Share link: {shareURL}')
if args.save_image:
    print('Result image file: ' + fname)