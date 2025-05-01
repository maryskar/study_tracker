# main.py
import customtkinter as ctk
import webbrowser
from datetime import datetime
from auth import AuthManager
from timer import TimerManager
from database import Database
from api_client import MotivationAPI, WorldTimeAPI, ScheduleAPI
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar
import json
import tkinter.messagebox as mb
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StudyTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.app_running = True
        self.title("Трекер Учёбы - Группа 5130904/20104")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        self.db = Database()
        self.auth = AuthManager(self.db)
        self.timer_manager = TimerManager(self.db, self.update_stats)
        self.current_user = None
        self.app_settings = self.load_settings()
        
        self.configure_colors()
        self.show_auth_screen()
        
    def configure_colors(self):
        self.colors = {
            "bg": "#2E2E2E",
            "accent": "#2ECC71",
            "secondary": "#3498DB",
            "text": "#ECF0F1"
        }
        
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except:
            return {"theme": "blue", "appearance_mode": "dark"}
        
    def destroy(self):
        self.app_running = False
        super().destroy()
            
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.app_settings, f)

    def show_auth_screen(self):
        self.clear_window()
        
        auth_frame = ctk.CTkFrame(self, fg_color=self.colors["bg"])
        auth_frame.pack(pady=100, padx=200, fill="both", expand=True)
        
        logo = ctk.CTkLabel(auth_frame, text="📚 Трекер Учёбы", 
                          font=("Arial", 36, "bold"), 
                          text_color=self.colors["accent"])
        logo.pack(pady=40)
        
        try:
            current_time = WorldTimeAPI.get_formatted_time()
            time_label = ctk.CTkLabel(auth_frame, 
                                     text=f"⏰ Текущее время: {current_time}", 
                                     font=("Arial", 14))
            time_label.pack(pady=10)
        except Exception as e:
            print(f"Ошибка API времени: {e}")

        self.auth_tabs = ctk.CTkTabview(auth_frame, 
                                      fg_color=self.colors["bg"], 
                                      segmented_button_selected_color=self.colors["accent"])
        self.auth_tabs.pack(fill="x", padx=50)
        
        login_tab = self.auth_tabs.add(" Вход ")
        self.setup_login_tab(login_tab)
        
        register_tab = self.auth_tabs.add(" Регистрация ")
        self.setup_register_tab(register_tab)
        
    def setup_login_tab(self, tab):
        ctk.CTkLabel(tab, text="Логин:").pack(pady=5)
        self.login_user = ctk.CTkEntry(tab)
        self.login_user.pack(pady=5, fill="x")
        
        ctk.CTkLabel(tab, text="Пароль:").pack(pady=5)
        self.login_pass = ctk.CTkEntry(tab, show="*")
        self.login_pass.pack(pady=5, fill="x")
        
        ctk.CTkButton(tab, text="Войти", 
                     command=self.handle_login,
                     fg_color=self.colors["accent"]).pack(pady=20)
        
    def setup_register_tab(self, tab):
        ctk.CTkLabel(tab, text="Логин:").pack(pady=5)
        self.reg_user = ctk.CTkEntry(tab)
        self.reg_user.pack(pady=5, fill="x")
        
        ctk.CTkLabel(tab, text="Пароль:").pack(pady=5)
        self.reg_pass = ctk.CTkEntry(tab, show="*")
        self.reg_pass.pack(pady=5, fill="x")
        
        ctk.CTkButton(tab, text="Зарегистрироваться", 
                     command=self.handle_register,
                     fg_color=self.colors["secondary"]).pack(pady=20)
        
    def show_main_app(self):
        self.clear_window()
        
        main_container = ctk.CTkFrame(self, fg_color=self.colors["bg"])
        main_container.pack(fill="both", expand=True)
        
        nav_frame = ctk.CTkFrame(main_container, width=200, 
                                fg_color="#34495E", 
                                corner_radius=15)
        nav_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        nav_buttons = [
            ("⏱ Таймер", self.show_timer),
            ("📅 Календарь", self.show_calendar),
            ("🏆 Достижения", self.show_achievements),
            ("🎨 Оформление", self.show_appearance_settings),
            ("🔔 Расписание группы", self.show_schedule),
            ("🚪 Выход", self.confirm_logout)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(nav_frame, text=text,
                               command=command,
                               fg_color="transparent",
                               hover_color="#2C3E50",
                               anchor="w")
            btn.pack(fill="x", pady=5, padx=10)
            
        self.content_frame = ctk.CTkFrame(main_container, 
                                        fg_color=self.colors["bg"])
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        self.show_timer()
        
    def show_timer(self):
        self.clear_content()
        
        timer_frame = ctk.CTkFrame(self.content_frame)
        timer_frame.pack(pady=50, padx=50, fill="both", expand=True)
        
        self.timer_label = ctk.CTkLabel(timer_frame, 
                                       text="25:00", 
                                       font=("Arial", 48))
        self.timer_label.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(timer_frame)
        btn_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(btn_frame, 
                                      text="Старт Помодоро", 
                                      command=lambda: self.start_session("pomodoro"))
        self.start_btn.pack(side="left", padx=10)
        
        self.stopwatch_btn = ctk.CTkButton(btn_frame,
                                          text="Секундомер",
                                          command=lambda: self.start_session("stopwatch"))
        self.stopwatch_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(btn_frame, 
                                     text="Стоп", 
                                     state="disabled",
                                     command=self.stop_timer)
        self.stop_btn.pack(side="left", padx=10)
        
        try:
            quote = MotivationAPI.get_quote()
            quote_label = ctk.CTkLabel(timer_frame, 
                                      text=f'"{quote}"',
                                      wraplength=600,
                                      font=("Arial", 14, "italic"))
            quote_label.pack(pady=20)
        except Exception as e:
            print(f"Ошибка API цитат: {e}")

    def show_calendar(self):
        self.clear_content()
        
        calendar_frame = ctk.CTkFrame(self.content_frame)
        calendar_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)
        
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        sessions = self.db.get_month_sessions(self.current_user["id"], now.month, now.year)
        
        ax.set_title(f"Календарь занятий за {now.strftime('%B %Y')}")
        ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, master=calendar_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_achievements(self):
        self.clear_content()
        
        achievements_frame = ctk.CTkFrame(self.content_frame)
        achievements_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        achievements = self.db.get_achievements(self.current_user["id"])
        
        ctk.CTkLabel(achievements_frame, 
                    text="Ваши достижения", 
                    font=("Arial", 24)).pack(pady=10)
        
        if achievements:
            for ach in achievements:
                ctk.CTkLabel(achievements_frame, 
                            text=f"🏆 {ach[2]} - {ach[3]}", 
                            font=("Arial", 14)).pack(pady=5)
        else:
            ctk.CTkLabel(achievements_frame, 
                        text="Пока нет достижений", 
                        font=("Arial", 14)).pack(pady=20)

    def show_appearance_settings(self):
        self.clear_content()
        
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(settings_frame, 
                    text="Цветовая тема", 
                    font=("Arial", 18)).pack(pady=10)
        
        theme_colors = ["green", "blue", "dark-blue", "purple"]
        self.theme_selector = ctk.CTkSegmentedButton(
            settings_frame,
            values=theme_colors,
            command=self.change_theme
        )
        self.theme_selector.pack(pady=10)
        self.theme_selector.set(self.app_settings.get("theme", "blue"))
        
        ctk.CTkLabel(settings_frame, 
                    text="Режим оформления", 
                    font=("Arial", 18)).pack(pady=10)
        
        self.mode_switch = ctk.CTkSwitch(
            settings_frame,
            text="Темная тема" if ctk.get_appearance_mode() == "dark" else "Светлая тема",
            command=self.toggle_theme_mode
        )
        self.mode_switch.pack(pady=10)
        
    def change_theme(self, value):
        ctk.set_default_color_theme(value)
        self.app_settings["theme"] = value
        self.save_settings()
        self.show_main_app()
        
    def toggle_theme_mode(self):
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.app_settings["appearance_mode"] = new_mode
        self.save_settings()
        self.show_main_app()

    def show_schedule(self):
        self.clear_content()

        schedule_frame = ctk.CTkFrame(self.content_frame)
        schedule_frame.pack(pady=20, padx=20, fill="both", expand=True)

        try:
            # Получаем данные
            group_info = ScheduleAPI.get_group_info(40520)
            schedule = ScheduleAPI.get_group_schedule(40520)

            # Заголовок
            header_frame = ctk.CTkFrame(schedule_frame)
            header_frame.pack(fill="x", pady=10)

            # Информация о группе
            group_info_label = ctk.CTkLabel(
                header_frame,
                text=f"👥 Группа: {group_info['name']} | 🏛 Институт компьютерных наук и технологий | 🎓 Курс: 3",
                font=("Arial", 14)
            )
            group_info_label.pack(side="left", padx=10)

            # Информация о неделе
            week_type = "Нечетная" if schedule["week"]["is_odd"] else "Четная"  #  Преобразование bool в строку
            week_label = ctk.CTkLabel(
                header_frame,
                text=f"📅 {schedule['week']['date_start']} - {schedule['week']['date_end']} ({week_type})",
                font=("Arial", 14)
            )
            week_label.pack(side="right", padx=10)

            # Контейнер для дней с прокруткой
            days_container = ctk.CTkScrollableFrame(schedule_frame, height=600)
            days_container.pack(fill="both", expand=True, pady=10)

            # Маппинг номеров дней недели
            weekday_names = {
                1: "Понедельник",
                2: "Вторник",
                3: "Среда",
                4: "Четверг",
                5: "Пятница",
                6: "Суббота",
                7: "Воскресенье"
            }

            for day in schedule["days"]:
                day_frame = ctk.CTkFrame(days_container)
                day_frame.pack(fill="x", pady=5, padx=5)

                # Заголовок дня
                day_header = ctk.CTkFrame(day_frame, fg_color="#3A7EBF")
                day_header.pack(fill="x")

                formatted_date = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
                weekday_name = weekday_names.get(day["weekday"], "День")

                ctk.CTkLabel(
                    day_header,
                    text=f"📌 {weekday_name} ({formatted_date})",
                    font=("Arial", 16, "bold")
                ).pack(side="left", padx=10, pady=5)

                if not day["lessons"]:
                    ctk.CTkLabel(
                        day_frame,
                        text="Нет занятий",
                        font=("Arial", 14)
                    ).pack(pady=10)
                    continue

                for lesson in day["lessons"]:
                    lesson_frame = ctk.CTkFrame(day_frame, fg_color="#2b2b2b")
                    lesson_frame.pack(fill="x", pady=3, padx=10)

                    # Временной блок
                    time_frame = ctk.CTkFrame(lesson_frame)
                    time_frame.pack(side="left", padx=5)
                    ctk.CTkLabel(
                        time_frame,
                        text=f"🕒 {lesson['time']}\n{lesson['type']}",
                        fg_color="#2b2b2b",
                        font=("Arial", 12)
                    ).pack()

                    # Основная информация
                    info_frame = ctk.CTkFrame(lesson_frame)
                    info_frame.pack(side="left", padx=10, fill="x", expand=True)

                    # Название предмета
                    ctk.CTkLabel(
                        info_frame,
                        text=lesson["subject"],
                        font=("Arial", 14, "bold")
                    ).pack(anchor="w")

                    # Детали
                    details_frame = ctk.CTkFrame(info_frame)
                    details_frame.pack(fill="x")

                    # Преподаватель
                    ctk.CTkLabel(
                        details_frame,
                        text=f"👤 {lesson['teacher']}",
                        font=("Arial", 12)
                    ).pack(side="left")

                    # Аудитория
                    ctk.CTkLabel(
                        details_frame,
                        text=f"📍 {lesson['room']}",
                        font=("Arial", 12)
                    ).pack(side="left", padx=20)

                    # Ссылка на LMS
                    if lesson.get("lms_url"):
                        ctk.CTkButton(
                            info_frame,
                            text="🌐 Курс в LMS",
                            fg_color="transparent",
                            hover_color="#e0e0e0",
                            text_color="#0066cc",
                            command=lambda url=lesson["lms_url"]: webbrowser.open(url)
                        ).pack(side="right")

        except Exception as e:
            print(f"Ошибка отображения расписания: {e}")
            ctk.CTkLabel(
                schedule_frame,
                text="Не удалось загрузить расписание",
                font=("Arial", 16)
            ).pack(pady=50)

    def confirm_logout(self):
        if mb.askyesno("Подтверждение", "Вы уверены, что хотите выйти?"):
            self.perform_logout()
            
    def perform_logout(self):
        self.current_user = None
        self.timer_manager.stop_timer()
        self.show_auth_screen()
        
    def handle_login(self):
        username = self.login_user.get()
        password = self.login_pass.get()
        
        if user := self.auth.login(username, password):
            self.current_user = user
            self.show_main_app()
        else:
            mb.showerror("Ошибка", "Неверные учетные данные!")
            
    def handle_register(self):
        username = self.reg_user.get()
        password = self.reg_pass.get()
        
        if self.auth.register(username, password):
            mb.showinfo("Успех", "Регистрация прошла успешно!")
            self.auth_tabs.set(" Вход ")
        else:
            mb.showerror("Ошибка", "Имя пользователя уже существует!")
            
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
            
    def start_session(self, mode):
        self.start_btn.configure(state="disabled")
        self.stopwatch_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.timer_manager.start_session(
            self.current_user["id"], 
            mode, 
            self.update_timer_display
        )
        
    def update_timer_display(self, time_str):
        self.timer_label.configure(text=time_str)
        
    def stop_timer(self):
        self.timer_manager.stop_timer()
        self.start_btn.configure(state="normal")
        self.stopwatch_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.update_stats()
        
    def update_stats(self):
        if hasattr(self, "stats_frame"):
            self.show_stats()

if __name__ == "__main__":
    app = StudyTrackerApp()
    app.mainloop()
