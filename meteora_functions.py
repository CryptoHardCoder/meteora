import asyncio
from playwright.async_api import BrowserContext, Page

from functions import smooth_scroll_with_mouse, find_page
from setting import usdt_swap_value_to_jlp, max_procent, logger, params, min_procent
from wallet_functions import connect_wallet, get_balance_in_page_jlp, confirm_transaction


async def choose_pool(context: BrowserContext, pool_name: str = 'JLP-USDT') -> None:
    # page: Page = context.pages[-1]
    page: Page = await find_page(context, title_name='Home | Meteora')
    await page.bring_to_front()

    if await page.locator('a:has-text("DLMM")').is_visible():
        await page.locator('a:has-text("DLMM")').click()

    if await page.get_by_alt_text('menu').is_visible():
        await page.get_by_alt_text('menu').click()
        if await page.locator('span:has-text("DLMM")').is_visible():
            await page.locator('span:has-text("DLMM")').click()
        else:
            await page.get_by_alt_text('menu').click()

    if await page.locator('button:has-text("Refresh")').is_visible():
        await page.locator('button:has-text("Refresh")').click()

    await page.get_by_placeholder('Search by token name, symbol, mint').type(f'{pool_name}')
    await page.get_by_text(f'{pool_name}').nth(0).click()
    await smooth_scroll_with_mouse(page, 300, 100)
    # await page.get_by_text(f'{pool_name}').nth(1).click()
    try:
        await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div[2]/'
                           'div/div[4]/div/div[1]/div/div/div/div[2]/div[2]/a[1]').click()
    except TimeoutError:
        await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div[2]'
                           '/div/div[4]/div/div[1]/div/div/div/div[2]/div[2]/a[1]').click()

    if await page.locator('button:has-text("Agree, let\'s go")').nth(1).is_visible():
        await page.locator('button:has-text("Agree, let\'s go")').nth(1).click()

    return None


async def chek_position(context: BrowserContext) -> float | None:
    """ Функция проверяет на наличие открытой позиции. Если есть открытая позиция, то возвращает (float) актуальную цену.
                                        Если нет, возвращает None"""
    logger.info('Проверка на наличие открытой позиции')

    page: Page = await find_page(context, title_name='JLP-USDT|Meteora', keyword_in_url='dlmm')
    await page.bring_to_front()

    if await page.locator('button:has-text("Go Back")').is_visible():
        await page.locator('button:has-text("Go Back")').click()
        # logger.info('Открытая позиция не обнаружена')

    if await page.locator('button:has-text("Refresh")').is_visible():
        await page.locator('button:has-text("Refresh")').click()

    if await page.get_by_alt_text('warning').is_visible():
        logger.warning('На сайте увидел "WARNING". Расхождение цены очень большая. Ждем 2 минуты')
        await asyncio.sleep(120)
        return None

    if await page.locator('button', has_text='Connecting...').nth(0).is_visible():
        await connect_wallet(context=context)

    elif await page.locator('button', has_text='Connect Wallet').nth(0).is_visible():
        await page.locator('button', has_text='Connect Wallet').nth(0).click(click_count=2)
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)

    await page.locator('span:has-text("Your Positions")').nth(0).click()

    if await page.locator('span:has-text("No Positions Found")').is_visible():
        logger.info("Открытых позиций не обнаружено.")
        return None

    if await page.locator('span:has-text("USDT per JLP")').is_visible():
        await page.locator('span:has-text("USDT per JLP")').scroll_into_view_if_needed()
        logger.info('Найдена открытая позиция')
        buttons = await page.locator('button').all_inner_texts()  # актуальный курс вытаскиваем
        # spans = await page.locator('span').all_inner_texts()  # рейдж цены открытой позиции
        buttons_data = list(filter(None, buttons))
        button_with_price: str = buttons_data[1]
        price = button_with_price.split('\n')
        current_price = float(price[0])

        return current_price


