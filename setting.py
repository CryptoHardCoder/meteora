from loguru import logger
from notifiers.logging import NotificationHandler

from fake_useragent import FakeUserAgent


adspower_api_url = "скопированный url сюда вставляем/api/v1/browser/start"

adspower_api_key = "ваш API KEY от ADSPOWER"

private_key = "ваш Private Key от ПРОФИЛЯ "

keyword_wallet = 'пароль от кошелька'

usdt_swap_value_to_sol: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение

usdt_swap_value_to_jlp: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение

status_check_interval: int = 10

max_procent = '2.75'  # максимальный процент при открытии позиции

min_procent = '0'  # минимальный процент при открытии позиции

default_swap_value_for_sol = 5
headers = {
    'user-agent': FakeUserAgent().random
}
url_jup = 'https://jup.ag/'

page_jlp = 'https://app.meteora.ag/dlmm/C1e2EkjmKBqx8LPYr2Moyjyvba4Kxkrkrcy5KuTEYKRH'

logger.level('POSITION', no=55, color='<green><bold>')
logger.level('CLOSE_POSITION', no=60, color='<blue><bold>')
logger.level('EXCEPTION', no=65, color='<red><bold>')

logger.add('positions_history', level='POSITION')
logger.add('logs.log', rotation='7 day', level='INFO')

params = {
    'token': None,
    'chat_id': None
}

tg_handler = NotificationHandler(provider='telegram', defaults=params)

logger.add(tg_handler, level='EXCEPTION')

