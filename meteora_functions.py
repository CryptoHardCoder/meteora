import asyncio
from typing import Tuple, Dict

from playwright.async_api import BrowserContext, Page

from functions import smooth_scroll_with_mouse, find_page
from setting import usdt_swap_value_to_jlp, max_procent, min_procent
from wallet_functions import connect_wallet, get_balance_in_page, confirm_transaction


async def choose_pool(context: BrowserContext, pool_name: str = 'JLP-USDT') -> None:
    page: Page = await find_page('DLMM Pools | Meteora', context)
    await asyncio.sleep(1)
    await page.wait_for_load_state()

    if page is None:
        print('Открываем новую страницу choose_pool')
        page = await context.new_page()
        await page.goto('https://app.meteora.ag/dlmm')
        await page.wait_for_load_state()

    if await page.locator('button', has_text='Connecting...').nth(0).is_visible():
        await connect_wallet(context=context)

    elif await page.locator('button', has_text='Connect Wallet').nth(0).is_visible():
        await page.locator('button', has_text='Connect Wallet').nth(0).click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)

    await page.wait_for_load_state()
    await page.get_by_placeholder('Search by token name, symbol, mint').type(f'{pool_name}')
    await page.get_by_text(f'{pool_name}').nth(0).click()
    await smooth_scroll_with_mouse(page, 300, 100)
    await page.get_by_text(f'{pool_name}').nth(1).click()
    await page.wait_for_load_state()

    if await page.locator('button:has-text("Agree, let\'s go")').is_visible():
        await page.locator('button:has-text("Agree, let\'s go")').nth(1).click()

    return None


async def chek_position(context: BrowserContext) -> float | None:
    """ Функция проверяет на наличие открытой позиции. Если есть открытая позиция, то возвращает (float) актуальную цену.
                                        Если нет, возвращает None"""
    print('Проверка на наличие открытой позиции')
    page: Page = await find_page('JLP-USDT | Meteora', context)
    await page.wait_for_load_state()
    await asyncio.sleep(1)

    await smooth_scroll_with_mouse(page, distance=300, speed=150)

    if await page.locator('span', has_text='Not connected').is_visible():
        await page.reload()
        await page.wait_for_load_state()
        await connect_wallet(context=context)

    await page.wait_for_load_state()
    if await page.locator('span:has-text("Loading...")').is_visible():
        while await page.locator('span:has-text("Loading...")').is_visible():
            await page.reload()
            await connect_wallet(context)
            await asyncio.sleep(5)

    if await page.locator('span:has-text("No Positions Found")').is_visible():
        print('Chek_position: У вас нет открытых позиций')
        return None

    if await page.get_by_alt_text('warning').is_visible():
        print('Chek_position: На сайте увидел "WARNING". Расхождение цены очень большая')
        return None

    await page.locator('span:has-text("Your Positions")').click()
    if await page.locator('span:has-text("Price Range")').is_visible():
        print('Chek_position: У вас уже есть  открытая позиция')
        buttons = await page.locator('button').all_inner_texts()  # актуальный курс вытаскиваем
        buttons_data = list(filter(None, buttons))
        # print(buttons_data)
        button_with_price: str = buttons_data[1]
        # print(button_with_price)
        price = button_with_price.split('\n')
        # print(price)
        current_price = float(price[0])
        # print(current_price)
        return current_price


async def swap_in_meteora(context: BrowserContext) -> Dict | None:
    print('Зашли в SWAP')
    page: Page = await find_page('JLP-USDT | Meteora', context)
    await page.wait_for_load_state()

    await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/'
                       'div[2]/div[1]/div[1]/div[3]/span').click()  # xpath кнопки SWAP
    print('Проверяем баланс в SWAP вкладке')

    swap_data = await get_balance_in_page(page, 1, 'JLP')
    print(f'Баланс: USDT: {swap_data["USDT"]}, JLP: {swap_data["JLP"]}')

    if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] < 1:
        print('Свапат нечего, имеем USDT меньше одного ')
        return None

    if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] > 1:
        print(f'Свапаем все USDT в JLP')
        await page.wait_for_load_state()
        await page.get_by_role("button", name="switch").click()
        await page.get_by_text("MAX", exact=True).click()

    elif usdt_swap_value_to_jlp > swap_data['USDT']:
        print(f'Имеем меньше чем вы указали, поэтому свапаем все USDT в JLP')
        await page.wait_for_load_state()
        await page.get_by_role("button", name="switch").click()
        await page.get_by_text("MAX", exact=True).click()

    else:
        print(f'Свапаем указанное вами количество USDT: {usdt_swap_value_to_jlp}')
        await page.get_by_role("button", name="switch").click()
        await page.locator('input').nth(0).click()
        await page.locator('input').nth(0).type(str({usdt_swap_value_to_jlp}))

    await page.locator('button[type="submit"]').click()
    while not await confirm_transaction(context):
        await page.locator('button[type="submit"]').click()
        await asyncio.sleep(2)
        await confirm_transaction(context)
        print('Транзакция отклонена, через 10сек попробуем еще раз')
        await asyncio.sleep(10)
    await asyncio.sleep(10)

    return swap_data