async def swap_in_meteora(context: BrowserContext) -> dict | None:
    # page: Page = context.pages[-1]
    page: Page = await find_page(context, title_name='JLP-USDT | Meteora', keyword_in_url='dlmm')
    await page.bring_to_front()

    # if page.url != page_jlp:
    #     await page.goto(page_jlp)
    if await page.locator('span:has-text("Connect Wallet")').nth(0).is_visible():
        await page.locator('span:has-text("Connect Wallet")').nth(0).click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)

    await page.locator('span:has-text("Swap")').nth(0).click()
    await page.locator('button:has-text("Swap")').nth(0).scroll_into_view_if_needed()

    first_input_place = page.locator('input').nth(0)

    swap_data = await get_balance_in_page_jlp(page, 1, 'JLP')
    logger.info(f'Баланс: USDT: {swap_data["USDT"]}, JLP: {swap_data["JLP"]}')

    switch_button = page.get_by_role("button", name="switch")
    swap_button = page.locator('button[type="submit"]')

    if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] < 1:
        logger.info(f"Мало USDT для свапа: {swap_data['USDT']}. Нужно больше 1 USDT.")
        return None

    if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] > 1:
        logger.info("Количество USDT не указано. Свапаем весь доступный USDT в JLP.")
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            await switch_button.click()
        await page.get_by_text("MAX", exact=True).click()
        await swap_button.click()

    elif usdt_swap_value_to_jlp > swap_data['USDT']:
        logger.info(f"Баланс USDT ({swap_data['USDT']}) меньше указанного вами порога. Свапаем весь USDT в JLP.")
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            await switch_button.click()
        await page.get_by_text("MAX", exact=True).click()
        await switch_button.click()

    else:
        logger.info(f'Свапаем указанное вами количество USDT: {usdt_swap_value_to_jlp} в JLP')
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            await switch_button.click()
        await first_input_place.click()
        await first_input_place.type(str({usdt_swap_value_to_jlp}))
        await swap_button.click()

    while not await confirm_transaction(context):
        logger.error('Через 10сек попробуем еще раз')
        await asyncio.sleep(10)
        await first_input_place.click()
        await first_input_place.type(str({usdt_swap_value_to_jlp}))
        await swap_button.click()
        await page.wait_for_timeout(2000)
        if await confirm_transaction(context):
            break

    await asyncio.sleep(10)  # ждем подгрузки данных, долго подгружаются

    return swap_data


