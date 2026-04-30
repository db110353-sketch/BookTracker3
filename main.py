import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.root.configure(bg='#f0f0f0')
        
        # Переменные
        self.password_length = tk.IntVar(value=12)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)
        
        # История паролей
        self.history_file = "password_history.json"
        self.password_history = []
        self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Генерация первого пароля
        self.generate_password()
    
    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных паролей", 
                                font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="15")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Ползунок длины пароля
        length_frame = ttk.Frame(settings_frame)
        length_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(length_frame, text="Длина пароля:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.length_scale = ttk.Scale(length_frame, from_=4, to=32, variable=self.password_length, 
                                      orient=tk.HORIZONTAL, command=self.update_length_label)
        self.length_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.length_label = ttk.Label(length_frame, text="12", font=('Arial', 10, 'bold'))
        self.length_label.pack(side=tk.LEFT)
        
        # Чекбоксы
        checkbox_frame = ttk.Frame(settings_frame)
        checkbox_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        ttk.Checkbutton(checkbox_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.use_uppercase).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="Строчные буквы (a-z)", 
                       variable=self.use_lowercase).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(checkbox_frame, text="Спецсимволы (!@#$%^&*()_+-=[]{}|;:,.<>?)", 
                       variable=self.use_special).pack(anchor=tk.W, pady=2)
        
        # Информационная метка
        self.info_label = ttk.Label(settings_frame, text="✅ Выберите хотя бы один тип символов", 
                                    foreground='blue')
        self.info_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Фрейм сгенерированного пароля
        password_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding="15")
        password_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                       font=('Courier', 14), state='readonly')
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления
        button_frame = ttk.Frame(password_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🔒 Сгенерировать", command=self.generate_password).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Копировать", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Сохранить в историю", command=self.save_to_history).pack(side=tk.LEFT)
        
        # Таблица истории
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Создание Treeview для истории
        columns = ('#', 'Пароль', 'Длина', 'Дата создания')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        
        # Настройка колонок
        self.history_tree.heading('#', text='#')
        self.history_tree.heading('Пароль', text='Пароль')
        self.history_tree.heading('Длина', text='Длина')
        self.history_tree.heading('Дата создания', text='Дата создания')
        
        self.history_tree.column('#', width=40, anchor='center')
        self.history_tree.column('Пароль', width=250)
        self.history_tree.column('Длина', width=60, anchor='center')
        self.history_tree.column('Дата создания', width=150, anchor='center')
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(history_buttons_frame, text="🗑️ Очистить историю", 
                  command=self.clear_history).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(history_buttons_frame, text="🔄 Обновить историю", 
                  command=self.refresh_history_display).pack(side=tk.RIGHT)
        
        # Обновление отображения истории
        self.refresh_history_display()
    
    def update_length_label(self, *args):
        """Обновление метки длины пароля"""
        self.length_label.config(text=str(self.password_length.get()))
    
    def get_character_set(self):
        """Получение набора символов на основе выбранных опций"""
        characters = ''
        
        if self.use_uppercase.get():
            characters += string.ascii_uppercase
        if self.use_lowercase.get():
            characters += string.ascii_lowercase
        if self.use_digits.get():
            characters += string.digits
        if self.use_special.get():
            characters += string.punctuation
        
        return characters
    
    def generate_password(self):
        """Генерация случайного пароля"""
        characters = self.get_character_set()
        
        # Проверка, что выбран хотя бы один тип символов
        if not characters:
            self.info_label.config(text="⚠️ Ошибка: Выберите хотя бы один тип символов!", 
                                  foreground='red')
            self.password_var.set("")
            return False
        
        self.info_label.config(text="✅ Настройки действительны", foreground='green')
        
        length = self.password_length.get()
        
        # Проверка минимальной и максимальной длины
        if length < 4:
            length = 4
            self.password_length.set(4)
            self.length_label.config(text="4")
        elif length > 32:
            length = 32
            self.password_length.set(32)
            self.length_label.config(text="32")
        
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Проверка, что пароль содержит все выбранные типы символов
        # (дополнительная безопасность для коротких паролей)
        max_attempts = 10
        for _ in range(max_attempts):
            valid = True
            if self.use_uppercase.get() and not any(c.isupper() for c in password):
                valid = False
            if self.use_lowercase.get() and not any(c.islower() for c in password):
                valid = False
            if self.use_digits.get() and not any(c.isdigit() for c in password):
                valid = False
            if self.use_special.get() and not any(c in string.punctuation for c in password):
                valid = False
            
            if valid:
                break
            
            # Перегенерировать пароль
            password = ''.join(random.choice(characters) for _ in range(length))
        
        self.password_var.set(password)
        return True
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования!")
    
    def save_to_history(self):
        """Сохранение текущего пароля в историю"""
        password = self.password_var.get()
        if not password:
            messagebox.showwarning("Предупреждение", "Нет пароля для сохранения!")
            return
        
        # Проверка на дубликаты (опционально)
        # for item in self.password_history:
        #     if item['password'] == password:
        #         messagebox.showinfo("Информация", "Этот пароль уже есть в истории!")
        #         return
        
        history_item = {
            'id': len(self.password_history) + 1,
            'password': password,
            'length': len(password),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.password_history.append(history_item)
        self.save_history()
        self.refresh_history_display()
        messagebox.showinfo("Успех", "Пароль сохранён в истории!")
    
    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.password_history = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.password_history = []
    
    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.password_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")
    
    def refresh_history_display(self):
        """Обновление отображения истории"""
        # Очистка текущих данных
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей из истории
        for item in self.password_history:
            self.history_tree.insert('', 'end', values=(
                item.get('id', ''),
                item.get('password', ''),
                item.get('length', ''),
                item.get('created_at', '')
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.password_history = []
            self.save_history()
            self.refresh_history_display()
            messagebox.showinfo("Успех", "История очищена!")

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()