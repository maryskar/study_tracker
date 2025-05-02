import unittest
from unittest.mock import patch, MagicMock
from program_files.api_client import ScheduleAPI
from datetime import datetime, timedelta
import requests  # Добавляем импорт requests

class TestScheduleAPI(unittest.TestCase):
    def setUp(self):
        # общий шаблон JSON для get_group_schedule
        self.sample = {
            "week": {"date_start": "2025-05-01", "date_end": "2025-05-07", "is_odd": True},
            "days": [
                {
                    "weekday": 1,
                    "date": "2025-05-01",
                    "lessons": [
                        {
                            "time_start": "09:00",
                            "time_end": "10:30",
                            "subject": "Math",
                            "typeObj": {"abbr": "Лекция"},
                            "auditories": [
                                {"building": {"name": "B"}, "name": "101"}
                            ],
                            "teachers": [{"full_name": "Иванов"}],
                            "lms_url": "http://lms.example.com"
                        }
                    ]
                },
                {
                    "weekday": 2,
                    "date": "2025-05-02",
                    "lessons": []
                }
            ]
        }

    @patch("program_files.api_client.requests.get")
    def test_get_group_info_success(self, mock_get):
        pass

    @patch("program_files.api_client.requests.get")
    def test_get_group_info_fallback(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("oops")
        fb = ScheduleAPI.get_group_info(999)
        self.assertIn("5130904/20104", fb["name"])

    @patch("program_files.api_client.requests.get")
    def test_get_group_schedule_success(self, mock_get):
        pass

    @patch("program_files.api_client.requests.get")
    def test_get_group_schedule_fallback(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("fail")
        fb = ScheduleAPI.get_group_schedule(123)
        self.assertIn("Математика", fb["days"][0]["lessons"][0]["subject"])