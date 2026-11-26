import io
import base64
import threading

import tkinter as tk
from tkinter import messagebox

import requests

API_URL = "https://api.openweathermap.org/data/2.5/weather"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"

# Сюда вставьте свой ключ с сайта openweathermap.org
APPID = "ВАШ_API_КЛЮЧ"


def get_weather(city):
    """Запрос погоды. Возвращает (данные, None) или (None, текст ошибки)."""
    if APPID == "ВАШ_API_КЛЮЧ":
        return None, "Сначала вставьте свой API-ключ в начало программы."
    try:
        response = requests.get(
            API_URL,
            params={"q": city, "appid": APPID, "units": "metric",
                    "lang": "ru"},
            timeout=10)
        if response.status_code == 404:
            return None, f"Город '{city}' не найден."
        if response.status_code == 401:
            return None, ("Ключ отклонён сервером. Проверьте APPID "
                          "или подождите пару часов после регистрации "
                          "(ключ активируется не сразу).")
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "Сервер погоды не отвечает (таймаут)."
    except requests.exceptions.RequestException:
        return None, "Ошибка соединения. Проверьте интернет."


def get_icon(icon_code):
    """Скачиваем иконку погоды. Возвращает PhotoImage или None."""
    try:
        response = requests.get(ICON_URL.format(icon_code), timeout=10)
        response.raise_for_status()
        data = base64.b64encode(response.content)
        return tk.PhotoImage(data=data)
    except requests.exceptions.RequestException:
        return None


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Погода")
        self.geometry("420x420")
        self.resizable(False, False)

        self.icon_image = None  # чтобы картинка не удалилась сборщиком мусора

        top = tk.Frame(self)
        top.pack(pady=10)
        tk.Label(top, text="Город:").pack(side="left")
        self.entry = tk.Entry(top, width=25)
        self.entry.pack(side="left", padx=5)
        self.entry.bind("<Return>", lambda event: self.show_weather())
        tk.Button(top, text="Показать погоду",
                  command=self.show_weather).pack(side="left")

        self.info = tk.Label(self, text="", font=("Arial", 12),
                             justify="left")
        self.info.pack(pady=10)

        self.icon_label = tk.Label(self)
        self.icon_label.pack(pady=5)

        self.status = tk.Label(self, text="", fg="gray")
        self.status.pack(side="bottom", pady=5)

    def show_weather(self):
        city = self.entry.get().strip()
        if not city:
            messagebox.showwarning("Внимание", "Введите название города.")
            return
        self.status.configure(text="Загружаю данные...", fg="blue")
        self.info.configure(text="")
        self.icon_label.configure(image="")
        threading.Thread(target=self._load, args=(city,),
                         daemon=True).start()

    def _load(self, city):
        data, error = get_weather(city)
        self.after(0, self._done, data, error, city)

    def _done(self, data, error, city):
        if error:
            self.status.configure(text=error, fg="red")
            return
        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        text = (f"Погода в городе {data.get('name', city)}:\n"
                f"{weather.get('description', '').capitalize()}\n"
                f"Температура: {main.get('temp')} °C "
                f"(ощущается как {main.get('feels_like')} °C)\n"
                f"Влажность: {main.get('humidity')} %\n"
                f"Ветер: {wind.get('speed', 0)} м/с")
        self.info.configure(text=text, fg="black")
        self.status.configure(text="Готово", fg="green")
        icon = get_icon(weather.get("icon", "01d"))
        if icon:
            self.icon_image = icon
            self.icon_label.configure(image=icon)


if __name__ == "__main__":
    WeatherApp().mainloop()
