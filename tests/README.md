# 🧪 Юнит-тесты для проекта "Трекер Учёбы"

Этот каталог содержит юнит-тесты для проверки корректности работы основных модулей проекта: аутентификация, база данных, API мотивации, API времени и API расписания.

## 📁 Содержание файлов

- **`test_auth.py`** — проверка регистрации и входа пользователя, обработка ошибок (неверный пароль, дубликаты).
- **`test_database.py`** — тесты добавления, удаления и поиска пользователей, сессий и достижений в SQLite базе данных.
- **`test_api_motivation.py`** — проверка получения мотивационной цитаты из внешнего API (с использованием подмены ответа).
- **`test_api_time.py`** — тесты получения текущего времени из API и правильности обработки данных.
- **`test_api_schedule.py`** — проверка получения и обработки расписания по имени пользователя (через API-запрос).

## ▶️ Как запустить тесты

В терминале из корня проекта: **`"C:\...\study_tracker"`**

```bash
python -m unittest discover -s tests
```
Для более подробного вывода:
```bash
python -m unittest discover -s tests -v
```
## 📝 Примечания

Тесты API используют unittest.mock для подмены внешних запросов (интернет не нужен).

Все тесты изолированы и не зависят друг от друга.

База данных используется временно и очищается между тесcами.

## ✅ Ожидаемый результат

-------------------------------------------------------c--------------
```
Ran 17 tests in 1.194s

OK
```
и подробный результат:
```
test_get_quote_fallback (test_api_motivation.TestMotivationAPI.test_get_quote_fallback) ... ok
test_get_quote_success (test_api_motivation.TestMotivationAPI.test_get_quote_success) ... ok
test_get_group_info_fallback (test_api_schedule.TestScheduleAPI.test_get_group_info_fallback) ... 
ok
test_get_group_info_success (test_api_schedule.TestScheduleAPI.test_get_group_info_success) ... ok
test_get_group_schedule_fallback (test_api_schedule.TestScheduleAPI.test_get_group_schedule_fallback) ...
ok
test_get_group_schedule_success (test_api_schedule.TestScheduleAPI.test_get_group_schedule_success) ... ok
test_get_formatted_time_fallback (test_api_time.TestWorldTimeAPI.test_get_formatted_time_fallback) ... ok
test_get_formatted_time_success (test_api_time.TestWorldTimeAPI.test_get_formatted_time_success) ... ok
test_login_nonexistent_user (test_auth.TestAuthManager.test_login_nonexistent_user) ... ok
test_login_success_and_token (test_auth.TestAuthManager.test_login_success_and_token) ... ok
test_login_wrong_password (test_auth.TestAuthManager.test_login_wrong_password) ... ok
test_register_user_success (test_auth.TestAuthManager.test_register_user_success) ... ok
test_achievements (test_database.TestDatabase.test_achievements) ... ok
test_create_and_get_user (test_database.TestDatabase.test_create_and_get_user) ... ok
test_create_session_and_get (test_database.TestDatabase.test_create_session_and_get) ... ok
test_create_user_duplicate (test_database.TestDatabase.test_create_user_duplicate) ... ok
test_month_sessions_filter (test_database.TestDatabase.test_month_sessions_filter) ... ok
```