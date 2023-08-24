from auth.schemas.entity import ChangeCredentials, Token, UserLogin, UserRegistration


USER_TO_REGISTER = [
    (UserRegistration(
        login='descartes',
        password='cogitoergosum',
        email='descartes@ratio.org'
    ),
    {
        'status_code': 201,
        'data': {'success':'Вы успешно зарегистрировались.'}
    }),
    (UserRegistration(
        login='wizard',
        password='iamtheblackwizard',
        email='wizard@ratio.org'
    ),
    {
        'status_code': 400,
        'data': {'error': 'Пользователь с логином wizard уже зарегистрирован.'}
    }),
    (UserRegistration(
        login='anna-varney',
        password='estutmirleid',
        email='wizard@ratio.org'
    ),
    {
        'status_code': 400,
        'data': {'error': 'Пользователь с email wizard@ratio.org уже зарегистрирован.'}
    }),
]

USER_TO_LOGIN = [
    (UserLogin(
        login='wizard',
        password='cogitoergosum'
    ),
    {
        'status_code': 200,
        'data': {'success': 'Вы вошли в свою учётную запись.'}
    }),
    (UserLogin(
        login='wizard',
        password='cogitoergoproxy'
    ),
    {
        'status_code': 401,
        'data': {'error': 'Логин или пароль не верен.'}
    })
    ]

USER_TO_LOGOUT = [
    (
        {'Authorization': 'Bearer my.supersecure.jwttoken'},
        {
        'status_code': 200,
        'data': {'success': 'Вы вышли из учётной записи.'}
        }
    ),
    (
        {'Authorization': 'Not-Bearer my.supersecure.jwttoken'},
        {
        'status_code': 401,
        'data': {'error': 'Недействительная схема авторизации. Авторизуйтесь снова.'}
        }
    ),
    (
        {'Authorization': ''},
        {
        'status_code': 401,
        'data': {'error': 'Отсутствует токен. Авторизуйтесь снова.'}
        }
    ),
    (
        {'Authorization': 'invalid.token'},
        {
        'status_code': 401,
        'data': {'error': 'Недействительный токен. Авторизуйтесь снова.'}
        }
    ),
]

REFRESH_TOKENS = [
    (
        Token(
            access_token='good.old.accesstoken',
            refresh_token='good.old.refreshtoken'
        ),
        {
        'status_code': 201,
        'data': {'access': 'new_access_token', 'refresh': 'new_refresh_token'}
        }
    ),
    (
        Token(
            access_token='good.old.accesstoken',
            refresh_token='bad.old.refreshtoken'
        ),
        {
        'status_code': 400,
        'data': {'error': 'Недействительный refresh-токен. Требуется пройти аутентификацию.'}
        }
    )
]

CHANGE_CREDENTIALS = [
    (
        ChangeCredentials(
            new_login='cool_new_login99',
            old_password='old_pass_123',
            new_password='seCuRe_nEw_pAss_987'
        ),
        {
        'status_code': 200,
        'data': {'success': 'Данные успешно изменены.'}
        }
    ),
    (
        ChangeCredentials(
            new_login='cool_new_login99',
            old_password='wrong_old_pass',
            new_password='seCuRe_nEw_pAss_987'
        ),
        {
        'status_code': 401,
        'data': {'error': 'Неверный старый пароль.'}
        }
    ),
    (
        ChangeCredentials(
            new_login='already_existing_login',
            old_password='old_pass_123',
            new_password='seCuRe_nEw_pAss_987'
        ),
        {
        'status_code': 409,
        'data': {'error': 'Указанный новый логин уже существует в системе.'}
        }
    )
]