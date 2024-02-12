import os

# module_name 는 플러그인의 폴더 이름입니다.
module_name = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
# 라우터 접두사는 /로 시작합니다. 붙이지 않을 때는 "" 빈문자열로 지정해야합니다.
router_prefix = '/coolsms'
admin_router_prefix = router_prefix

TEMPLATE_PATH = f'{module_name}/templates'

# 관리자 메뉴를 설정합니다.
admin_menu = {
    f'{module_name}': [
        {
            'name': 'CoolSMS',
            'url': '',
            'tag': '',
        },
        {
            'id': module_name + '1',
            'name': '대시보드',
            'url': f'{admin_router_prefix}/dashboard',
            'tag': 'dashboard',
        },
        {
            'id': module_name + '2',
            'name': '발송 에러',
            'url': f'{admin_router_prefix}/error',
            'tag': 'error',
        },
        {
            'id': module_name + '3',
            'name': '상태 검색',
            'url': f'{admin_router_prefix}/search',
            'tag': 'search'
        }
    ]
}
