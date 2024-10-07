import asyncio
from playwright.async_api import async_playwright, Error

from functions import get_profile_data
from jupiter_swap_func import chek_balance_sol
from meteora_functions import choose_pool, chek_position, swap_in_meteora, add_position, close_position
from setting import private_key, status_check_interval, headers, logger, params


async def main():
    async with async_playwright() as p:
        profile_data = await get_profile_data(private_key=private_key)
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=1800,
                                                    headers=headers)
        context = browser.contexts[0]
        context.set_default_timeout(60000)
        page = await context.new_page()
        page.set_default_navigation_timeout(60000)
        await page.goto('https://app.meteora.ag/')

        for page in context.pages:
            if page.url == 'https://app.meteora.ag/':
                continue
            await page.close()

        # Проверка значения navigator.webdriver:
        # True -> страница видит что браузер запускается с помощью ботов,
        # False -> значит не видит, страница думает что мы человек)
        is_webdriver = await page.evaluate("navigator.webdriver")
        # print(f'navigator.webdriver: {is_webdriver}')

        await choose_pool(context)

        while await chek_position(context):
            await close_position(context)
            break

        chek_result, balance = await chek_balance_sol(page, context)
        if not chek_result:
            if params.get('token') is not None and params.get('chat_id') is not None:
                logger.log('EXCEPTION',
                           f"Критическая ошибка: недостаточно SOL ({balance['SOL']}). "
                           f"Софт будет приостановлен. Пожалуйста, пополните баланс!")
            else:
                logger.critical(f"Критическая ошибка: недостаточно SOL ({balance['SOL']}). "
                                f"Софт приостановлен. Пожалуйста, пополните баланс!")
            return

        try:
            while True:
                logger.debug('Мы в цикле')
                chek_position_result = await chek_position(context)
                if chek_position_result is None:
                    await swap_in_meteora(context)
                    try_add_position = await add_position(context)
                    if try_add_position is not None:
                        open_price, max_price, min_price = try_add_position

                else:
                    current_price = chek_position_result

                    """ниже формула = если цена пойдет в право до половины, то есть поднимется на 95%, 
                                                бот закрывает позицию """
                    target_price = open_price + 0.95 * (max_price - open_price)
                    # target_price = open_price + 0.05 * (max_price - open_price)

                    target_price = round(target_price, 4)
                    logger.info(f'Текущая цена:{current_price}')
                    # logger.info(f"Позиция закроется при превышении: {target_price} или падении ниже: {open_price}.")
                    logger.info(f"Позиция закроется при превышении: {target_price}")
                    # """ниже формула = если цена приближается к минимальной цене на 90% бот закрывает позицию"""
                    # closure_price = min_price + 0.1 * (current_price - min_price)

                    # if current_price >= target_price or current_price < open_price:
                    if current_price >= target_price:
                        logger.info("Цена вышла за диапазон. Запущен процесс закрытия позиции")
                        await close_position(context)
                        if not await chek_balance_sol(page, context):
                            if params.get('token') is not None and params.get('chat_id') is not None:
                                logger.log('EXCEPTION',
                                           f"Критическая ошибка: недостаточно SOL ({balance['SOL']}). "
                                           f"Софт будет приостановлен. Пожалуйста, пополните баланс!")
                            else:
                                logger.critical(f"Критическая ошибка: недостаточно SOL ({balance['SOL']}). "
                                                f"Софт приостановлен. Пожалуйста, пополните баланс!")
                                break

                        await swap_in_meteora(context)
                        try_add_position = await add_position(context)
                        if try_add_position is not None:
                            open_price, max_price, min_price = try_add_position
                    else:
                        logger.info(f'Цена находиться в установленном диапазоне')

                await asyncio.sleep(status_check_interval)

        except Exception as err:
            if params.get('token') is not None and params.get('chat_id') is not None:
                logger.log("EXCEPTION", f'Возникла не предвиденная ошибка. Софт приостановлен. '
                                        f'Пожалуйста сообщите разрабу!')
            else:
                logger.exception(f'Возникла не предвиденная ошибка: {err}. '
                                 f'Софт приостановлен. Пожалуйста сообщите разрабу!')
        except Error as e:
            if params.get('token') is not None and params.get('chat_id') is not None:
                logger.log("EXCEPTION",
                           f'Возникла не предвиденная ошибка. Софт приостановлен. Пожалуйста сообщите разрабу!')
            else:
                logger.exception(f'Возникла не предвиденная ошибка: {e}'
                                 f'Софт приостановлен. Пожалуйста сообщите разрабу!')


asyncio.run(main())
