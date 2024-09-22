from playwright.async_api import async_playwright
import asyncio

from typing import Dict

from functions import get_profile_data, smooth_scroll_with_mouse
from jupiter_swap_func import swap_usdt_to_sol
from meteora_functions import choose_pool, chek_position, swap_in_meteora, add_position, close_position
from setting import private_key, status_check_interval, headers, url_jup

from wallet_functions import get_balance_in_wallet


async def main():
    async with async_playwright() as p:

        profile_data = await get_profile_data(private_key=private_key)
        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=1000,
                                                    headers=headers)
        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://meteora.ag/', timeout=60000)
        # Проверка значения navigator.webdriver:
        # True -> страница видит что браузер запускается с помощью ботов,
        # False -> значит не видит, страница думает что мы человек)
        is_webdriver = await page.evaluate("navigator.webdriver")
        print(f'navigator.webdriver: {is_webdriver}')
        await asyncio.sleep(1)

        await smooth_scroll_with_mouse(page, distance=1000, speed=170)
        await page.get_by_text('Try this now').nth(0).click()
        await page.close()

        await choose_pool(context)

        while True:
            chek_position_result = await chek_position(context)
            if chek_position_result is None:
                await swap_in_meteora(context)
                try_add_position = await add_position(context)
                if try_add_position is not None:
                    open_price, max_price, min_price = try_add_position
                    await asyncio.sleep(30)  # для загрузки сайта после добавления первой ликвы
            else:
                current_price = chek_position_result

                """ниже формула = если цена пойдет в право до половины, то есть поднимется на 95%, 
                                            бот закрывает позицию """
                target_price = open_price + 0.95 * (max_price - open_price)

                # """ниже формула = если цена приближается к минимальной цене на 90% бот закрывает позицию"""
                # closure_price = min_price + 0.1 * (current_price - min_price)

                if current_price >= target_price or current_price <= open_price:
                    print('Цена вышла за рамки нашего диапозона')
                    await close_position(context)
                    await asyncio.sleep(20)  # для подгрузки страницы после закрытия позиции
                    balance: Dict = await get_balance_in_wallet(page, context)

                    """Sol при открытии позиции изымается залоговая сумма в размере 0.06 SOl(при закрытии позиции 
                    возвращается), остальные на оплату газа нужны, а меньше 5 USDT нет смысла ходит свапат"""

                    if balance['SOL'] < 0.09 and balance['USDT'] > 5:
                        success = await swap_usdt_to_sol(page, context)  # Сохраняем результат
                        if not success:  # Если результат False, выходим из цикла
                            print(
                                'Недостаточно средств для дальнейших действий, пожалуйста пополните баланс SOL или USDT')
                            break
                    await swap_in_meteora(context)
                    try_add_position = await add_position(context)
                    if try_add_position is not None:
                        open_price, max_price, min_price = try_add_position
                    # open_price, max_price, min_price = await add_position(context)
                else:
                    print('Цена в нашем диапазоне')

            await asyncio.sleep(status_check_interval)


asyncio.run(main())
