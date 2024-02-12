from fastapi import APIRouter
from starlette.requests import Request

from core.plugin import get_admin_plugin_menus, get_all_plugin_module_names
from core.template import AdminTemplates
from lib.common import get_admin_menus, get_client_ip
from lib.template_functions import (
    get_editor_select, get_member_id_select, get_member_level_select,
    get_selected, get_skin_select, option_array_checked
)
from . import plugin_config
from ..plugin_config import module_name, admin_router_prefix

# Custom Load
from ..extend import coolsms
from ..extend.coolsms_filters import (phone_number, preg_replace)
from lib.common import nl2br
import datetime
import math
from starlette.responses import RedirectResponse
from fastapi import Depends, Form, Query, Path
from lib.dependencies import validate_token
from core.exception import AlertException
import re

templates = AdminTemplates()

templates.env.globals["admin_menus"] = get_admin_menus()
templates.env.globals["getattr"] = getattr
templates.env.globals["get_member_id_select"] = get_member_id_select
templates.env.globals["get_skin_select"] = get_skin_select
templates.env.globals["get_editor_select"] = get_editor_select
templates.env.globals["get_selected"] = get_selected
templates.env.globals["get_member_level_select"] = get_member_level_select
templates.env.globals["option_array_checked"] = option_array_checked
templates.env.globals["get_admin_plugin_menus"] = get_admin_plugin_menus
templates.env.globals["get_client_ip"] = get_client_ip
templates.env.globals["get_all_plugin_module_names"] = get_all_plugin_module_names

# Custom Filter
templates.env.filters['phone_number'] = phone_number
templates.env.filters['preg_replace'] = preg_replace
templates.env.filters['nl2br'] = nl2br

admin_router = APIRouter(prefix=admin_router_prefix, tags=['demo_admin'])


@admin_router.get('/dashboard')
async def dashboard(request: Request):
    request.session["menu_key"] = module_name
    request.session["plugin_submenu_key"] = module_name + "1"

    sms = coolsms.CoolSMS()
    now = datetime.datetime.now()
    date_start = (now - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    date_end = now.strftime('%Y-%m-%d')

    params = __get_params(request)
    sent = sms.get_sent(params)
    pagination = __pagination(sent)

    context = {
        "request": request,
        "title": f"대시보드 < {module_name}",
        "content": f"대시보드 < {module_name}",
        "module_name": module_name,

        'sms': sms,
        'now': now,

        'status': sms.get_status(),
        'infos': sms.get_data(),
        'balance': sms.get_balance(),
        'sent': sent,

        'date_start': date_start,
        'date_end': date_end,
        'pagination': pagination,

        'template_path': plugin_config.TEMPLATE_PATH
    }
    return templates.TemplateResponse(f'{plugin_config.TEMPLATE_PATH}/admin/dashboard.html', context)


@admin_router.post('/send', dependencies=[Depends(validate_token)])
async def send(
    request: Request,
    sms_from: str = Form(...),
    sms_to: str = Form(...),
    sms_datetime: str = Form(None),
    sms_text: str = Form(...)
):
    if sms_to is None or sms_text is None:
        raise AlertException('잘못된 접근입니다.', 403)

    # Send SMS
    response = coolsms.CoolSMS().send({
        'from': sms_from,
        'to': sms_to,
        'datetime': sms_datetime,
        'text': sms_text
    })
    if not response['status']:
        raise AlertException(response['message'], 403)

    return RedirectResponse('/admin/coolsms/dashboard', status_code=302)


@admin_router.post('/cancel', dependencies=[Depends(validate_token)])
async def cancel(
    request: Request,
    message_id: str = Form(None),
    group_id: str = Form(None)
):
    data = {}

    if message_id is not None:
        data['mid'] = message_id

    if group_id is not None:
        data['gid'] = group_id

    if 'mid' not in data and 'gid' not in data:
        raise AlertException('잘못된 접근입니다.', 403)

    response = coolsms.CoolSMS().cancel(data)
    if not response:
        raise AlertException('예약 발송 취소를 실패하였습니다.', 403)

    return RedirectResponse('/admin/coolsms/dashboard', status_code=302)


@admin_router.get('/error')
async def error(request: Request):
    request.session['menu_key'] = module_name
    request.session['plugin_submenu_key'] = module_name + '2'

    params = __get_params(request)
    params['notin_resultcode'] = ['00', '99', '60']
    sent = coolsms.CoolSMS().get_sent(params)
    pagination = __pagination(sent)

    context = {
        'request': request,
        'title': f'발송 에러 < {module_name}',
        'content': f'발송 에러 < {module_name}',
        'module_name': module_name,

        'params': params,
        'sent': sent,
        'pagination': pagination,

        'template_path': plugin_config.TEMPLATE_PATH
    }
    return templates.TemplateResponse(f'{plugin_config.TEMPLATE_PATH}/admin/error.html', context)


@admin_router.get('/search')
async def search(request: Request):
    request.session['menu_key'] = module_name
    request.session['plugin_submenu_key'] = module_name + '3'

    params = __get_params(request)
    sent = coolsms.CoolSMS().get_sent(params)
    pagination = __pagination(sent)

    context = {
        'request': request,
        'title': f'상태 검색 < {module_name}',
        'content': f'상태 검색 < {module_name}',
        'module_name': module_name,

        'params': params,
        'sent': sent,
        'pagination': pagination,

        'template_path': plugin_config.TEMPLATE_PATH
    }
    return templates.TemplateResponse(f'{plugin_config.TEMPLATE_PATH}/admin/search.html', context)


def __get_params(request: Request):
    page = request.query_params.get('page')
    if page is None:
        page = '1'

    sms_search_to = request.query_params.get('sms_search_to')
    if sms_search_to is None:
        sms_search_to = ''
    else:
        sms_search_to = re.sub(r'[^0-9]', r'', sms_search_to)

    sms_search_start_date = request.query_params.get('sms_search_start_date')
    if sms_search_start_date is None:
        sms_search_start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        sms_search_start_date += ' 00:00:00'

    sms_search_end_date = request.query_params.get('sms_search_end_date')
    if sms_search_end_date is None:
        sms_search_end_date = datetime.datetime.now().strftime('%Y-%m-%d 23:59:59')

    sms_search_count = request.query_params.get('sms_search_count')
    if sms_search_count is None:
        sms_search_count = '20'

    params = {
        'page': page,
        's_rcpt': sms_search_to,
        'start': sms_search_start_date,
        'end': sms_search_end_date,
        'count': sms_search_count
    }
    return params


def __pagination(sent):
    pagination = {}
    if sent['total_count'] > sent['list_count']:
        pagination['start'] = math.floor(sent['page'] / 10) * 10 + 1
        pagination['end'] = math.ceil(sent['total_count'] / sent['list_count'])
        if pagination['start'] + 9 <= pagination['end']:
            pagination['showEnd'] = pagination['start'] + 9
        else:
            pagination['showEnd'] = pagination['end']
    return pagination
