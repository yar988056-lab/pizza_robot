import asyncio
import json
import random
import re

admin_password = 'Zhjckfd0316'
ingredients = {
    '1': 'грибы;45', '2': 'пепперони;25', '3': 'ананасы;60', '4': 'оливки;30',
    '5': 'сыр;10', '6': 'баклажаны;65', '7': 'болгарский перец;50', '8': 'сосиски;40',
    '9': 'томаты;30', '10': 'сок яблочный/апельсиновый;150', '11': 'пепперони;90',
    '12': 'ветчина;65', '13': 'бекон;80', '14': 'курица;70', '15': 'ананасы;55',
    '16': 'маслины;45', '17': 'болгарский перец;35', '18': 'помидоры черри;40',
    '19': 'моцарелла;75', '20': 'пармезан;85', '21': 'кукуруза;30', '22': 'маринованные огурцы;35',
    '23': 'красный лук;25', '24': 'охотничьи колбаски;85', '25': 'говядина;100',
    '26': 'шпинат;40', '27': 'халапеньо;35', '28': 'фета;70', '29': 'артишоки;65',
    '30': 'соус барбекю;45',
}
alco_menu = {
    '31': 'водка 0.5;400', '32': 'вино красное/белое;800', '33': 'коньяк;650',
    '34': 'джин;500', '35': 'виски;550', '36': 'ром;700', '37': 'шампанское;375',
    '38': 'текила;600', '39': 'пиво;250', '40': 'ликёр;570',
}

stock = {}
for k in ingredients.keys():
    stock[k] = 50
for k in alco_menu.keys():
    stock[k] = 15.0

items_in_delivery = set()
DELIVERY_TIME_SECONDS = 10 * 60
TOTAL_OVENS = 5
busy_ovens = 0

