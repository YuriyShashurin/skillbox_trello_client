import sys
import requests

base_url = "https://api.trello.com/1/{}"
auth_params = {
    'key': "ENTER_YOUR_KEY",
    'token': "ENTER_YOUR_TOKEN", }
board_id = "ENTER_YOUR_BOARD_ID"


def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        sum_tasks = 0
        # Получаем количество задач для колонки column
        for task in task_data:
            if task['name']:
                sum_tasks += 1

        # Выводим название колонки и количество задач в ней
        print(column['name'] + " (Общее количество задач: " + str(sum_tasks) + ")")
        if not task_data:
            print('\t' + 'Нет задач!')
            continue

        # выводим список задач с нумерацией
        n = 1
        for task in task_data:
            print('\t' + str(n) + ". " + task['name'])
            n += 1


# Создание новой колонки
def create_list(name):
    board_data = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
    requests.post(base_url.format('lists'), data={'name': name, 'idBoard': board_data['id'], **auth_params})
    print("Колонка добавлена")

# Создание новой задачи
def create_task(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break
    print("Задача " + name + " создана в колонке " + column_name)

def check_task(name,column_data):
    # Среди всех колонок нужно найти все задачи с указанным именем
    tasks_list = []
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                #Добавляем все совпадения в словарь, затем словарь добавляем в список
                valid_task = {
                    "list_name": column["name"],
                    "list_id": column["id"],
                    "task_id": task['id'],
                    "task_name": task["name"],
                    "task_desc": task["desc"],
                    "task_url": task["shortUrl"],
                }
                tasks_list.append(valid_task)
    #   Если совпадений названий нет, то выбирается id единственной валидной задачи
    if len(tasks_list)<=1:
        for task in tasks_list:
            task_id = task['task_id']
    #   Иначе выводим пользователи в консоль все валидные задачи...
    else:
        print("Найдено несколько задач с одинаковым названием: ")
        i = 1
        for tasks in tasks_list:
            print('\t' + "№ " + str(i) + ". " + "Задача " + "\"" + tasks['task_name'] + "\"" + " в столбце " + "\"" + tasks['list_name'] + "\"" + " с описанием задачи " + "\"" + tasks['task_desc'] + "\"" + ". Ссылка на задачу: " +  tasks['task_url'] )
            i += 1
        select_task = 0
        # ... И даем пользователю выбрать из списка задачу по №, с которой необходимо продолжить работу. Также в цикле проверяем пользовательский ввод
        while select_task < 1 or select_task > (i - 1):
            try:
                select_task = int(input("Введите № задачи, которую в дальнейшем необходимо перенести (число от 1 до {} включительно): ".format(i - 1) ))
                if select_task < 1 or select_task > (i - 1):
                    print("Error! Выбран неправильный №, попробуйте снова.")
            # Если полученный ввод не число, будет вызвано исключение.
            # При успешном преобразовании в целое число цикл закончится.
            except ValueError:
                print("Error! Выбран неправильный № (введено не число), попробуйте снова.")


        # Фиксируем для пользователя выбранный номер задачи, сохраняем id выбранной задачи для дальнейшей работы
        print("Выбрана задача с № {}".format(select_task))
        task_id = tasks_list[select_task-1]['task_id']
    # Возвращаем полученное айди для перемещения задачи между колонками
    return task_id

# Перемещение задач между колонками
def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Получим данные о id задачи после проверки на совпадающие имена и выборе пользователям нужной задачи в случае наличия совпадений
    task_id = check_task(name, column_data)

    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # Проверяем, существует ли выбранная пользователем задача в колонке, куда необходимо ее перенести
            column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
            tasks_id = []
            for task in column_tasks:
                tasks_id.append(task['id'])
            # Если задача уже существует в необходимой колонке, перенос осуществляться не будет, предупредим пользователя
            if task_id in tasks_id:
                print('Данная задача уже находится в столбце ' + column_name)
            # Если такой задачи нет,  выполним запрос к API для перемещения задачи в нужную колонку
            else:
                requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                              data={'value': column['id'], **auth_params})
                print("Задача " + "\"" + name + "\"" + " перенесена в колонку " + "\"" + column_name + "\"")
                break

if __name__ == "__main__":
    #Запускаем в консоли в формате "python trello_client.py"
    if len(sys.argv) <= 2:
        read()
    # Запускаем в консоли в формате "python trello_client.py create_task ИМЯ_ЗАДАЧИ ИМЯ_КОЛОНКИ"
    elif sys.argv[1] == 'create_task':
        create_task(sys.argv[2], sys.argv[3])
    # Запускаем в консоли в формате "python trello_client.py create_list ИМЯ_КОЛОНКИ"
    elif sys.argv[1] == 'create_list':
        create_list(sys.argv[2])
    # Запускаем в консоли в формате "python trello_client.py move ИМЯ_ЗАДАЧИ ИМЯ_КОЛОНКИ"
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
