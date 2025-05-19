from locust import HttpUser, task, between, events
import random
import time
from program_files.auth import AuthManager
from program_files.database import Database
from program_files.timer import TimerManager
from program_files.api_client import MotivationAPI, ScheduleAPI


class StudyTrackerLoadTest(HttpUser):
    host = "http://localhost"  
    wait_time = between(0.5, 2)  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()
        self.auth = AuthManager(self.db)
        self.user_id = None
        self.username = None
        self.password = "testpassword"

    def on_start(self):
        self.username = f"testuser_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
        
        registered = self.auth.register(self.username, self.password)
        if not registered:
            user = self.auth.login(self.username, self.password)
        else:
            user = self.auth.login(self.username, self.password)

        if isinstance(user, tuple) and len(user) > 0:
            self.user_id = user[0]
        elif isinstance(user, dict) and 'id' in user:
            self.user_id = user['id']
        elif hasattr(user, '__getitem__') and hasattr(user, '__iter__'):
            try:
                self.user_id = user[0]  
            except IndexError:
                print("Ошибка: Не удалось получить ID пользователя")
                self.user_id = None
        else:
            print("Ошибка: Неверные данные пользователя")
            self.user_id = None

    @task(3)
    def login_and_start_session(self):
        if not self.user_id:
            return

        start_time = time.time()
        exception = None
        response_length = 0

        try:
            timer = TimerManager(self.db, lambda x: None)
            timer.start_session(self.user_id, "pomodoro", lambda x: None)
            time.sleep(random.uniform(1, 3))
            timer.stop_timer()
        except Exception as e:
            exception = e
        finally:
            total_time = (time.time() - start_time) * 1000
            events.request.fire(
                request_type="POST",
                name="/pomodoro/session",
                response_time=total_time,
                response_length=response_length,
                exception=exception
            )

    @task(2)
    def get_achievements(self):
        if not self.user_id:
            return

        start_time = time.time()
        exception = None
        response_length = 0

        try:
            achievements = self.db.get_achievements(self.user_id)
            response_length = len(achievements)
        except Exception as e:
            exception = e
        finally:
            total_time = (time.time() - start_time) * 1000
            events.request.fire(
                request_type="GET",
                name="/achievements",
                response_time=total_time,
                response_length=response_length,
                exception=exception
            )

    @task(1)
    def fetch_schedule(self):
        start_time = time.time()
        exception = None
        response_length = 0

        try:
            ScheduleAPI.get_group_schedule(40520)
        except Exception as e:
            exception = e
        finally:
            total_time = (time.time() - start_time) * 1000
            events.request.fire(
                request_type="GET",
                name="/api/group-schedule",
                response_time=total_time,
                response_length=response_length,
                exception=exception
            )

    @task(1)
    def fetch_quote(self):
        start_time = time.time()
        exception = None
        response_length = 0

        try:
            quote = MotivationAPI.get_quote()
            response_length = len(quote)
        except Exception as e:
            exception = e
        finally:
            total_time = (time.time() - start_time) * 1000
            events.request.fire(
                request_type="GET",
                name="/api/quote",
                response_time=total_time,
                response_length=response_length,
                exception=exception
            )