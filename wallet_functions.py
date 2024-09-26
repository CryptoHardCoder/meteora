import asyncio
from loguru import logger

from playwright.async_api import BrowserContext, Page, expect

from functions import find_page
from setting import keyword_wallet, url_jup


async def get_balance_in_page(page: Page, step: int, token_name: str, stable_coin: str = 'USDT') -> dict:
    """
    Получает информацию о доступных балансах на странице 'meteora/dlmm'.

    Эта функция используется для извлечения информации о подсвеченных доступных балансах на странице добавления позиции или свапа.
    Значение параметра `step` определяет, как именно будут извлекаться данные, в зависимости от того,
    на какой странице вы находитесь (например, для добавления позиции или для свапа).

    Параметры:
    ----------
    page : Page
        Объект страницы Playwright, на которой будет производиться извлечение данных.

    step : int
        Значение, определяющее текущий шаг.
        - На странице добавления позиции `step` = 2.
        - На странице свапа `step` = 1.

    token_name : str
        Название токена, для которого необходимо получить информацию о балансе.

    stable_coin : str, optional
        Название стабильной монеты, по умолчанию 'USDT'. Используется для сравнения с доступными балансами.

    Returns:
    --------
    dict
        Словарь, содержащий информацию о доступных балансах, ключами которого являются названия токенов,
        а значениями - соответствующие балансы. Структура словаря зависит от значения параметра `step`.
    """

    await asyncio.sleep(1)
    lines = (await page.locator('form').nth(0).inner_text()).split('\n')
    # print(lines)
    swap_data = {
        token_name: None,
        stable_coin: None
    }
    # Проходим по строкам текста
    for i in range(len(lines) - 1):
        if 'Balance:' in lines[i]:
            balance_value = lines[i + 1].strip()
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                # Определяем актив по предыдущей строке и сохраняем баланс
                if token_name in lines[i - step]:  # Проверяем предыдущую строку
                    swap_data[token_name] = balance_value
                elif stable_coin in lines[i - step]:  # Проверяем предыдущую строку
                    swap_data[stable_coin] = balance_value
    # print(type(swap_data), swap_data)
    return swap_data


async def confirm_transaction(context: BrowserContext) -> bool:
    wallet_page: Page = await find_page('Solflare', context)

    if wallet_page is None:  # иногда не сразу появляется кошелек, для этого небольшой цикл написал
        for _ in range(3):
            await asyncio.sleep(5)
            wallet_page: Page = await find_page('Solflare', context)
            if wallet_page is not None:
                break

    if await wallet_page.locator('h3:has-text("Укажите пароль")').is_visible():
        await wallet_page.get_by_placeholder("Пароль").type(keyword_wallet)
        await wallet_page.locator('button:has-text("Разблокировать")').click()

    if (await wallet_page.locator('h4:has-text("Simulation failed")').is_visible() or
            await wallet_page.locator('h4:has-text("Slippage tolerance exceeded")').is_visible()):
        await wallet_page.locator('button:has-text("Отклонить")').click()
        logger.error('Транзакцию отклонил, не показывал что и сколько меняем')
        return False
    await expect(wallet_page.locator('button:has-text("Утвердить")')).to_be_visible()
    await wallet_page.locator('button:has-text("Утвердить")').click()

    return True


async def connect_wallet(context: BrowserContext, title_name: str = 'Solflare') -> bool:
    # print('Подключаем кошелек')
    context.expect_page()
    wallet_page: Page = await find_page(title_name, context)

    try:
        if await wallet_page.locator('button:has-text("Подключиться")').is_visible():
            # print('Без пароля коннектимся')
            await wallet_page.locator('button:has-text("Подключиться")').click(click_count=2)  # иногда с одного клика
            # не срабатывает "подключиться"
        else:
            # print('С вводом пароля коннектимся')
            solflare = wallet_page.get_by_placeholder("Пароль")
            await solflare.type(keyword_wallet)
            await wallet_page.locator('button:has-text("Разблокировать")').click()
            await expect(wallet_page.locator('button:has-text("Подключиться")')).to_be_visible()
            await wallet_page.locator('button:has-text("Подключиться")').click(click_count=2)
            # print('Успешно ввели пароль от кошелька')

    except Exception as e:
        logger.error(f'Ошибка при вводе пароля: {e}')
        return False
    return True


async def get_balance_in_wallet(page: Page, context: BrowserContext) -> dict:
    """ Функция получает баланс на странице: Jup.ag. Работает только для трех монет: SOL, USDT, JLP.
                На прямую с кошелька не берет баланс. Возвращает словарь. """
    logger.info('Получаем баланс через сайт jup.ag')

    url = page.url

    if url != url_jup:
        await page.goto(url_jup)

    if await page.get_by_role("button", name="Connect Wallet").is_visible():
        await page.locator('button:has-text("Connect Wallet")').click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context)

    await page.wait_for_load_state()
    await expect(page.get_by_alt_text('Wallet logo')).to_be_visible()
    location_menu = await page.get_by_alt_text('Wallet logo').nth(1).bounding_box()
    await page.get_by_alt_text('Wallet logo').nth(1).click()
    await page.locator('span:has-text("Your Tokens")').click()

    # путь селектора 'Your tokens' содержащий баланс
    data = (await page.locator('//*[@id="__next"]/div[2]/div[1]/div/'
                               'div[4]/div[3]/div/div[2]').inner_text()).split('\n')
    balance_wallet = {
        'SOL': None,
        'JLP': None,
        'USDT': None
    }
    for i in range(len(data) - 1):
        if 'SOL' in data[i]:
            balance_value = data[i + 1].strip().replace(',', '.')
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['SOL'] = balance_value
        if 'JLP' in data[i]:
            balance_value = data[i + 1].strip().replace(',', '.')
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['JLP'] = balance_value
        if 'USDT' in data[i]:
            balance_value = data[i + 1].strip().replace(',', '.')
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['USDT'] = balance_value
    print(balance_wallet)
    await page.mouse.click(location_menu['x'], location_menu['y'])  # нажимаем в меню чтобы скрыт вкладку
    await page.close()

    return balance_wallet
