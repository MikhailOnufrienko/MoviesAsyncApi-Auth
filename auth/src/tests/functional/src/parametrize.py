



from auth.schemas.entity import UserRegistration


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