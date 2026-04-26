# Unit Tests

Набор модульных тестов для `program_files`.

## Структура
- `tests/positive/` - позитивные сценарии (happy path)
- `tests/negative/` - негативные сценарии (ошибки, fallback, невалидный ввод)

## Покрытие и отчеты
Тесты запускаются с порогом покрытия 80% через `pytest.ini`.

## Локальный запуск
```bash
pytest tests --cov=program_files --cov-fail-under=80
```

Отдельный запуск позитивных сценариев:
```bash
pytest tests/positive
```

Отдельный запуск негативных сценариев:
```bash
pytest tests/negative
```

## Что проверяется
- позитивные и негативные сценарии
- эквивалентные классы
- граничные значения
- обработка ошибок и fallback
