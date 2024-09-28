import asyncio

from playwright.async_api import BrowserContext, Page
from setting import url_jup, usdt_swap_value_to_sol, default_swap_value_for_sol, logger
from wallet_functions import connect_wallet, confirm_transaction, get_balance_in_wallet
from functions import find_page


async def swap_in_jupiter(context: BrowserContext, usdt: bool = False, jlp: bool = False) -> bool:
    page: Page = await find_page(context, 'Swap | Jupiter')
    if page is None or page.url != url_jup:
        page = await context.new_page()
        await page.goto(url_jup)
    try:
        if await page.locator('button:has-text("Connect Wallet")').nth(0).is_visible():
            await page.locator('button:has-text("Connect Wallet")').nth(0).click()
            await page.locator('span:has-text("Solflare")').click(click_count=2)
            await connect_wallet(context)
    except AssertionError:
        if await page.locator('button:has-text("Connect Wallet")').nth(1).is_visible():
            await page.locator('button:has-text("Connect Wallet")').nth(1).click()
            await page.locator('span:has-text("Solflare")').click(click_count=2)
            await connect_wallet(context)

    if usdt:
        await page.locator('button:has-text("USDC")').click()
        await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/'
                           'div[2]/button[4]/span/img').click()  # xpath usdt при выборе монеты для обмена
        # await page.get_by_alt_text('USDC').click()
        # await page.wait_for_selector('Es9vM...nwNYB')
        # await page.get_by_alt_text('USDT').nth(0).click(force=True)
        # await page.get_by_placeholder('Search by token or paste address').type('USDT')
        # await page.get_by_text('Es9vM...nwNYB').click()  # подсвечиваемая часть контракта USDT
        logger.info('Первую монету выбрали: USDT')
        await page.wait_for_timeout(1000)
        if usdt_swap_value_to_sol == 0:
            await page.locator('input').nth(0).click()
            await page.locator('input').nth(0).type(f'{default_swap_value_for_sol}')
            logger.info(f'Свапаем дефолтное количество USDT: {default_swap_value_for_sol}')
        else:
            await page.locator('input').nth(0).click()
            await page.locator('input').nth(0).type(str(usdt_swap_value_to_sol))
            logger.info(f'Свапаем вами указанное количество USDT: {usdt_swap_value_to_sol}')
        await page.wait_for_timeout(1000)

    if jlp:
        await page.locator('button:has-text("USDC")').click()
        await page.locator('p:has-text("Jupiter Perps")').click()
        await page.wait_for_timeout(1000)
        await page.locator('input').nth(0).type('2')
        logger.info(f'USDT для свапа не было, cвапаем 2 JLP в SOL')

    if await page.get_by_alt_text("SOL").nth(0).is_visible():
        logger.info('Вторая монета дефолтно стоял: SOL')
    else:
        await page.locator('//*[@id="__next"]/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div['
                           '2]/div/button').click()  # xpath выбора второй монеты для свапа
        await page.get_by_text('Solana').click()
        logger.info('Вторую монету выбрали: SOL')
    await page.wait_for_timeout(1000)

    if (await page.locator('button:has-text("Insufficient SOL")').is_visible() or
            await page.locator('button:has-text("Swap")').is_disabled()):
        logger.error('Недостаточно SOl для оплаты газа')
        return False
    else:
        await page.locator('button[type="submit"]').click()
        while not await confirm_transaction(context):
            await page.locator('button[type="submit"]').click()
            # await expect(page).to_have_title('Solflare')
            await confirm_transaction(context)
            logger.error('Транзакция отклонена, через 10сек попробуем еще раз')
            await asyncio.sleep(10)

    await page.close()

    return True


