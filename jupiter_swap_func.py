import asyncio

from playwright.async_api import BrowserContext, Page
from setting import usdt_swap_value_to_sol, default_swap_value_for_sol, logger
from wallet_functions import connect_wallet, confirm_transaction, get_balance_in_wallet
from functions import find_page


async def swap_in_jupiter(context: BrowserContext, usdt: bool = False, jlp: bool = False) -> bool:
    # try:
    page: Page = await find_page(context, 'Swap | Jupiter', keyword_in_url='jup.ag')
    # except Exception as e:
    #     logger.error(f'Словили ошибку: {e} '
    #                  'Не удалось найти страницу Jup.ag, открываем новую страницу')
    #     page: Page = await context.new_page()
    #     await page.goto(url_jup)

    # await page.wait_for_load_state('domcontentloaded')
    await page.bring_to_front()

    if (
            await page.locator('button:has-text("Connect Wallet")').nth(0).is_visible() or
            await page.locator('button:has-text("Connect Wallet")').nth(1).is_visible()
    ):
        try:
            # if await page.locator('button:has-text("Connect Wallet")').nth(0).is_visible():
            await page.locator('button:has-text("Connect Wallet")').nth(0).click()
            await page.locator('span:has-text("Solflare")').click(click_count=2)
            await connect_wallet(context)
        except AssertionError:
            # if await page.locator('button:has-text("Connect Wallet")').nth(1).is_visible():
            await page.locator('button:has-text("Connect Wallet")').nth(1).click()
            await page.locator('span:has-text("Solflare")').click(click_count=2)
            await connect_wallet(context)

    first_input_place = page.locator('input').nth(0)

    if usdt:
        await page.locator('button:has-text("USDC")').click()
        await page.get_by_placeholder('Search by token or paste address').type('USDT')
        await page.locator('span:has-text("Es9vM...nwNYB")').click()
        logger.info('Первую монету выбрали: USDT')
        await page.wait_for_timeout(1000)
        if usdt_swap_value_to_sol == 0:
            await first_input_place.click()
            await first_input_place.type(f'{default_swap_value_for_sol}')
            logger.info(f'Свапаем дефолтное количество USDT: {default_swap_value_for_sol}')
        else:
            await first_input_place.click()
            await first_input_place.type(str(usdt_swap_value_to_sol))
            logger.info(f'Свапаем вами указанное количество USDT: {usdt_swap_value_to_sol}')
        await page.wait_for_timeout(1000)

    if jlp:
        await page.locator('button:has-text("USDC")').click()
        if await page.locator('p:has-text("Jupiter Perps")').is_visible():
            await page.locator('p:has-text("Jupiter Perps")').click()
        else:
            await page.get_by_placeholder('Search by token or paste address').type('JLP')
            await page.locator('p:has-text("Jupiter Perps")').click()

        # await page.wait_for_load_state('domcontentloaded')
        await first_input_place.type('2')
        logger.info(f'USDT для свапа не было, cвапаем 2 JLP в SOL')

    if (await page.locator('button:has-text("Insufficient SOL")').is_visible() or
            await page.locator('button:has-text("Swap")').is_disabled()):
        logger.error('Недостаточно SOl для оплаты газа')
        return False
    else:
        await page.locator('button[type="submit"]').click()
        while not await confirm_transaction(context):
            logger.error('Через 10сек попробуем еще раз')
            await asyncio.sleep(10)
            await page.locator('button[type="submit"]').click()
            # await expect(page).to_have_title('Solflare')
            if await confirm_transaction(context):
                logger.debug('swap_in_jupiter in else break')
                break

    # await page.close()

    return True


async def chek_balance_sol(page: Page, context: BrowserContext) -> tuple[bool, dict]:
    balance: dict = await get_balance_in_wallet(context)

    """Sol при открытии позиции изымается залоговая сумма в размере 0.056 SOl(при закрытии позиции 
    возвращается), остальные на оплату газа нужны, а меньше 5 USDT нет смысла ходит свапат"""

    if balance['SOL'] < 0.08:
        logger.info('SOL меньше 0.08, идем свапат USDT to SOL')
        if balance['USDT'] > 5:
            if await swap_in_jupiter(context, usdt=True):
                return True, balance
        elif balance['USDT'] < 5 and balance['JLP'] > 2:
            # await page.wait_for_timeout(20000)
            if await swap_in_jupiter(context, jlp=True):
                return True, balance
        else:
            logger.critical('Недостаточно средств для дальнейших действий, '
                            'пожалуйста пополните баланс SOL')
            return False, balance
    else:
        return True, balance

