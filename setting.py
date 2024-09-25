import random
from loguru import logger

from fake_useragent import FakeUserAgent


adspower_api_url = "скопированный url сюда вставляем/api/v1/browser/start"

adspower_api_key = "ваш API KEY от ADSPOWER"

private_key = "ваш Private Key от ПРОФИЛЯ "

keyword_wallet = 'пароль от кошелька'


usdt_swap_value_to_sol: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение

usdt_swap_value_to_jlp: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение

status_check_interval: int = 60

max_procent = '2.75'  # максимальный процент при открытии позиции

min_procent = '0'  # минимальный процент при открытии позиции

default_swap_value_for_sol = random.randint(1, 5)
headers = {
    'user-agent': FakeUserAgent().random
}
url_jup = 'https://jup.ag/'

logger.add('logs.log', rotation='1 day', level='INFO')


