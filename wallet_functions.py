import asyncio

from playwright.async_api import BrowserContext, Page, expect, TimeoutError
from setting import keyword_wallet, url_jup, logger
from functions import find_page


async def get_balance_in_page_jlp(page: Page, step: int, token_name: str, stable_coin: str = 'USDT') -> dict:
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

    # await asyncio.sleep(1)
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


async def get_balance_in_wallet(context: BrowserContext) -> dict:
    """ Функция получает баланс на странице: Jup.ag. Работает только для трех монет: SOL, USDT, JLP.
                На прямую с кошелька не берет баланс. Возвращает словарь. """
    logger.info('Получаем баланс через сайт jup.ag')

    page: Page = await find_page(context, 'Swap | Jupiter', keyword_in_url='jup.ag')

    if page is None:
        pages = context.pages
        jup_page = None
        # Проходим по всем страницам и ищем дубликаты 'jup.ag'
        for page in pages:
            if 'jup.ag' in page.url:
                if jup_page is None:
                    # Оставляем первую найденную страницу 'jup.ag'
                    jup_page = page
                    page = jup_page
                else:
                    # Закрываем все остальные страницы с 'jup.ag' если есть такие
                    await page.close()

    if page is None or page.url != url_jup:
        page = await context.new_page()
        await page.goto(url_jup)
    await page.bring_to_front()

    connect_wallet_button = page.locator('span:has-text("Connect Wallet")').first
    # connect_wallet_button = page.locator('//*[@id="__next"]/div[2]/div[1]/div/'
    #                                      'div[4]/div[3]/button') # xpath кнопки Connect wallet
    if await connect_wallet_button.is_visible():
        location_menu = await connect_wallet_button.bounding_box()
        await connect_wallet_button.click()
    else:
        try:
            # await jup_connect_wallet(context, page=page)  # когда функция работает по xpath
            # location_menu = await get_location_menu(page=page)  # когда функция работает по xpath
            await jup_connect_wallet(context, page=page, button_index=1)  # когда функция работает по поиску лого
            location_menu = await get_location_menu(page, button_index=1)  # когда функция работает по поиску лого
        except AssertionError:
            logger.error(f'Словили ошибку: \nПробуем менять индексы')
            # await jup_connect_wallet(context, page=page)  # когда функция работает по xpath
            # location_menu = await get_location_menu(page=page)  # когда функция работает по xpath
            await jup_connect_wallet(context, page=page, button_index=0)
            location_menu = await get_location_menu(page, button_index=0)  # когда функция работает по поиску лого

    # await page.locator('span:has-text("Your Tokens")').click()
    # await page.locator('//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/'
    #                    'div/div[2]').click()  # путь селектора 'Your tokens' содержащий баланс
    # data = (await page.locator(
    #     '//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/div/div[2]'
    # ).inner_text()).split('\n')  # путь селектора 'Your tokens' содержащий баланс
    # balance_wallet = {
    #     'SOL': None,
    #     'JLP': None,
    #     'USDT': None
    # }
    # for i in range(len(data) - 1):
    #     if 'SOL' in data[i]:
    #         balance_value = data[i + 1].strip().replace(',', '.')
    #         if balance_value.replace('.', '', 1).isdigit():
    #             balance_value = float(balance_value)
    #             balance_wallet['SOL'] = balance_value
    #     if 'JLP' in data[i]:
    #         balance_value = data[i + 1].strip().replace(',', '.')
    #         if balance_value.replace('.', '', 1).isdigit():
    #             balance_value = float(balance_value)
    #             balance_wallet['JLP'] = balance_value
    #     if 'USDT' in data[i]:
    #         balance_value = data[i + 1].strip().replace(',', '.')
    #         if balance_value.replace('.', '', 1).isdigit():
    #             balance_value = float(balance_value)
    #             balance_wallet['USDT'] = balance_value

    # data = (await page.locator(
        # '//*[@id="__next"]/div[2]/div[1]/div[2]/div[2]/div/div[2]/div/div[1]/div').inner_text()).split('\n')
    data = (await page.locator('//*[@id="__next"]/div[2]/div[1]/div[2]/div[2]/'
                               'div/div[3]/div/div[1]/div/div[3]').inner_text()).split('\n')
    # print(data)
    data = [item for item in data if item]

    balance_wallet = {
        'SOL': None,
        'JLP': None,
        'USDT': None
    }

    for i in range(len(data) - 1):
        if 'Solana' in data[i]:
            balance_value = data[i + 1].strip().replace('SOL', '').replace(',', '.').strip()
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['SOL'] = balance_value

        if 'USDT' in data[i]:
            balance_value = data[i + 1].strip().replace('USDT', '').replace(',', '.').strip()
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['USDT'] = balance_value

        if 'Jupiter Perps' in data[i]:
            balance_value = data[i + 1].strip().replace('JLP', '').replace(',', '.').strip()
            if balance_value.replace('.', '', 1).isdigit():
                balance_value = float(balance_value)
                balance_wallet['JLP'] = balance_value

    # print(balance_wallet)
    logger.info(f'Баланс составляет: {balance_wallet}')
    await page.mouse.click(location_menu['x'], location_menu['y'])  # нажимаем в меню чтобы скрыт вкладку
    # await page.close()

    return balance_wallet


