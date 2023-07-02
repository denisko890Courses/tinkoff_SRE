import requests
import sys
import yaml
from datetime import datetime, timedelta

oncall_url=sys.argv[1]
username=sys.argv[2]
password=sys.argv[3]
path_to_teams_data = sys.argv[4]

requests_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
request_data = {'username': username, 'password': password}

# Авторизация пользователя
get_auth_response = requests.post(url=f'{oncall_url}/login', headers=requests_headers, data=request_data)
if get_auth_response.status_code != 200:
    print('Ошибка при авторизации')
    exit()

# Получение cookie и csrf токена
my_cookies = get_auth_response.cookies
response_json = get_auth_response.json()
my_csrf_token = response_json['csrf_token']

# Чтение данных из файла
with open(path_to_teams_data, 'r') as file:
    data = yaml.safe_load(file)

# Запрос на создание команды
for team_data in data['teams']:
    team_name = team_data['name']

    # Создание команды
    post_team_response = requests.post(oncall_url + '/api/v0/teams', json={
        'name': team_name,
        'scheduling_timezone': team_data['scheduling_timezone'],
        'email': team_data['email'],
        'slack_channel': team_data['slack_channel']
    }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

    if post_team_response.status_code != 201:
        print(f'Ошибка при создании команды {team_name}')
        continue

    post_rosters_response = requests.post(f'{oncall_url}/api/v0/teams/{team_name}/rosters', json={
        'name': team_name
    }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

    if post_rosters_response.status_code != 201:
        print(post_rosters_response.json())
        print(f'Ошибка при создании rosters {team_name}')
        continue


    # Запрос на создание пользователей
    for user_data in team_data['users']:
        user_name = user_data['name']

        post_user_response = requests.post(f'{oncall_url}/api/v0/users', json={
            'contacts': {
                'call': user_data['phone_number'],
                'email': user_data['email'],
                'sms': user_data['phone_number']
            },
            'name': user_name,
            'full_name': user_data['full_name'],
        }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

        if post_user_response.status_code != 201:
            print(f'Ошибка при создании пользователя {user_name}')
            continue

        # Обновление контактов пользователей
        put_user_response = requests.put(f'{oncall_url}/api/v0/users/{user_name}', json={
            'contacts': {
                'call': user_data['phone_number'],
                'email': user_data['email'],
                'sms': user_data['phone_number']
            },
            'name': user_name,
            'full_name': user_data['full_name'],
        }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

        if put_user_response.status_code != 204:
            print(f'Ошибка при обновлении пользователя {user_name} {put_user_response}')
            continue

        post_rosters_user_response = requests.post(f'{oncall_url}/api/v0/teams/{team_name}/rosters/{team_name}/users', json={
            'name': user_name
        }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

        if post_rosters_user_response.status_code != 201:
            print(post_rosters_user_response.content)
            print(f'Ошибка при добавление пользователя {user_name} в команду {team_name} {post_rosters_user_response}')
            continue


        # Запрос на создание shedule
        for duty_data in user_data['duty']:
            date_string = duty_data['date']
            date_format = '%d/%m/%Y'
            role = duty_data['role']
            date_start_object = datetime.strptime(date_string, date_format)
            date_start_object_timestamp = int(date_start_object.timestamp())
            date_stop_object = date_start_object + timedelta(days=1)
            date_stop_object_timestamp = int(date_stop_object.timestamp())

            response = requests.post(f'{oncall_url}/api/v0/events', json={
                "role": role,
                "start": date_start_object_timestamp,
                "end": date_stop_object_timestamp,
                "team": team_name,
                "user": user_name
            }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

            if response.status_code != 201:
                print(f'Ошибка при создании дежурства для пользователя {user_name} в команде {team_name} на дату {date_string}')

    print(f'Расписание успешно заполнено для команды {team_name}')
