import asyncio
from playwright.async_api import async_playwright, Error, BrowserContext, Page

from functions import get_profile_data
from jupiter_swap_func import chek_balance_sol
from meteora_functions import choose_pool, chek_position, add_position, close_position
from setting import private_key, status_check_interval, headers, logger, params

from functions import smooth_scroll_with_mouse, find_page
from setting import usdt_swap_value_to_jlp, max_procent, min_procent, logger, params
from wallet_functions import connect_wallet, get_balance_in_page_jlp, confirm_transaction


async def swap_in_meteora(context: BrowserContext, jlp_to_usdt: int = None) -> dict | None:
    # page: Page = context.pages[-1]
    page: Page = await find_page(context, title_name='JLP-USDT | Meteora', keyword_in_url='dlmm')
    await page.wait_for_load_state('domcontentloaded')
    await page.bring_to_front()

    if await page.locator('button:has-text("Refresh")').is_visible():
        await page.locator('button:has-text("Refresh")').click()

    # if page.url != page_jlp:
    #     await page.goto(page_jlp)
    if await page.locator('span:has-text("Connect Wallet")').nth(0).is_visible():
        await page.locator('span:has-text("Connect Wallet")').nth(0).click()
        await page.locator('button:has-text("Solflare")').click()
        await connect_wallet(context=context)

    await page.locator('//*[@id="__next"]/div[1]/div[3]/div/div[2]/div/div[2]/'
                       'div[2]/div[1]/div[1]/div[3]/span').click()  # xpath кнопки SWAP
    await page.locator('button:has-text("Swap")').nth(0).scroll_into_view_if_needed()

    first_input_place = page.locator('input').nth(0)

    swap_data = await get_balance_in_page_jlp(page, 1, 'JLP')
    logger.info(f'Баланс: USDT: {swap_data["USDT"]}, JLP: {swap_data["JLP"]}')

    # print(await page.locator('form').nth(0).inner_text())
    tokens = await page.locator('form').nth(1).inner_text()
    tokens_list = tokens.split('\n')
    print(tokens_list, tokens_list[0])
    print('-------------------------------------')

    switch_button = page.get_by_role("button", name="switch")
    swap_button = page.locator('button[type="submit"]')
    tokens = await page.locator('form').nth(0).inner_text()
    tokens_list = tokens.split('\n')
    print(tokens_list, tokens_list[0])
    # print(await page.locator('form').nth(1).inner_text())
    print('-------------------------------------')

    # if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] < 1:
    #     logger.info(f"Мало USDT для свапа: {swap_data['USDT']}. Нужно больше 1 USDT.")
    #     return None

    if usdt_swap_value_to_jlp == 0 and swap_data['USDT'] > 1:
        logger.info("Количество USDT не указано. Свапаем весь доступный USDT в JLP.")
        await page.wait_for_load_state('domcontentloaded')
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            print('if не зашли')
            await switch_button.click()
        await page.get_by_text("MAX", exact=True).click()
        await swap_button.click()

    elif usdt_swap_value_to_jlp > swap_data['USDT']:
        logger.info(f"Баланс USDT ({swap_data['USDT']}) меньше указанного вами порога. Свапаем весь USDT в JLP.")
        await page.wait_for_load_state('domcontentloaded')
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            print('elif не зашли')
            await switch_button.click()
        tokens = await page.locator('form').nth(0).inner_text()
        tokens_list = tokens.split('\n')
        if tokens_list[0] != 'USDT':
            await switch_button.click()
        await page.get_by_text("MAX", exact=True).click()
        await switch_button.click()

    else:
        logger.info(f'Свапаем указанное вами количество USDT: {usdt_swap_value_to_jlp} в JLP')
        await switch_button.click()
        info_tokens = await page.locator('form').nth(0).inner_text()
        positions_tokens = info_tokens.split('\n')
        if positions_tokens[0] != 'USDT':
            print('else не зашли')

            await switch_button.click()
        await first_input_place.click()
        await first_input_place.type(str({usdt_swap_value_to_jlp}))
        await swap_button.click()
    print('finish')

    while not await confirm_transaction(context):
        logger.error('Через 10сек попробуем еще раз')
        await asyncio.sleep(10)
        await first_input_place.click()
        await first_input_place.type(str({usdt_swap_value_to_jlp}))
        await swap_button.click()
        await page.wait_for_timeout(2000)
        # await expect(page).to_have_title('Solflare')
        if await confirm_transaction(context):
            logger.debug('swap_in_meteora in else break')
            break

    await asyncio.sleep(10)  # ждем подгрузки данных, долго подгружаются

    return swap_data


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
        await swap_in_meteora(context)

asyncio.run(main())


