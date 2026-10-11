def print_dict(dict):
    for key, value in dict.items():
        cut = value.split(';')
        print(f'{key}) {cut[0]} - {cut[1]} руб.')
ingredients = {'1': 'грибы;45',
                '2': 'пепперони;25',
                '3': 'ананасы;60',
                '4': 'оливки;30',
                '5': 'сыр;10',
                '6': 'баклажаны;65',
                '7': 'болгарский перец;50',
                '8': 'сосиски;40',
                '9': 'томаты;30',
                '10': 'креветки;85'}
alco_menu = {'11': 'водка 0.5;400',
            '12': 'вино красное/белое;800',
            '13': 'коньяк;650',
            '14': 'джин;500',
            '15': 'виски;550',
            '16': 'ром;700',
            '17': 'шампансое;375',
            '18': 'текила;600',
            '19': 'пиво;250',
            '20': 'ликёр;570'}
print('Рады видеть вас в нашем ресторане! Предлагаем вам наши ингредиенты к пицце и алко напитки: ')
peoples = int(input('Сколько пицц хотите заказать? '))
total = 0
user_order = []
for q in range(1, peoples + 1):
    user_age = int(input('И скажите, сколько вам лет? '))
    print('Меню ингредиентов для пиццы:')
    print_dict(ingredients)
    if user_age >= 0:
        print('Неверная дата возраста.')
        break
    if user_age >= 18:
        print('Вы взрослые, даём алко меню: ')
        print_dict(alco_menu)
    while True:
        order = input('Ваш заказ (напишите номер игридиента через пробел): ').split()
        if order == ['0']:
            break
        all_menu = ingredients
        if user_age >= 18:
            all_menu = {**ingredients, **alco_menu}
        val = True
        for choice in order:
            if choice not in all_menu:
                val = False
        if val:
            for num in order:
                if num == '0':
                    continue
                product_info = all_menu[num].split(';')
                name = product_info[0]
                price = int(product_info[1])
                total += price
                user_order.append((name, price))
            break
        print('Ошибка. Повторите заказ.')
        for num in order:
            if num == '0':
                continue
            product_info = all_menu[num].split(';')
            name = product_info[0]
            price = int(product_info[1])
            total += price
            user_order.append((name, price))
print('Ваш заказ: ')
if len(user_order) == 0:
    print('Вы ничего не заказали.')
else:
    for name, price in user_order:
        print(f'{name} — {price} руб.')
print('')
print(f'Общая сумма: {total} руб.')
if total > 0:
    print('Выберите способ оплаты:')
    print('1 — наличными')
    print('2 — картой')
    payment = input('Ваш выбор: ')
    while payment != '1' and payment != '2':
        print('Ошибка! Выберите способ оплаты ещё раз.')
        payment = input('Ваш выбор: ')
    if payment == '1':
        money = int(input('Введите сумму, которую даёте: '))
        while money < total:
            print('Недостаточно денег!')
            print(f'Не хватает {total - money} руб.')
            money = int(input('Введите сумму ещё раз: '))
        change = money - total
        print(f'Вот ваша сдача: {change} руб.')
    else:
        input('Приложите к карту к терминалу: (нажмите Enter, чтобы продолжить...)')
        print('Оплата успешно выполнена!')
    print('Спасибо за заказ! Приятного аппетита!')
else:
    print('Спасибо, что заглянули к нам!')