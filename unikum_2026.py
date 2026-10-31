sucsses = False
while not sucsses:
    try:
        temp = int(input('Введите температуру: '))
        weather_event = input('Введите время года (дождь, снег, ясно, солнечно, переменная облачность, пасмурно, иней, град, туман, ветер, гроза, метель) ').lower()
        if weather_event == 'ясно' or weather_event == 'солнечно' or weather_event == 'пасмурно':
            if temp >= 22:
                print('Одевайте шорты, футболку и кепку')
            else:
                print('Неправильный ввод температуры')
        elif weather_event == 'дождь' or weather_event == 'туман' or weather_event == 'ветер' or weather_event == 'град':
            if temp > 0 and temp < 20:
                print('Одевайте ветровку, штаны, ботинки, тонкую шапку')
            else:
                print('Неправильный ввод температуры')
        elif weather_event == 'снег' or weather_event == 'иней' or weather_event == 'метель':
            if temp < -15 and temp < 0:
                print('Одевайте тёплую шапку, пуховик, ботинки, шарф, перчатки')
            else:
                print('Неправильный ввод температуры')
        elif weather_event == 'гроза':
            if temp <= 22 and temp > -10:
                print('В грозу лучше не выходите. 😅')
            else:
                print('Неправильный ввод температуры')
    except ValueError:
        print('Введите првильный ввод значений.')