async def chek_balance_sol(page: Page, context: BrowserContext) -> tuple[bool, dict]:
    balance: dict = await get_balance_in_wallet(page, context)

    """Sol при открытии позиции изымается залоговая сумма в размере 0.056 SOl(при закрытии позиции 
    возвращается), остальные на оплату газа нужны, а меньше 5 USDT нет смысла ходит свапат"""

    if balance['SOL'] < 0.08:
        logger.info('SOL меньше 0.08, идем свапат USDT to SOL')
        if balance['USDT'] > 5:
            if await swap_in_jupiter(page, context, usdt=True):  # Сохраняем результат
                return True, balance
        elif balance['USDT'] < 5 and balance['JLP'] > 2:
            await page.wait_for_timeout(20000)
            if await swap_in_jupiter(page, context, jlp=True):
                return True, balance
        else:
            logger.critical('Недостаточно средств для дальнейших действий, '
                            'пожалуйста пополните баланс SOL')
            return False, balance
    else:
        return True, balance

    # async def swap_usdt_to_sol(page: Page, context: BrowserContext) -> bool:
#
#     if page.url != url_jup or None:
#         page = await context.new_page()
#         await page.goto(url_jup)
#     try:
#         if await page.locator('button:has-text("Connect Wallet")').nth(0).is_visible():
#             await page.locator('button:has-text("Connect Wallet")').nth(0).click()
#             await page.locator('span:has-text("Solflare")').click(click_count=2)
#             await connect_wallet(context)
#     except AssertionError:
#         if await page.locator('button:has-text("Connect Wallet")').nth(1).is_visible():
#             await page.locator('button:has-text("Connect Wallet")').nth(1).click()
#             await page.locator('span:has-text("Solflare")').click(click_count=2)
#             await connect_wallet(context)
#
#     await page.locator('button:has-text("USDC")').click()
#     await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]'
#                        '/div/div/div/li[3]/div[2]/div[2]/div[1]/p').click()    # xpath usdt при выборе монеты для обмена
#     # await page.get_by_alt_text('USDC').click()
#     # await page.wait_for_selector('Es9vM...nwNYB')
#     # await page.get_by_alt_text('USDT').nth(0).click(force=True)
#     # await page.get_by_placeholder('Search by token or paste address').type('USDT')
#     # await page.get_by_text('Es9vM...nwNYB').click()  # подсвечиваемая часть контракта USDT
#     logger.info('Первую монету выбрали: USDT')
#     await page.wait_for_timeout(1000)
#     if usdt_swap_value_to_sol == 0:
#         await page.locator('input').nth(0).click()
#         await page.locator('input').nth(0).type(f'{default_swap_value_for_sol}')
#         logger.info(f'Свапаем дефолтно указанное количество USDT: {default_swap_value_for_sol}')
#     else:
#         await page.locator('input').nth(0).click()
#         await page.locator('input').nth(0).type(str(usdt_swap_value_to_sol))
#         logger.info(f'Свапаем вами указанное количество USDT: {usdt_swap_value_to_sol}')
#     await page.wait_for_timeout(1000)
#
#     if await page.get_by_alt_text("SOL").nth(0).is_visible():
#         logger.info('Вторая монета дефолтно стоял: SOL')
#     else:
#         await page.locator('//*[@id="__next"]/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div['
#                            '2]/div/button').click()  # xpath выбора второй монеты для свапа
#         await page.get_by_text('Solana').click()
#         logger.info('Вторую монету выбрали: SOL')
#     await page.wait_for_timeout(1000)
#
#     if (await page.locator('button:has-text("Insufficient SOL")').is_visible() or
#             await page.locator('button:has-text("Swap")').is_disabled()):
#         logger.error('Недостаточно SOl для оплаты газа')
#         return False
#     else:
#         await page.locator('button[type="submit"]').click()
#         while not await confirm_transaction(context):
#             await page.locator('button[type="submit"]').click()
#             await expect(page).to_have_title('Solflare')
#             await confirm_transaction(context)
#             logger.error('Транзакция отклонена, через 10сек попробуем еще раз')
#             await asyncio.sleep(10)
#
#     await page.close()
#
#     return True
