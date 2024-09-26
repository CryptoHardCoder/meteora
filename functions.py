import asyncio

import requests
from playwright.async_api import Page, BrowserContext
from loguru import logger

from setting import adspower_api_url, adspower_api_key


async def smooth_scroll_with_mouse(page: Page, distance: int = 700, speed: int = 90):
    await page.mouse.move(0, 0)
    for _ in range(0, distance, speed):
        await page.mouse.wheel(0, speed)
        await asyncio.sleep(0.05)


async def find_page(title_name: str, context: BrowserContext) -> Page | None:
    # await asyncio.sleep(2)
    context.expect_event('page')
    pages = context.pages
    result_pages = []
    result_page: Page | None = None
    for page in pages:
        title = await page.title()
        if title_name in title:
            result_pages.append(page)

    # print(f'Страница с заголовком {title_name} найдена, количество найденных страниц:', len(result_pages))
    if len(result_pages) == 0:
        return None
    elif len(result_pages) > 1:
        result_page = result_pages[-1]
    elif len(result_pages) == 1:
        result_page = result_pages[0]

    return result_page


async def get_profile_data(private_key: str) -> dict:
    """Запрашивает и возвращает данные профиля в виде словаря."""
    response = requests.get(adspower_api_url, params={
        "user_id": private_key,
        "apikey": adspower_api_key
    })
    data = response.json()
    # print(data)

    if data["code"] != 0:
        logger.error(f"Не удалось получить данные профиля: {data['msg']}")
        raise Exception(f"Не удалось получить данные профиля: {data['msg']}")

    return data
