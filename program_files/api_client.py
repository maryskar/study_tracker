# api_client.py
import requests
from datetime import datetime, timedelta
from datetime import datetime
import json
import customtkinter as ctk
import webbrowser

class MotivationAPI:
    @staticmethod
    def get_quote():
        try:
            response = requests.get("https://api.quotable.io/random", timeout=3)
            return response.json()["content"]
        except:
            return "Сосредоточьтесь и продолжайте учиться!"

class WorldTimeAPI:
    @staticmethod
    def get_formatted_time():
        try:
            response = requests.get("http://worldtimeapi.org/api/ip", timeout=3)
            data = response.json()
            dt = datetime.fromisoformat(data["datetime"])
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ScheduleAPI:
    BASE_URL = "https://ruz.spbstu.ru/api/v1/ruz"

    @staticmethod
    def get_group_info(group_id):
        try:
            response = requests.get(
                f"{ScheduleAPI.BASE_URL}/groups/{group_id}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                "name": data.get("name", "Неизвестно"),
                "faculty": data.get("faculty", {}).get("name", "Неизвестно"),
                "course": data.get("course", "Неизвестно")
            }
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения информации о группе: {e}")
            return {
                "name": "5130904/20104",
                "faculty": "Институт компьютерных наук и кибербезопасности",
                "course": 3
            }

    @staticmethod
    def get_group_schedule(group_id, date=None):
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            response = requests.get(
                f"{ScheduleAPI.BASE_URL}/scheduler/{group_id}",
                headers={"User-Agent": "Mozilla/5.0"},
                params={"date": date},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            print(json.dumps(data, indent=4, ensure_ascii=False))  #  Для отладки

            schedule = {
                "week": {
                    "date_start": data.get("week", {}).get("date_start"),
                    "date_end": data.get("week", {}).get("date_end"),
                    "is_odd": data.get("week", {}).get("is_odd")
                },
                "days": []
            }

            for day in data.get("days", []):
                day_data = {
                    "weekday": day.get("weekday"),
                    "date": day.get("date"),
                    "lessons": []
                }

                for lesson in day.get("lessons", []):
                    room = "Не указано"
                    if lesson.get("auditories"):
                        auditories = lesson.get("auditories")
                        if auditories and isinstance(auditories, list) and len(auditories) > 0:
                            first_auditory = auditories[0]
                            building_name = first_auditory.get("building", {}).get("name", "")
                            auditory_name = first_auditory.get("name", "")
                            room = f"{building_name} {auditory_name}".strip()

                    teacher = "Не указан"
                    if lesson.get("teachers"):
                        teachers = lesson.get("teachers")
                        if teachers and isinstance(teachers, list) and len(teachers) > 0:
                            first_teacher = teachers[0]
                            teacher = first_teacher.get("full_name", teacher)

                    lesson_data = {
                        "time": f"{lesson.get('time_start', '')} - {lesson.get('time_end', '')}",
                        "subject": lesson.get("subject", "Не указано"),
                        "type": lesson.get("typeObj", {}).get("abbr", ""),
                        "room": room,
                        "teacher": teacher,
                        "lms_url": lesson.get("lms_url", "") #  Добавлено извлечение lms_url
                    }
                    day_data["lessons"].append(lesson_data)

                schedule["days"].append(day_data)

            return schedule

        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения расписания: {e}")
            return {
                "week": {
                    "is_odd": False,
                    "date_start": datetime.now().strftime("%Y.%m.%d"),
                    "date_end": (datetime.now() + timedelta(days=7)).strftime("%Y.%m.%d")
                },
                "days": [
                    {
                        "weekday": 1,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "lessons": [
                            {
                                "time": "09:00 - 10:30",
                                "subject": "Математика",
                                "type": "Лекция",
                                "room": "A101",
                                "teacher": "Иванов И.И."
                            }
                        ]
                    }
                ]
            }
