from value import header_1, header_2, app_v, zb_id, cookie
import requests
import json
import time
import re

head = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"}


def down_order():
    """ 下单 """
    a = 0
    while True:
        try:
            api = "https://api.bilibili.com/x/garb/trade/create"
            data = {"item_id": f"{zb_id}",
                    "platform": "android",  # "platform": "android",
                    "currency": "bp",
                    "add_month": -1,
                    "buy_num": 1,
                    "coupon_token": "",
                    "hasBiliapp": "true",
                    "csrf": f"{cookie['bili_jct']}"}
            r1 = requests.post(api, headers=header_1, cookies=cookie, data=data)
            print(r1.text)
            order_id = r1.json()['data']['order_id']
            if not order_id:
                continue
            return order_id
        except:
            print(f"下单失败 重试:{a}次")
            if a >= 10:
                return "下单失败"
            a += 1
            time.sleep(0.1)


def confirm_order(order_id):
    """ 确认订单 """
    a = 0
    while True:
        a += 1
        print(f"获取pay_data... {a}")
        api = "https://api.bilibili.com/x/garb/trade/confirm"
        data = {"order_id": f"{order_id}", "csrf": f"{cookie['bili_jct']}"}
        r1 = requests.post(api, headers=header_1, cookies=cookie, data=data).json()
        print(r1)
        pay_data = r1['data']['pay_data']
        if not pay_data:
            continue
        pay_json = json.loads(pay_data)
        return pay_json


def get_pay_data(data):
    """ 获取付款验证表单以及cookie """
    url_api = "https://pay.bilibili.com/payplatform/pay/pay"
    data1 = {
        "appName": "tv.danmaku.bili",
        "appVersion": app_v,
        "payChannelId": "99",
    }
    for li in data:
        data1[li] = data[li]
    data1['sdkVersion'] = "1.4.9"
    data1['device'] = "ANDROID"
    data1['payChannel'] = "bp"
    data1['network'] = "WiFi"

    response = requests.post(url_api, headers=header_2, json=data1)
    print(response.text)
    cookie_str = re.split(";", response.headers['Set-Cookie'])[0]
    cookie_pay = {"payzone": cookie_str.replace("payzone=", "")}
    pay_data = json.loads(response.json()['data']['payChannelParam'])
    return cookie_pay, pay_data


def pay(cookie_pay, data):
    api = "https://pay.bilibili.com/paywallet/pay/payBp"
    r1 = requests.post(api, cookies=cookie_pay, json=data, headers=header_2)
    print(r1.text)


def start_pay():
    order_id = down_order()
    if "下单失败" == order_id:
        print("寄了")
        return
    print(order_id)
    pay_json = confirm_order(order_id)
    cookie_pay, pay_data = get_pay_data(pay_json)
    print(cookie_pay, pay_data)
    pay(cookie_pay, pay_data)


def get_open_time():
    api = f"https://api.bilibili.com/x/garb/mall/item/suit/v2?item_id={zb_id}"
    r1 = requests.get(api, headers=head).json()
    if r1['code'] != 0:
        print("错误")
        return None
    return int(r1['data']['item']['properties']['sale_time_begin'])


def bili_time():
    api = 'http://api.bilibili.com/x/report/click/now'
    r1 = requests.get(api, headers=head).json()
    return r1['data']['now']


def main():
    open_time = get_open_time()
    # open_time = 1
    while True:
        bili_now_time = bili_time()
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(bili_now_time))
        print("b站时间:", time_string)
        if bili_now_time >= open_time:
            s = time.time()
            start_pay()
            e = time.time()
            input(f"-------购买完成 耗时:{e - s}秒")
            break
        time.sleep(0.5)


if __name__ == '__main__':
    main()
