import asyncio

from playwright.async_api import BrowserContext, Page, expect
from setting import url_jup, usdt_swap_value_to_sol, default_swap_value_for_sol, logger
from wallet_functions import connect_wallet, confirm_transaction


async def swap_usdt_to_sol(page: Page, context: BrowserContext, usdt: bool = None, jlp: bool = None) -> bool:
    if page.url != url_jup or None:
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

    if usdt is not None:
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
            logger.info(f'Свапаем дефолтно указанное количество USDT: {default_swap_value_for_sol}')
        else:
            await page.locator('input').nth(0).click()
            await page.locator('input').nth(0).type(str(usdt_swap_value_to_sol))
            logger.info(f'Свапаем вами указанное количество USDT: {usdt_swap_value_to_sol}')
        await page.wait_for_timeout(1000)

        if await page.get_by_alt_text("SOL").nth(0).is_visible():
            logger.info('Вторая монета дефолтно стоял: SOL')
        else:
            await page.locator('//*[@id="__next"]/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div['
                               '2]/div/button').click()  # xpath выбора второй монеты для свапа
            await page.get_by_text('Solana').click()
            logger.info('Вторую монету выбрали: SOL')
        await page.wait_for_timeout(1000)

    if jlp is not None:
        await page.locator('button:has-text("USDC")').click()
        await page.locator('p:has-text("Jupiter Perps")').click()
        # await page.get_by_alt_text('USDC').click()
        # await page.wait_for_selector('Es9vM...nwNYB')
        # await page.get_by_alt_text('USDT').nth(0).click(force=True)
        # await page.get_by_placeholder('Search by token or paste address').type('USDT')
        # await page.get_by_text('Es9vM...nwNYB').click()  # подсвечиваемая часть контракта USDT
        logger.info('Первую монету выбрали: USDT')
        await page.wait_for_timeout(1000)
        await page.locator('input').nth(0).type('2')
        logger.info(f'Свапаем 2 JLP в USDT для покупки USDT')

        await page.locator('//*[@id="__next"]/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div['
                           '2]/div/button').click()  # xpath кнопки выбора второй монеты для свапа
        await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/'
                           'div[2]/button[4]/span/img').click()  # xpath usdt при выборе монеты для обмена
        logger.info('Вторую монету выбрали: USDT')
        await page.wait_for_timeout(1000)

    if (await page.locator('button:has-text("Insufficient SOL")').is_visible() or
            await page.locator('button:has-text("Swap")').is_disabled()):
        logger.error('Недостаточно SOl для оплаты газа')
        return False
    else:
        await page.locator('button[type="submit"]').click()
        while not await confirm_transaction(context):
            await page.locator('button[type="submit"]').click()
            await expect(page).to_have_title('Solflare')
            await confirm_transaction(context)
            logger.error('Транзакция отклонена, через 10сек попробуем еще раз')
            await asyncio.sleep(10)

    await page.close()

    return True