def load_orders() -> list:
    try:
        with open('orders.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_orders(orders: list) -> None:
    with open('orders.json', 'w', encoding='utf-8') as file:
        json.dump(orders, file, ensure_ascii=False, indent=4)

def print_dict(menu: dict) -> None:
    for key, value in menu.items():
        name, price = value.split(';')
        print(f'{key}) {name} - {price} руб.')

order_queue = asyncio.Queue()
oven_queue = asyncio.Queue()
order_counter = 0

async def async_input(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)

async def delivery_truck(item_id: str) -> None:
    if item_id in ingredients:
        name = ingredients[item_id].split(';')[0]
        amount = 50
        unit = 'шт.'
    else:
        name = alco_menu[item_id].split(';')[0]
        amount = 15.0
        unit = 'л.'
    print(f"\n(ДОСТАВКА) Внимание! {name} закончился. Грузовик выехал, ожидайте 10 минут...")
    await asyncio.sleep(DELIVERY_TIME_SECONDS)
    stock[item_id] += amount
    items_in_delivery.remove(item_id)
    print(f"\n(ДОСТАВКА) Грузовик приехал. На складе снова {stock[item_id]} {unit}.")

async def oven(oven_name: str, queue: asyncio.Queue) -> None:
    global busy_ovens
    _ = oven_name
    while True:
        task = await queue.get()
        if task is None:
            queue.task_done()
            break
        busy_ovens += 1
        order, ready_event = task
        try:
            bake_time = random.uniform(3.0, 15.0)
            await asyncio.sleep(bake_time)
            await asyncio.to_thread(save_order_to_file, order)
            ready_event.set()
        finally:
            busy_ovens -= 1
            queue.task_done()

async def waiter(waiter_name: str, order_q: asyncio.Queue, oven_q: asyncio.Queue, stats: dict) -> None:
    while True:
        order = await order_q.get()
        if order is None:
            order_q.task_done()
            break
        print(f"\n{waiter_name} Принял заказ №{order['id']} и отнес на кухню.")
        ready_event = asyncio.Event()
        await oven_q.put((order, ready_event))
        await ready_event.wait()
        print(f"\n{waiter_name} Забрал из печки и отдал заказ.")
        stats[waiter_name] = stats.get(waiter_name, 0) + 1
        order_q.task_done()

def save_order_to_file(order: dict) -> None:
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    async def start_kitchen(waiters_count: int = 6, ovens_count: int = TOTAL_OVENS) -> tuple[list, dict]:
        stats = {}
        ovens = [
            asyncio.create_task(oven(f'Печка-{i}', oven_queue))
            for i in range(1, ovens_count + 1)
        ]
        waiters = [
            asyncio.create_task(waiter(f'Официант-{i}', order_queue, oven_queue, stats))
            for i in range(1, waiters_count + 1)
        ]
        return waiters + ovens, stats
    async def stop_kitchen(all_tasks: list, waiters_count: int = 6, ovens_count: int = TOTAL_OVENS) -> None:
        await order_queue.join()
        await oven_queue.join()
        for _ in range(waiters_count):
            await order_queue.put(None)
        for _ in range(ovens_count):
            await oven_queue.put(None)
        await asyncio.gather(*all_tasks)
    async def safe_int_async(prompt: str) -> int:
        while True:
            try:
                return int(await async_input(prompt))
            except ValueError:
                print('Ошибка! Введите целое число.')
    async def choose_products_async(menu: dict) -> list:
        while True:
            order_input = await async_input('Ваш заказ (номера через пробел, 0 — закончить): ')
            order = order_input.split()
            if order == ['0']:
                return list()
            if not all(num in menu for num in order):
                print('Ошибка. Есть несуществующие номера.')
                continue
            return order
    async def make_order() -> None:
        global order_counter
        if busy_ovens + oven_queue.qsize() >= TOTAL_OVENS:
            print("\nИзвините, но все печки сейчас заняты. Заказ отменен. Попробуйте позже.")
            return
        user_age = await safe_int_async('Сколько вам лет? ')
        if user_age <= 0:
            print('Неверный возраст.')
            return
        menu = {**ingredients, **alco_menu} if user_age >= 18 else ingredients
        if user_age >= 18:
            print('\nВзрослым - алко-меню:')
            print_dict(alco_menu)
        peoples = await safe_int_async('Сколько пицц хотите заказать? ')
        total = 0
        user_order = []
        order_ids = []
        for q in range(1, peoples + 1):
            print(f'\nПицца - {q}')
            print('Меню ингредиентов:')
            print_dict(ingredients)
            products_ids = await choose_products_async(menu)
            for num in products_ids:
                name, price = menu[num].split(';')
                user_order.append((name, int(price)))
                order_ids.append(num)
                total += int(price)
        if not user_order:
            print('Вы ничего не заказали. Спасибо, что заглянули!')
            return
        required = {}
        for item_id in order_ids:
            if item_id in ingredients:
                required[item_id] = required.get(item_id, 0) + 1
            else:
                name = alco_menu[item_id].split(';')[0]
                match = re.search(r'\d+\.?\d*', name)
                volume = float(match.group()) if match else 0.5
                required[item_id] = required.get(item_id, 0) + volume

        for item_id, amount in required.items():
            if stock[item_id] < amount:
                item_name = menu[item_id].split(';')[0]
                print(f"\nОшибка! На складе недостаточно: {item_name}.")
                print(f"Требуется: {amount}, в наличии: {stock[item_id]}. Заказ отменен.")
                if stock[item_id] <= 0 and item_id not in items_in_delivery:
                    items_in_delivery.add(item_id)
                    asyncio.create_task(delivery_truck(item_id))
                return
        for item_id, amount in required.items():
            stock[item_id] -= amount
            if stock[item_id] <= 0 and item_id not in items_in_delivery:
                items_in_delivery.add(item_id)
                asyncio.create_task(delivery_truck(item_id))
        print('\nВаш заказ:')
        for name, price in user_order:
            print(f'{name} — {price} руб.')
        print(f'\nОбщая сумма: {total} руб.')
        print('Выберите способ оплаты:')
        print('1 — наличными')
        print('2 — картой')
        payment = await async_input('')
        while payment not in ('1', '2'):
            print('Ошибка! Выберите 1 или 2.')
            payment = await async_input('')
        if payment == '1':
            money = await safe_int_async('Введите сумму, которую даёте: ')
            while money < total:
                print(f'Недостаточно! Не хватает {total - money} руб.')
                money = await safe_int_async('Введите сумму ещё раз: ')
            change = money - total
            print(f'Вот ваша сдача: {change} руб.')
            payment_method = 'Наличными'
        else:
            await async_input('Приложите карту к терминалу (Enter — продолжить)...')
            print('Связь с банком...')
            await asyncio.sleep(2.0)
            print('Оплата успешно выполнена!')
            payment_method = 'Карта'
            money = total
            change = 0
        print('Спасибо за заказ! Приятного аппетита!')
        print('Ваш заказ передан на кухню. Ожидайте...')
        order_counter += 1
        order_data = {
            'id': order_counter,
            'products': user_order,
            'total': total,
            'payment': payment_method,
            'money': money,
            'change': change,
        }
        order_queue.put_nowait(order_data)
    async def admin_panel() -> None:
        password = await async_input('Введите пароль администратора: ')
        if password != admin_password:
            print('Неверный пароль!')
            return
        while True:
            print('\n--- Панель администратора ---')
            print('1 - История всех заказов')
            print('2 - Остатки на складе')
            print('3 - Выход из панели')
            choice = await async_input('Ваш выбор: ')
            if choice == '1':
                orders = load_orders()
                if not orders:
                    print('Заказов пока нет.')
                    continue
                print('\nИстория всех заказов:')
                for number, order in enumerate(orders, start=1):
                    print(f'\n=========Заказ№{number}=========')
                    for name, price in order['products']:
                        print(f'{name} — {price} руб.')
                    print(f"\nСумма: {order['total']} руб.")
                    print(f"Оплата: {order['payment']}")
                    print(f"Внесено: {order['money']} руб.")
                    print(f"Сдача: {order['change']} руб.")
            elif choice == '2':
                print('\n--- Остатки на складе ---')
                print('Ингредиенты:')
                for k, v in stock.items():
                    if k in ingredients:
                        name = ingredients[k].split(';')[0]
                        delivery_mark = '(в пути)' if k in items_in_delivery else ''
                        print(f'  {name}: {v} шт.{delivery_mark}')
                print('\nАлкоголь:')
                for k, v in stock.items():
                    if k in alco_menu:
                        name = alco_menu[k].split(';')[0]
                        delivery_mark = '(в пути)' if k in items_in_delivery else ''
                        print(f'  {name}: {v} л.{delivery_mark}')
            elif choice == '3':
                break
            else:
                print('Неверный выбор.')
    async def main() -> None:
        print('Приветствуем вас в нашей пиццерие!')
        all_tasks, stats = await start_kitchen(waiters_count=6, ovens_count=TOTAL_OVENS)
        while True:
            print('')
            print('1 - Войти в панель администратора')
            print('2 - Сделать заказ')
            print('3 - Выход из программы')
            choice = await async_input('Ваш выбор: ')
            if choice == '1':
                await admin_panel()
            elif choice == '2':
                await make_order()
            elif choice == '3':
                print('Ожидаем завершения всех заказов.')
                await stop_kitchen(all_tasks, waiters_count=6, ovens_count=TOTAL_OVENS)
                for name, count in sorted(stats.items()):
                    print(f'{name}: {count} заказ(ов)')
                print('До свидания!')
                break
            else:
                print('Неверный выбор.')

if __name__ == '__main__':
    asyncio.run(main())