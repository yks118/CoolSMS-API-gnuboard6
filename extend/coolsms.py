import os
import json
import requests
import time
import uuid
import hmac
import hashlib
import math
import re

class CoolSMS:
    # API URL
    __url = 'https://api.coolsms.co.kr/'

    # API KEY
    __key = ''

    # API Secret
    __secret = ''

    # API Version
    __version = '1.6'

    # API Sender ID Version
    __senderIDVersion = '1.2'

    __data = {
        "byte": {
            "sms": 90,
            "lms": 2000
        },
        "charge": {
            "sms": 20,
            "lms": 50
        },
        "senderid": {
            "list": {},
            "default": ""
        }
    }

    __srk = 'K0010535426'

    def __init__(self):
        # 설정 파일을 읽어옵니다.
        path = os.path.dirname(__file__)
        with open(path + '/config.json') as f:
            config = json.load(f)
            self.__key = config['CoolsmsApiKey']
            self.__secret = config['CoolsmsApiSecret']

        # 발신자 정보를 가져옵니다.
        self.__data['senderid']['list'] = self.get_sender_id_list()
        for row in self.__data['senderid']['list']:
            if row['flag_default'] == 'Y':
                self.__data['senderid']['default'] = row['phone_number']

    def __get_signature(self, timestamp, salt):
        key = bytes(self.__secret, 'utf-8')
        msg = str(timestamp).encode('utf-8') + str(salt).encode('utf-8')
        return hmac.new(key, msg, hashlib.md5).hexdigest()

    def __authentication(self, data):
        timestamp = int(time.time())
        salt = uuid.uuid4()
        signature = self.__get_signature(timestamp, salt)

        data['api_key'] = self.__key
        data['timestamp'] = timestamp
        data['salt'] = salt
        data['signature'] = signature
        return data

    def __get(self, method, version, action, data=None):
        if data is None:
            data = {}

        url = self.__url + method + '/' + version + '/' + action
        response = requests.get(url, self.__authentication(data))
        return response.json()

    def __post(self, method, version, action, data=None):
        if data is None:
            data = {}

        url = self.__url + method + '/' + version + '/' + action
        response = requests.post(url, self.__authentication(data))
        return response.json()

    def __getByte(self, text):
        byte = 0
        length = text.encode('utf-8').__len__()

        for i in range(1, length):
            char = text[i - 1:i]
            str_hex = char.encode('utf-8').hex()
            len = str_hex.__len__()
            if str_hex == '0D':
                # CR (Carriage Return)
                ...
            elif str_hex == '0A':
                # LF (Line Feed)
                byte += 1
            elif len == 2:
                # 1byte: [0-9a-zA-Z]
                byte += 1
            elif len == 6:
                # 3byte: [가-히]
                byte += 2

        return byte

    def get_sender_id_list(self):
        return self.__get('senderid', self.__senderIDVersion, 'list')

    def get_status(self, params=None):
        # $data = $this->get('sms', $this->version, 'status', $param);
        return self.__get('sms', self.__version, 'status', params)

    def get_data(self):
        return self.__data

    def get_balance(self):
        return self.__get('sms', self.__version, 'balance')

    def get_remaining(self, cash, point, service):
        return math.floor((cash + point) / self.__data['charge'][service])

    def get_sent(self, params):
        return self.__get('sms', self.__version, 'sent', params)

    def send(self, data):
        response = {}

        if data['to'] and data['text']:
            if data['from'] is None:
                data['from'] = self.__data['senderid']['default']

            # 하이픈 제거
            data['to'] = re.sub(r'[^0-9,]', r'', data['to'])
            data['from'] = re.sub(r'[^0-9]', r'', data['from'])

            if data['datetime']:
                # 숫자만 남기고 제거
                data['datetime'] = re.sub(r'[^0-9]', r'', data['datetime'])
            else:
                data['datetime'] = ''

            if self.__srk:
                data['srk'] = self.__srk

            if 'type' not in data:
                # 문자 byte를 가져옴..
                byte = self.__getByte(data['text'])

                if byte <= self.__data['byte']['sms']:
                    data['type'] = 'SMS'
                elif byte <= self.__data['byte']['lms']:
                    data['type'] = 'LMS'

            if data['type']:
                if data['to'] and data['from']:
                    res = self.__post('sms', self.__version, 'send', data)

                    if res['result_message'] == 'Success':
                        response['status'] = True
                        response['message'] = '문자 발송에 성공하였습니다.'
                else:
                    response['status'] = False
                    response['message'] = '번호를 확인해주세요.'
            else:
                response['status'] = False
                response['message'] = '문자 길이를 체크해주세요.'
        else:
            response['status'] = False
            response['message'] = '문자 발송에 실패하였습니다.'

        return response

    def cancel(self, data):
        if 'mid' in data or 'gid' in data:
            # 메시지ID 혹은 그룹ID 가 존재
            res = self.__post('sms', self.__version, 'cancel', data)

            if 'errorCode' not in res:
                return True

        return False
