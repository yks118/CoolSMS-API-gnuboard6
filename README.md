# CoolSMS-API-gnuboard6
[그누보드6](https://github.com/gnuboard/g6) 용 [CoolSMS](https://www.coolsms.co.kr/) 플러그인입니다.

## Install Module
해당 플러그인을 사용하기 위해서는 requests 모듈이 추가로 필요하기에 설치합니다.
```bash
pip install requests
```

## File Upload
다운로드 받은 파일을 /plugin/ 에 coolsms 폴더를 생성해서 다운로드 받은 파일을 넣어줍니다.
```bash
mkdir ./plugin/coolsms
```

## Modify API Key And Secret
CoolSMS 에서 발급받은 API Key 와 API Secret 를 지정된 파일을 작성해서 서버에 업로드 합니다.
```bash
cat > ./plugin/coolsms/extend/config.json << EOF
{
  "CoolsmsApiKey": "Your API Key",
  "CoolsmsApiSecret": "Your API Secret"
}
EOF
```

# Note
Python 용으로 만들어진 플러그인입니다만, 그누보드6 이외 다른 파이썬에서 그대로 사용이 불가능할거라 생각합니다. 사용시에는 자신에게 맞도록 커스텀해서 사용하셔야합니다.