async def add_position(context: BrowserContext) -> Tuple[float, float, float] | None:
    print('Зашли в добавление позиции')
    page: Page = await find_page('JLP-USDT | Meteora', context)
    await page.wait_for_load_state()

    if await page.get_by_alt_text('warning').is_visible():
        print('Add_position: На сайте увидел "WARNING". Расхождение цены очень большая, не будем добавлять ликвидность')
        return None

    await page.locator('span:has-text("Add Position")').click()
    add_position_balance = await get_balance_in_page(page, step=2, token_name='JLP')
    print(f'Контрольная проверка баланса: USDT: {add_position_balance["USDT"]}, JLP: {add_position_balance["JLP"]} ')

    if (add_position_balance['USDT'] and add_position_balance['JLP']) is None:
        print('Не удалось получить баланс, return')
        return None

    if 0 < add_position_balance['JLP'] < 1:
        print('Add_position: На балансе мало JLP, поэтому не будем открывать пулл')
        return None
    else:
        await page.locator(f'span:has-text("{add_position_balance["JLP"]}")').click()  # нажимает на кнопку с балансом
        # для заполнения поля

        await page.locator('button:has-text("Spot")').get_by_alt_text('Spot').click()

        if await page.locator('button:has-text("Add Liquidity")').is_disabled():
            await page.get_by_placeholder('0.00').nth(0).clear()
            await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div['
                               '2]/form/div[1]/div[1]/div/div/button').click()  # xpath кнопки Auto-fill
            await page.locator(f'span:has-text("{add_position_balance["JLP"]}")').click()  # нажимает на кнопку с
            # балансом для заполнения поля

        await page.locator('div:has-text("Min Price")').locator('input').nth(1).type(min_procent)
        print('написал мин прайс')

        await page.locator('div:has-text("Max Price")').locator('input').nth(7).type(max_procent)
        print('написал макс прайс')
        await page.locator('span:has-text("Num Bins")').click()

        buttons = await page.locator('button').all_inner_texts()  # актуальный курс вытаскиваем при открытии позиции
        buttons_data = list(filter(None, buttons))
        button_with_price: str = buttons_data[1]
        price = button_with_price.split('\n')
        open_price = float(price[0])

        input_elements = page.locator('input')  # макс и мин цену вытаскиваем при открытии позиции
        count = await input_elements.count()
        input_values = []
        for i in range(count):
            value = await input_elements.nth(i).input_value()
            input_values.append(value)
        input_data = list(filter(None, input_values))
        # print(input_data)
        min_price = float(input_data[-5])
        # print(min_price)
        max_price = float(input_data[-3])
        # print(max_price)

        await page.locator('button', has_text='Add Liquidity').click()

        while not await confirm_transaction(context):
            await page.locator('button', has_text='Add Liquidity').click()
            await asyncio.sleep(2)
            await confirm_transaction(context)
            print('Транзакция отклонена, через 10сек попробуем еще раз')
            await asyncio.sleep(10)

        print('Add_position: Ликва добавлена')

    return open_price, max_price, min_price


async def close_position(context: BrowserContext) -> bool:
    print('Зашли в закрытие позиции')
    page: Page = await find_page('JLP-USDT | Meteora', context)
    await page.wait_for_load_state()

    await page.locator('span:has-text("Your Positions")').click()
    if await page.locator('span:has-text("Price Range")').is_visible():
        await smooth_scroll_with_mouse(page, 200, 100)
        await page.locator('span:has-text("USDT per JLP")').click()
        await page.get_by_text('Withdraw').click()
        if await page.locator('button:has-text("Withdraw & Close Position")').is_enabled():
            await page.locator('button:has-text("Withdraw & Close Position")').click()
            await confirm_transaction(context)
        else:
            await page.locator('100%').click()
            await page.locator('button:has-text("Withdraw & Close Position")').click()
            await confirm_transaction(context)
        print('закрыли позицию')
        return True
    elif await page.locator('span:has-text("No Positions Found")').is_visible():
        print('Close_position: Нет открытых позиций')
    return False
