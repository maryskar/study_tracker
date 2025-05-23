# study_tracker
Приложение для отслеживания времени, проведенного за учебой, и концентрации внимания, расписанием учебы  

## Тема проекта: 
**⏱️ Трекер учебной активности с расписанием группы**    

## Состав группы:  
Потапова Марина Александровна 5130904/20104  
Скарлыгина Мария Дмитриевна 5130904/20104  
Чулков Леонтий Андреевич 5130904/20104  
Фесенко Иван Николаевич 5130904/20104  

## Ссылка на репозиторий:  
https://github.com/maryskar/study_tracker.git  
**Файлы реализации:**  
- папка разработки [program_files](program_files/); описание [program_files/README.md](program_files/README.md);  
- папка тестирования [tests](tests/); описание [tests/README.md](tests/README.md);
  
**Отчет по проекту:** [ОТЧЕТ ПДФ](КОНСТРУИРОВАНИЕ_ПО_5130904_20104.pdf)  
  
# Технологический стек

### Клиентская часть (Desktop приложение)
- **Язык программирования**: Python 3.8+
- **GUI Framework**: 
  - `customtkinter==5.2.2` - современная версия Tkinter с Material Design элементами
  - `matplotlib==3.8.4` - визуализация статистики

### Работа с данными
- **База данных**: SQLite (встроенная, файл study.db)
- **ORM**: Нативный SQL-запросы
- **Кэширование**: Локальное хранение настроек в JSON

### Внешние сервисы
- **Расписание**: API Политеха (`ruz.spbstu.ru`)
- **Время**: WorldTimeAPI (`worldtimeapi.org`)
- **Мотивация**: Quotable API (`api.quotable.io`)

### Дополнительные компоненты
- **Планировщик**: APScheduler для работы с таймерами
- **Безопасность**: 
  - `bcrypt==4.0.1` - хеширование паролей
  - `python-jose==3.3.0` - JWT-токены

### Сборка и зависимости
- **Менеджер пакетов**: pip (requirements.txt)
- **Верстка**: Нативные компоненты CTk с кастомными стилями

## Архитектура приложения

### Основные модули
1. **main.py** - ядро приложения, интерфейс
2. **database.py** - работа с SQLite
3. **auth.py** - система аутентификации
4. **timer.py** - логика таймеров
5. **api_client.py** - интеграция с внешними API

### Ключевые функции
- 🔐 Авторизация/регистрация пользователей
- ⏱️ Таймер Pomodoro и секундомер
- 📅 Интеграция с расписанием Политеха (группа 5130904/20104)
- 📊 Визуализация учебной статистики
- 🏆 Система достижений
- 🎨 Кастомизация интерфейса

## Особенности реализации
1. **Офлайн-работа** - локальное хранение всех данных
2. **Адаптивный дизайн** - поддержка разных разрешений экрана
3. **Безопасность** - хеширование паролей + JWT
4. **Интеграция с API** - автоматическое обновление расписания

## Установка
```bash
git clone https://github.com/maryskar/study_tracker.git
cd study-tracker\program_files
pip install -r requirements.txt
python main.py
```
