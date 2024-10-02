import asyncio

import requests
from playwright.async_api import Page, BrowserContext
from setting import adspower_api_url, adspower_api_key, logger


async def smooth_scroll_with_mouse(page: Page, distance: int = 700, speed: int = 90):
    await page.mouse.move(0, 0)
    for _ in range(0, distance, speed):
        await page.mouse.wheel(0, speed)
        await asyncio.sleep(0.05)


def get_last_page(pages_list: list) -> str | None:
    if len(pages_list) > 1:
        return pages_list[-1]
    elif len(pages_list) == 1:
        return pages_list[0]
    return None


async def find_page(context: BrowserContext, title_name: str = None, keyword_in_url: str = None) -> Page | None:
    await asyncio.sleep(2)
    pages = context.pages
    # print(pages)
    result_pages = []  # список создаю для того чтобы если с нужным заголовком найдена много страниц чтобы
    # переключиться на самый последний
    result_page: Page | None = None
    if title_name:
        for page in pages:
            title = await page.title()
            if title_name in title:
                result_pages.append(page)
        # print(f'Страница с заголовком {title_name} найдена, количество найденных страниц:', len(result_pages))
        # print(result_pages)
    result_page = get_last_page(result_pages)

    if result_page:
        return result_page

    if keyword_in_url:
        if result_page is None:
            result_pages.clear()
            for page in pages:
                if keyword_in_url in page.url:
                    result_pages.append(page)
    # print(result_pages)
    result_page = get_last_page(result_pages)

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
        logger.critical(f"Не удалось получить данные профиля: {data['msg']}")
        raise Exception(f"Не удалось получить данные профиля: {data['msg']}")

    return data
