import io
import threading

import tkinter as tk
from tkinter import messagebox

import requests
from PIL import Image, ImageTk

CAT_API = "https://api.thecatapi.com/v1/images/search"
DOG_API = "https://dog.ceo/api/breeds/image/random"


def get_url(kind):
    """Получаем ссылку на случайную картинку. (url, None) или (None, ошибка)."""
    try:
        response = requests.get(CAT_API if kind == "cat" else DOG_API,
                                timeout=10)
        response.raise_for_status()
        data = response.json()
        if kind == "cat":
            url = data[0].get("url")
        else:
            url = data.get("message")
        if not url:
            return None, "Сервис не вернул ссылку на картинку."
        return url, None
    except requests.exceptions.RequestException:
        return None, "Ошибка соединения. Проверьте интернет."


def download_image(url):
    """Скачиваем картинку и делаем из неё объект для Tkinter."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        # Приводим к разумному размеру, чтобы картинка влезла в окно
        image.thumbnail((420, 320))
        return ImageTk.PhotoImage(image)
    except requests.exceptions.RequestException:
        return None
    except OSError:
        return None


class PetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Случайные коты и собаки")
        self.geometry("500x520")
        self.resizable(False, False)

        self.photo = None  # чтобы картинка не удалилась сборщиком мусора

        tk.Label(self, text="Случайные питомцы",
                 font=("Arial", 14, "bold")).pack(pady=8)

        buttons = tk.Frame(self)
        buttons.pack(pady=5)
        tk.Button(buttons, text="Получить кота", width=18,
                  command=lambda: self.show("cat")).pack(side="left", padx=10)
        tk.Button(buttons, text="Получить собаку", width=18,
                  command=lambda: self.show("dog")).pack(side="left", padx=10)

        self.image_label = tk.Label(self, text="",
                                    width=58, height=18)
        self.image_label.pack(pady=8)

        self.status = tk.Label(self, text="Нажмите кнопку, чтобы получить питомца",
                               fg="gray")
        self.status.pack(pady=5)

    def show(self, kind):
        self.status.configure(text="Загружаю картинку...", fg="blue")
        self.image_label.configure(text="...")
        threading.Thread(target=self._load, args=(kind,),
                         daemon=True).start()

    def _load(self, kind):
        url, error = get_url(kind)
        if error:
            self.after(0, self._error, error)
            return
        photo = download_image(url)
        self.after(0, self._done, photo, kind)

    def _error(self, error):
        self.image_label.configure(text="")
        self.status.configure(text=error, fg="red")

    def _done(self, photo, kind):
        if photo is None:
            self._error("Не удалось скачать картинку. Попробуйте ещё раз.")
            return
        self.photo = photo
        self.image_label.configure(image=photo, text="")
        self.status.configure(
            text="Готово! Нажмите кнопку ещё раз для новой картинки.",
            fg="green")


if __name__ == "__main__":
    PetApp().mainloop()
