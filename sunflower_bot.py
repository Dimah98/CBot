"""Автоматизація гри Sunflower Land.

Модуль містить функції для отримання даних ферми через публічний API,
групування ресурсів за типами та автоматизації кліків у браузері
Playwright. Коментарі написані українською для полегшення супроводу.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

import requests
from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright


Coordinate = Tuple[float, float]


@dataclass
class ResourceGroup:
    """Описує групу ресурсів певного типу та їх координати."""

    resource_type: str
    coordinates: List[Coordinate]


def fetch_farm_data(farm_id: str, api_key: str) -> Mapping:
    """Отримує сирі дані ферми через API Sunflower Land.

    Параметри:
        farm_id: Ідентифікатор ферми.
        api_key: Ключ для заголовку ``x-api-key``.

    Повертає:
        Розібране JSON-представлення відповіді API.
    """

    url = f"https://api.sunflower-land.com/community/farms/{farm_id}"
    response = requests.get(url, headers={"x-api-key": api_key}, timeout=30)
    response.raise_for_status()
    return response.json()


def _extract_coordinate(tree_like: Mapping) -> Coordinate:
    """Визначає координати дерева, враховуючи можливі схеми JSON.

    Деякі варіанти відповіді можуть містити координати як ``{"x": 1, "y": 2}``,
    інші — вкладено як ``{"coordinates": {"x": 1, "y": 2}}``. Функція
    покриває обидва випадки та гарантує повернення кортежу ``(x, y)``.
    """

    if "coordinates" in tree_like and isinstance(tree_like["coordinates"], Mapping):
        data = tree_like["coordinates"]
        return float(data.get("x", 0)), float(data.get("y", 0))

    return float(tree_like.get("x", 0)), float(tree_like.get("y", 0))


def parse_resource_groups(farm_data: Mapping) -> Dict[str, ResourceGroup]:
    """Групує координати ресурсів за типами.

    На поточний момент зосереджуємося на деревах, але структуру лишаємо
    узагальненою, щоб у майбутньому легко додати каміння, залізо тощо.

    Повертає:
        Словник, де ключ — назва ресурсу, а значення — :class:`ResourceGroup`.
    """

    grouped: Dict[str, ResourceGroup] = {}
    trees: Iterable[Mapping] = farm_data.get("trees", []) if isinstance(farm_data, Mapping) else []

    for tree in trees:
        coords = _extract_coordinate(tree)
        grouped.setdefault("trees", ResourceGroup(resource_type="trees", coordinates=[])).coordinates.append(coords)

    return grouped


def should_purchase_axes(inventory: Mapping) -> bool:
    """Перевіряє, чи варто купувати сокири.

    Логіка: якщо вже є більше 10 сокир або доступно понад 500 золота,
    робимо клік по координатах магазину, щоб поповнити запас інструментів.
    Якщо ресурсів бракує — повертаємо ``False`` і пропускаємо покупку.
    """

    axes = inventory.get("axes", 0)
    gold = inventory.get("gold", 0)
    return axes > 10 or gold > 500


def create_browser_context(playwright: Playwright, profile_dir: str) -> BrowserContext:
    """Створює браузерний контекст з окремим профілем.

    ``profile_dir`` дозволяє розділити кукі та localStorage між сесіями,
    що зручно для одночасного запуску кількох ботів або ізоляції тестів.
    """

    return playwright.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        headless=False,
        viewport={"width": 1280, "height": 720},
    )


def go_to_game(context: BrowserContext) -> Page:
    """Відкриває гру та повертає сторінку для подальших дій."""

    page = context.new_page()
    page.goto("https://sunflower-land.com/play/", wait_until="domcontentloaded")
    return page


def click_store_for_axes(page: Page, store_coordinate: Coordinate) -> None:
    """Імітує покупку сокир кліком по координатах магазину."""

    x, y = store_coordinate
    page.mouse.click(x, y)


def chop_trees(page: Page, tree_coordinates: Sequence[Coordinate]) -> None:
    """Тричі клікає по кожній координаті дерева для збору дерева."""

    for x, y in tree_coordinates:
        for _ in range(3):
            page.mouse.click(x, y)


def run_bot(
    farm_id: str,
    api_key: str,
    profile_dir: str,
    store_coordinate: Coordinate,
    inventory: Mapping,
) -> None:
    """Повний сценарій: отримує дані ферми, купує сокири та рубає дерева.

    Якщо запасів недостатньо, покупка та збір дерев будуть пропущені.
    """

    farm_data = fetch_farm_data(farm_id=farm_id, api_key=api_key)
    resources = parse_resource_groups(farm_data)

    if not should_purchase_axes(inventory):
        return

    tree_coordinates = resources.get("trees", ResourceGroup("trees", [])).coordinates
    if not tree_coordinates:
        return

    with sync_playwright() as playwright:
        context = create_browser_context(playwright, profile_dir)
        page = go_to_game(context)
        click_store_for_axes(page, store_coordinate)
        chop_trees(page, tree_coordinates)
        context.close()


__all__ = [
    "Coordinate",
    "ResourceGroup",
    "fetch_farm_data",
    "parse_resource_groups",
    "should_purchase_axes",
    "create_browser_context",
    "go_to_game",
    "click_store_for_axes",
    "chop_trees",
    "run_bot",
]
