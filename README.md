# CBot

Модуль `sunflower_bot.py` автоматизує збір дерева в грі [Sunflower Land](https://sunflower-land.com/play/) через API та браузерну сесію Playwright. Код отримує інвентар із заголовком `x-api-key`, групує координати ресурсів, за потреби купує сокири та тричі клікає по кожній координаті дерева.

## Вимоги
- Python 3.11+
- Залежності з `requirements.txt` (`requests`, `playwright`)
- Доступ до API Sunflower Land із власним `farmId` та `x-api-key`

## Установка залежностей
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Запуск сценарію
Приклад коду для запуску повного сценарію:
```python
from sunflower_bot import run_bot

run_bot(
    farm_id="<ВАШ_FARM_ID>",
    api_key="<ВАШ_API_KEY>",
    profile_dir="/path/to/profile",
    store_coordinate=(100, 200),
)
```
- `profile_dir` — шлях до каталогу для окремого профілю браузера.
- `store_coordinate` — координати магазину для покупки сокир (клік виконується один раз).

Якщо бот виявляє більше 10 сокир або понад 500 золота, він клікає по магазину та виконує трійний клік по кожному дереву зі списку з API. Якщо ресурсів бракує або координат немає, сценарій завершиться без дій.

## Перевірка
```bash
python -m compileall sunflower_bot.py
```
