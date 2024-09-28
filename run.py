import asyncio

from functions import get_profile_data
from jupiter_swap_func import chek_balance_sol
from meteora_functions import choose_pool, chek_position, swap_in_meteora, add_position, close_position
from playwright.async_api import async_playwright
from setting import private_key, status_check_interval, headers, logger


async def main():
    async with async_playwright() as p:

        profile_data = await get_profile_data(private_key=private_key)
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=1500,
                                                    headers=headers)
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://meteora.ag/', timeout=60000)

        # Проверка значения navigator.webdriver:
        # True -> страница видит что браузер запускается с помощью ботов,
        # False -> значит не видит, страница думает что мы человек)
        is_webdriver = await page.evaluate("navigator.webdriver")
        # print(f'navigator.webdriver: {is_webdriver}')

        await page.get_by_text('Launch App').nth(0).click()

        await choose_pool(context)

        if await chek_position(context) is not None:
            logger.info('Вижу до запуска софта открытую позицию, закрываю, так как у меня мало информации о ней')
            await close_position(context)
            await asyncio.sleep(30)  # долго подгружаются данные после открытия и закрытия позиций
        else:
            chek_result, balance = await chek_balance_sol(page, context)
            if not chek_result:
                logger.critical(f'Выключаемся. На балансе мало SOL: {balance["SOL"]}, пожалуйста пополните баланс')
                return

        while True:
            logger.debug('Мы в цикле')
            chek_position_result = await chek_position(context)
            if chek_position_result is None:
                await swap_in_meteora(context)
                try_add_position = await add_position(context)
                if try_add_position is not None:
                    open_price, max_price, min_price = try_add_position
                    await page.wait_for_timeout(20000)  # для загрузки сайта после добавления первой ликвы

            else:
                current_price = chek_position_result

                """ниже формула = если цена пойдет в право до половины, то есть поднимется на 95%, 
                                            бот закрывает позицию """
                target_price = open_price + 0.95 * (max_price - open_price)

                # """ниже формула = если цена приближается к минимальной цене на 90% бот закрывает позицию"""
                # closure_price = min_price + 0.1 * (current_price - min_price)

                if current_price >= target_price or current_price < open_price:
                    logger.info(f'Цена вышла за рамки нашего диапозона:Цена открытия: {open_price},'
                                f'Текущая цена: {current_price}')
                    await close_position(context)
                    await asyncio.sleep(20)  # для подгрузки данных страницы после закрытия позиции
                    if not await chek_balance_sol(page, context):
                        logger.warning('Пополните баланс SOL, а мы выключаемся')
                        break
                    await swap_in_meteora(context)
                    try_add_position = await add_position(context)
                    if try_add_position is not None:
                        open_price, max_price, min_price = try_add_position
                else:
                    logger.info('Цена в нашем диапазоне')

            await asyncio.sleep(status_check_interval)


asyncio.run(main())
