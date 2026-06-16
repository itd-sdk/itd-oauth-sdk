# ITD-OAuth-SDK

SDK для авторизации через ИТД OAuth для серверов.

## Установка
```bash
uv add itd-oauth-sdk
```

## Документация

### Client
```py
client = Client(
    client_id='ID клиента',
    client_secret='Секрет'
)
```
Получить свой токен можно на [официальном портале](https://dev.итд.tech) (если сайт не работает, можно обратиться в [ЛС канала @itdStatus](https://t.me/itdStatus?direct)). Также можно использовать [тестовые токены](https://github.com/itdPlus/ITD-OAuth-SDK/blob/main/docs/DEV-TOKENS.md).

### Получение ссылки на авторизацию
```py
url = client.get_authorization_url(
    scopes=['posts', 'users'],
    redirect_uri='localhost:1000'
)
```
[`scope`](#scope) - разрешения (требовать разрешение на комментирование, список постов и тд). `redirect_uri` устанавливается только если у вас тестовый `client_id` (на него перешлет pop up).

### Обмен кода
```py
res = client.exchange_code('123456789')
access_token = res['access_token']
refresh_token = res['refresh_token']
access_token_expires_in = res['expires_in']
```
Код приходит в каллбэке (`/auth/callback?code=xxx`).

### Обновить `access_token`
```py
res = client.refresh_token(refresh_token)
access_token = res['token']
access_token_expires_in = res['expires_in']
```

### Прокси
```py
res = client.proxy(
    access_token,
    'get',
    'posts',
    data=None,
    files=None,
    headers=None,
    json=None,
    params={'limit': 20},
    timeout=15
)
```
Отправить запрос через Oauth proxy. Есть практически все параметры из `requests.request()`.

### Прокси с авто-рефрешем
```py
res = client.proxy_with_refresh(
    refresh_token,
    'get',
    'posts',
    data=None,
    files=None,
    headers=None,
    json=None,
    params={'limit': 20},
    timeout=15,
    access_token=access_token
)
```
Тоже самое, что и `client.proxy()`, только с функцией обновления токена (вызовет `client.refresh_token` если истек).

### FastAPI роутер
```py
from fastapi import FastAPI

app = FastAPI()
app.include_router(client.get_router(
    prefix='/api/auth'
))

```
Добавляет эндпоинт `POST /api/auth` (или указанный в `prefix`), который принимает `code` и отдает `token`, а также записывает `itd_oauth_refresh` в куки.

Требуется установка FastAPI:
```bash
uv add itd-oauth-sdk[fastapi]
```

### FastAPI зависимость
```py
from fastapi import Depends

@app.get('me')
def api_get_me(token: dict = Depends(client.dependency)):
    return token  # {"sid":"08d7ef36-5914-45d5-95b2-f349d401fa48","clientId":"itd-oauth-dev","scope":["posts"],"sub":"587167e9-25ad-4948-afc0-2ee5bc9097ea","iat":1781596719,"exp":1781597919}
```
Добавляет данные пользователя (расшифрованный `access_token`) в контекст роута.

### Интеграция с itd-sdk
```py
from itd import ITDClient

ITDClient(config=client.sdk_config)
```
Изменяет целевой URL на OAuth прокси.

Требуется установка itd-sdk:
```bash
uv add itd-oauth-sdk[itd-sdk]
```

## Scope
Scope определяет к каким данным и действиям получает доступ приложение.  
Пользователь видит список запрошенных прав на странице подтверждения и может отклонить запрос.

## Доступные варианты

| Scope            | Разрешения                                                      |
|------------------|-----------------------------------------------------------------|
| `users`          | Просомотр и изменение профиля, подписки, блокировки             |
| `posts`          | Чтение, создание, изменение постов, лайки, репосты, комментарии |
| `comments`       | Создание, изменение и удаление комментариев, лайки              |
| `notifications`  | Просмотр уведомлений                                            |
| `files`          | Загрузка файлов                                                 |
| `reports`        | Отправка жалоб на контент                                       |
| `hashtags`       | Получние списка хэштэгов, поиск и получение постов по хэштэгу   |
| `search`         | Поиск пользователей и хэштэгов                                  |
| `subscription`   | Просмотр статуса подписки                                       |
| `verification`   | Просмотр статуса верификации аккаунта                           |
| `platform`       | Просмотр ченжлога и актуальных версий приложений                |