async def confirm_transaction(context: BrowserContext, keyword_in_url: str = 'chrome-extension://') -> bool:
    # await asyncio.sleep(2)
    wallet_page: Page = await find_page(context, 'Solflare', keyword_in_url=keyword_in_url)

    if wallet_page is None:  # иногда не сразу появляется кошелек, для этого небольшой цикл написал
        for _ in range(3):
            wallet_page: Page = await find_page(context, 'Solflare', keyword_in_url=keyword_in_url)
            await asyncio.sleep(5)
            if wallet_page is not None:
                break
    await wallet_page.bring_to_front()

    if await wallet_page.locator('h4:has-text("Укажите пароль")').is_visible():
        await wallet_page.get_by_placeholder("Пароль").type(keyword_wallet)
        await wallet_page.locator('button:has-text("Разблокировать")').click()

    # cancel_button = wallet_page.locator('button:has-text("Отклонить")')
    submit_button = wallet_page.locator('button:has-text("Утвердить")')

    if (
            await wallet_page.locator('h5:has-text("Simulation failed")').is_visible() or
            await wallet_page.locator('h5:has-text("Slippage tolerance exceeded")').is_visible()
    ):
        await wallet_page.close()
        # await cancel_button.click()
        logger.error('Транзакцию отклонена. Причина: не удалось получить симуляцию, пробуем через 10сек')
        return False

    try:
        await expect(submit_button).to_be_enabled()
        await submit_button.click()
        logger.info('Транзакция подтверждена')
        return True
    except AssertionError:
        # await wallet_page.locator('button:has-text("Отклонить")').click()
        logger.exception(f'Транзакцию отклонена. Причина: кнопка "Утвердить" была не доступна ')
        await wallet_page.close()
    except TimeoutError:
        logger.exception(f'Транзакцию отклонена. Причина: кнопка "Утвердить" была не доступна ')
        await wallet_page.close()
        return False


async def connect_wallet(context: BrowserContext, title_name: str = 'Solflare',
                         keyword_in_url: str = 'chrome-extension://') -> bool:
    # await asyncio.sleep(2)
    wallet_page: Page = await find_page(context, title_name=title_name, keyword_in_url=keyword_in_url)
    await wallet_page.bring_to_front()

    try:
        if await wallet_page.locator('button:has-text("Подключиться")').is_visible():
            await wallet_page.locator('button:has-text("Подключиться")').click(click_count=2)  # иногда с одного клика
            # не срабатывает "подключиться"
        else:
            await wallet_page.get_by_placeholder("Пароль").type(keyword_wallet)
            await wallet_page.locator('button:has-text("Разблокировать")').click()
            await expect(wallet_page.locator('button:has-text("Подключиться")')).to_be_visible()
            await wallet_page.locator('button:has-text("Подключиться")').click(click_count=2)

    except Exception as e:
        logger.error(f'Ошибка при вводе пароля: {e}')
        return False
    return True


async def jup_connect_wallet(context, page: Page, button_index: int):
    if await page.locator('button:has-text("Connect Wallet")').nth(button_index).is_visible():
        await page.locator('button:has-text("Connect Wallet")').nth(button_index).click()
        await page.locator('span:has-text("Solflare")').click(click_count=2)
        await connect_wallet(context)


async def get_location_menu(page: Page, button_index: int):
    if await page.get_by_alt_text('Wallet logo').nth(button_index).is_visible():
        location_menu = await page.get_by_alt_text('Wallet logo').nth(button_index).bounding_box()
        await page.get_by_alt_text('Wallet logo').nth(button_index).click()
    else:
        await expect(page.get_by_alt_text('Wallet logo').nth(button_index)).to_be_visible()
        location_menu = await page.get_by_alt_text('Wallet logo').nth(button_index).bounding_box()
        await page.get_by_alt_text('Wallet logo').nth(button_index).click()

    return location_menu

