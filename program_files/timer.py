# timer.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class TimerManager:
    MODES = {
        "pomodoro": 25 * 60,
        "short_break": 5 * 60,
        "long_break": 15 * 60,
        "stopwatch": None
    }

    def __init__(self, db, update_callback):
        self.db = db
        self.update_callback = update_callback
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        self.current_mode = "pomodoro"
        self.start_time = None
        self.session_id = None
        self.user_id = None
        self.running = False
        self.app_running = True

    def start_session(self, user_id, mode, update_ui):
        self.current_mode = mode
        self.user_id = user_id
        self.start_time = datetime.now()
        self.running = True
        
        self.session_id = self.db.create_session(
            user_id,
            self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            mode
        )
        
        if mode == "stopwatch":
            self.scheduler.add_job(
                self._update_stopwatch,
                'interval', 
                seconds=1,
                args=[update_ui]
            )
        else:
            self.scheduler.add_job(
                self._update_timer,
                'interval',
                seconds=1,
                args=[update_ui]
            )

    def _update_timer(self, update_ui):
        if self.running and self.app_running:
            elapsed = datetime.now() - self.start_time
            remaining = self.MODES[self.current_mode] - elapsed.seconds
            
            if remaining <= 0:
                self._complete_session()
                return
                
            mins, secs = divmod(remaining, 60)
            update_ui(f"{mins:02d}:{secs:02d}")

    def _update_stopwatch(self, update_ui):
        if self.running and self.app_running:
            try:
                elapsed = datetime.now() - self.start_time
                update_ui(str(elapsed).split(".")[0])
            except Exception as e:
                print(f"Ошибка обновления секундомера: {e}")

    def _complete_session(self):
        self.stop_timer()
        if self.current_mode == "pomodoro":
            self.db.add_achievement(
                self.user_id,
                "Помодоро завершено",
                "Успешно завершена 25-минутная сессия"
            )
            self.update_callback()

    def stop_timer(self):
        if self.running:
            self.running = False
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            self.db.update_session(
                self.session_id,
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
                int(duration)
            )
            self.scheduler.remove_all_jobs()
