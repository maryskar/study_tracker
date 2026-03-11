# Unit Tests

Набор модульных тестов для `program_files`.

## Файлы
- `tests/test_auth.py`
- `tests/test_database.py`
- `tests/test_api_clients.py`
- `tests/test_timer.py`

## Покрытие и отчеты
Тесты запускаются с порогом покрытия 80% через `pytest.ini`.

## Локальный запуск
```bash
pytest tests --cov=program_files --cov-fail-under=80
```

## Что проверяется
- позитивные и негативные сценарии
- эквивалентные классы
- граничные значения
- обработка ошибок и fallback