#
# async def confirm_transaction(context: BrowserContext, keyword_in_url: str = 'chrome-extension://') -> bool:
#     # await asyncio.sleep(2)
#     wallet_page: Page = await find_page(context, 'Solflare', keyword_in_url=keyword_in_url)
#
#     if wallet_page is None:  # иногда не сразу появляется кошелек, для этого небольшой цикл написал
#         for _ in range(3):
#             wallet_page: Page = await find_page(context, 'Solflare', keyword_in_url=keyword_in_url)
#             await asyncio.sleep(5)
#             if wallet_page is not None:
#                 break
#     await wallet_page.wait_for_load_state('domcontentloaded')
#     await wallet_page.bring_to_front()
#
#     if await wallet_page.locator('//*[@id="radix-:r0:"]/div/div/div/div[1]/form/div/div/input').is_visible():  # поля ввода пароля
#         await wallet_page.locator('//*[@id="radix-:r0:"]/div/div/div/div[1]/form/div/div/input').type(keyword_wallet)  # поля ввода пароля
#         await wallet_page.locator('//*[@id="radix-:ra:"]/div/div/div/div[1]/form/button').click()  # кнопка разблокировки кошелька
#
#     # cancel_button = wallet_page.locator('button:has-text("Отклонить")')
#     submit_button = wallet_page.locator('/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]')  # кнопка подтверждения транзы
#
#     await wallet_page.wait_for_load_state('domcontentloaded')
#
#     if (
#             await wallet_page.locator('h5:has-text("Simulation failed")').is_visible() or
#             await wallet_page.locator('h5:has-text("Slippage tolerance exceeded")').is_visible()
#     ):
#         await wallet_page.close()
#         # await cancel_button.click()
#         logger.error('Транзакцию отклонена. Причина: не удалось получить симуляцию, пробуем через 10сек')
#         return False
#
#     try:
#         await expect(submit_button).to_be_enabled()
#         await submit_button.click()
#         logger.info('Транзакция подтверждена')
#         return True
#     except AssertionError:
#         # await wallet_page.locator('button:has-text("Отклонить")').click()
#         logger.error(f'Транзакцию отклонена. Причина: кнопка "Утвердить" была не доступна ')
#         # await expect(cancel_button).to_be_enabled(timeout=20000)
#         # await cancel_button.click()
#         await wallet_page.close()
#         return False

#
# async def connect_wallet(context: BrowserContext, title_name: str = 'Solflare',
#                          keyword_in_url: str = 'chrome-extension://') -> bool:
#     # await asyncio.sleep(2)
#     wallet_page: Page = await find_page(context, title_name=title_name, keyword_in_url=keyword_in_url)
#     await wallet_page.wait_for_load_state('domcontentloaded')
#     await wallet_page.bring_to_front()
#
#     try:
#         if await wallet_page.locator('/html/body/div[2]/div[2]/div/div[3]/div/button[2]').is_visible():  # кнопка подлючиться
#             await wallet_page.locator('/html/body/div[2]/div[2]/div/div[3]/div/button[2]').click(click_count=2)  # иногда с одного клика
#             # не срабатывает "подключиться"
#         else:
#             await wallet_page.locator('//*[@id="radix-:r0:"]/div/div/div/div[1]/form/div/div/input').type(keyword_wallet)  # поля ввода пароля
#             await wallet_page.locator('//*[@id="radix-:ra:"]/div/div/div/div[1]/form/button').click()  # кнопка разблокировки кошелька
#             await expect(wallet_page.locator('/html/body/div[2]/div[2]/div/div[3]/div/button[2]')).to_be_visible()  # кнопка подлючиться
#             await wallet_page.locator('/html/body/div[2]/div[2]/div/div[3]/div/button[2])').click(click_count=2)  # кнопка подлючиться
#
#     except Exception as e:
#         logger.error(f'Ошибка при вводе пароля: {e}')
#         return False
#     return True


#
# async def jup_connect_wallet(context, page: Page):
#     # if await page.locator('//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/div/button[2]').is_visible():
#     await page.locator('//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/div/button[2]').click()
#     await page.locator('span:has-text("Solflare")').click(click_count=2)
#     await connect_wallet(context)
#
#
# async def get_location_menu(page: Page):
#     location_menu = await page.locator(
#         '//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/button/div[3]').bounding_box()  # xpath лого кошелька
#     await page.locator('//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/button/div[3]').click()  # xpath лого кошелька
#
#     return location_menu
