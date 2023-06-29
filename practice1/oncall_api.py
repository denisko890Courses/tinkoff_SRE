import requests
import yaml

oncall_url='http://51.250.64.245:8080'
username='root'
password='123'

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
with open('teams.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Запрос на создание команды
for team_data in data['teams']:
    team_name = team_data['name']

    post_team_response = requests.post(oncall_url + '/api/v0/teams', json={
        'name': team_name,
        'scheduling_timezone': team_data['scheduling_timezone'],
        'email': team_data['email'],
        'slack_channel': team_data['slack_channel']
    }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

    if post_team_response.status_code != 201:
        print(f'Ошибка при создании команды {team_name}')
        continue

#    get_team_response = requests.post(oncall_url + '/api/v0/teams', json={
#        'name': team_name,
#        'scheduling_timezone': team_data['scheduling_timezone'],
#        'email': team_data['email'],
#        'slack_channel': team_data['slack_channel']
#    }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})
#
#    if get_team_response.status_code != 200:
#        print(f'Ошибка при создании команды {team_name}')
#        continue
#
#    response_json = get_team_response.json()
#    team_id = response_json['id']
    # Запрос на создание пользователей
    for user_data in team_data['users']:
        user_name = user_data['name']

        response = requests.post(f'{oncall_url}/api/v0/teams/{team_name}/users', json={
            'name': user_name,
            'full_name': user_data['full_name'],
            'phone_number': user_data['phone_number'],
            'email': user_data['email']
        }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

        if response.status_code != 201:
            print(f'Ошибка при создании пользователя {user_name} в команде {team_name}')
            continue

        user_id = response.json()['id']

        # Запрос на создание дежурств
        for duty_data in user_data['duty']:
            date = duty_data['date']
            role = duty_data['role']

            response = requests.post(f'{oncall_url}/api/teams/{team_name}/users/{user_id}/duty', json={
                'date': date,
                'role': role
            }, cookies=my_cookies, headers={'x-csrf-token': my_csrf_token})

            if response.status_code != 201:
                print(f'Ошибка при создании дежурства для пользователя {user_name} в команде {team_name} на дату {date}')

    print(f'Расписание успешно заполнено для команды {team_name}')
