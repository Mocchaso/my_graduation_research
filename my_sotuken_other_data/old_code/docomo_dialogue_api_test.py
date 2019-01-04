# -*- coding: utf-8 -*-

import requests
import json
from _datetime import datetime

# your APIKEY
KEY = '63743363366345624f487a4e785546544e39787175547435303053456f517653493857386745624f616944'

# リクエストクエリ
endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/dialogue?APIKEY=REGISTER_KEY'
url = endpoint.replace('REGISTER_KEY', KEY)


#　user registration
def register():
    r_endpoint = 'https://api.apigw.smt.docomo.ne.jp/naturalChatting/v1/registration?APIKEY=REGISTER_KEY'
    r_url = r_endpoint.replace('REGISTER_KEY', KEY)
    r_headers = {'Content-type': 'application/json'}
    pay = {
        "botId": "Chatting",
        "appKind": "Smart Phone"
    }
    r = requests.post(r_url, data=json.dumps(pay), headers=r_headers)
    appId = r.json()['appId']
    return appId


def reply(appId, utt_content):
    headers = {'Content-type': 'application/json;charset=UTF-8'}
    payload = {
        "language": "ja-JP",
        "botId": "Chatting",
        "appId": appId,
        "voiceText": utt_content,
        "appRecvTime": "2018-06-11 22:44:22",  # 仮置き。これで動いてしまう。
        "appSendTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    # Transmission
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    data = r.json()
    # rec_time = data['serverSendTime']
    response = data['systemText']['expression']

    print("response: %s" % response)
    return response



if __name__ == "__main__":
    # appIdを取得した2回目以降、コメントアウトして55行目に記載
    appId = register()
    print(appId)
    # appId = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    while True:
        utt_content = input('>>')
        reply(appId, utt_content)