async def add_position(context: BrowserContext) -> tuple[float, float, float] | None:
    logger.info("Начали этап добавления позиции.")

    # page: Page = context.pages[-1]
    #
    # try:
    #     page: Page = context.pages[-1]
    # except IndexError:
    page: Page = await find_page(context, title_name='JLP-USDT | Meteora', keyword_in_url='dlmm')
    await page.bring_to_front()

    if await page.locator('button:has-text("Wallet not connect")').nth(0).is_visible():
        await page.locator('span:has-text("Connect Wallet")').nth(0).click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)
    elif await page.locator('span:has-text("Connect Wallet")').nth(0).is_visible():
        await page.locator('span:has-text("Connect Wallet")').nth(0).click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)

    if await page.locator('button:has-text("Refresh")').is_visible():
        await page.locator('button:has-text("Refresh")').click()

    # if await page.locator('span:has-text("Loading...")').is_visible():
    #     while await page.locator('span:has-text("Loading...")').is_visible():
    #         await page.reload()
    #         await connect_wallet(context)
    #         await asyncio.sleep(5)

    if await page.get_by_alt_text('warning').is_visible():
        logger.warning('Обнаружено предупреждение на сайте: "WARNING". '
                       'Раскорреляция цен слишком велика, добавление ликвидности отменено.')
        return None

    await page.locator('span:has-text("Add Position")').click()
    add_position_balance = await get_balance_in_page_jlp(page, step=2, token_name='JLP')
    logger.info(
        f'Контрольная проверка баланса: USDT: {add_position_balance["USDT"]}, JLP: {add_position_balance["JLP"]}')

    if (add_position_balance['USDT'] and add_position_balance['JLP']) is None:
        logger.error('Не удалось получить баланс')
        return None

    if 0 < add_position_balance['JLP'] < 1:
        logger.info('На балансе мало JLP, поэтому не будем открывать пулл')
        return None
    else:
        await page.locator(f'span:has-text("{add_position_balance["JLP"]}")').click()  # нажимает на кнопку
        # с балансом для заполнения поля
        await page.locator('button:has-text("Spot")').get_by_alt_text('Spot').click()

        add_luquidity_button = page.locator('button:has-text("Add Liquidity")')

        if await add_luquidity_button.is_disabled():
            await page.get_by_placeholder('0.00').nth(0).scroll_into_view_if_needed()
            await page.get_by_placeholder('0.00').nth(0).clear()
            if await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/div[2]/div[2]/form/div['
                                  '1]/div[1]/div/div/button').is_visible():
                await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/div[2]'
                                   '/div[2]/form/div[1]/div[1]/div/div/button').click()
            else:
                await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]'
                                   '/div[2]/form/div[1]/div[1]/div/div/button').click()
            # await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/'
            #                    'div[2]/form/div[1]/div[1]/div/div/button/div').click()

            # await page.("button + span:has-text('Auto-Fill')").click(click_count=2)
            # await page.locator("button + span:has-text('Auto-Fill')").click(click_count=2)
            # await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]'
            # '/div[2]/form/div[1]/div[1]/div/div').click(click_count=2)
            # await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/'
            #                    'div[2]/form/div[1]/div[1]/div/div/button').click(click_count=2)  # xpath кнопки Auto-fill
            await page.locator(f'span:has-text("{add_position_balance["JLP"]}")').click()  # нажимает на кнопку с
            # балансом для заполнения поля
            await add_luquidity_button.scroll_into_view_if_needed()

        await page.locator('div:has-text("Min Price")').locator('input').nth(1).type(min_procent)

        await page.locator('div:has-text("Max Price")').locator('input').nth(7).type(max_procent)
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

        await add_luquidity_button.click()

        while not await confirm_transaction(context):
            logger.error('Через 10сек попробуем еще раз')
            await asyncio.sleep(10)
            if await page.get_by_role('alert').nth(0).is_visible():
                if await confirm_transaction(context):
                    break
            else:
                await add_luquidity_button.click()
                if await confirm_transaction(context):
                    break

        # logger.info(f'Ликвидность добавлена в рейндже {min_price} - {max_price}')
        logger.log("POSITION", f'Ликвидность добавлена в рейндже {min_price} - {max_price}')
        await page.wait_for_timeout(30000)  # для подгрузки данных о добавленнной позиции
    return open_price, max_price, min_price


async def close_position(context: BrowserContext) -> bool:
    logger.info('Начали этап закрытия позиции')
    # page: Page = context.pages[-1]
    page: Page = await find_page(context, title_name='JLP-USDT | Meteora', keyword_in_url='dlmm')
    await page.bring_to_front()

    if await page.locator('button:has-text("Refresh")').is_visible():
        await page.locator('button:has-text("Refresh")').click()

    await page.locator('span:has-text("Your Positions")').click()
    if await page.locator('span:has-text("USDT per JLP")').nth(0).is_visible():
        await page.locator('span:has-text("USDT per JLP")').nth(0).click()
        await page.get_by_text('Withdraw', exact=True).click()
        close_position_button = page.locator('button:has-text("Withdraw & Close Position")')
        await close_position_button.scroll_into_view_if_needed()
        if await close_position_button.is_enabled():
            await close_position_button.click()

        else:
            await page.locator('100%').click()
            await close_position_button.click()

        while not await confirm_transaction(context):
            logger.error('Через 10сек попробуем еще раз')
            await asyncio.sleep(10)
            await page.get_by_text('Withdraw', exact=True).click()
            if await page.get_by_role('alert').nth(0).is_visible():
                if await confirm_transaction(context):
                    break
            else:
                await close_position_button.click()
                if await confirm_transaction(context):
                    break

        await page.wait_for_timeout(30000)  # для подгрузки данных страницы после закрытия позиции и
        # ждем возврата залоговый 0.056 SOL
        # logger.info('Позиция закрыта')
        logger.log('CLOSE_POSITION', 'Предыдущая позиция закрыта')
        return True
    elif await page.locator('span:has-text("No Positions Found")').is_visible():
        logger.info("Открытых позиций не обнаружено.")
        return False
