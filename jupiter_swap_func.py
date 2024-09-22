import asyncio

from playwright.async_api import BrowserContext, Page

from setting import url_jup, usdt_swap_value_to_sol, default_swap_value_for_sol
from wallet_functions import connect_wallet, confirm_transaction


async def swap_usdt_to_sol(page: Page, context: BrowserContext) -> bool:
    url_page = page.url

    if url_page != url_jup:
        await page.goto(url_jup)
        await page.get_by_role("button", name="Connect Wallet").first.click()
        await page.get_by_role("button", name="Solflare icon Solflare Auto").click()
        await connect_wallet(context)

    await page.locator('button:has-text("USDC")').click()
    await asyncio.sleep(1)
    await page.get_by_text('Es9vM...nwNYB').click()  # подсвечиваемая часть контракта USDT
    print('Первую монету выбрали: USDT')
    await asyncio.sleep(1)
    if usdt_swap_value_to_sol == 0:
        await page.locator('input').nth(0).click()
        await page.locator('input').nth(0).type(f'{default_swap_value_for_sol}')
        print(f'Свапаем дефолтно указанное количество USDT: {default_swap_value_for_sol}')
    else:
        await page.locator('input').nth(0).click()
        await page.locator('input').nth(0).type(str(usdt_swap_value_to_sol))
        print(f'Свапаем вами указанное количество USDT: {usdt_swap_value_to_sol}')
    await asyncio.sleep(1)

    if await page.get_by_alt_text("SOL").nth(0).is_visible():
        print('Вторая монета дефолтно стоял: SOL')
    else:
        await page.locator('//*[@id="__next"]/div[2]/div[3]/div[1]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div['
                           '2]/div/button').click()  # xpath выбора второй монеты для свапа
        await page.get_by_text('Solana').click()
        print('Вторую монету выбрали: SOL')
    await asyncio.sleep(1)

    if (await page.locator('button:has-text("Insufficient SOL")').is_visible() or
            await page.locator('button:has-text("Swap")').is_disabled()):
        print('Недостаточно SOl для оплаты газа')
        return False
    else:
        await page.locator('button[type="submit"]').click()
        while not await confirm_transaction(context):
            await page.locator('button[type="submit"]').click()
            await asyncio.sleep(2)
            await confirm_transaction(context)
            print('Транзакция не отклонена, через 10сек попробуем еще раз')
            await asyncio.sleep(10)

    await page.close()

    return True
