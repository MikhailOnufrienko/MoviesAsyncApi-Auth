from auth.schemas.entity import UserLogin, UserRegistration


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