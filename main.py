import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x500")

        # --- Поля ввода ---
        tk.Label(root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = tk.Entry(root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.category_entry = tk.Entry(root)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(root)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Кнопка добавления ---
        self.add_button = tk.Button(root, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=3, columnspan=2, pady=10)

        # --- Таблица расходов ---
        self.tree = ttk.Treeview(root, columns=("Сумма", "Категория", "Дата"), show="headings")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        self.tree.grid(row=4, columnspan=2, sticky="nsew", padx=5)

        # Настройка сетки для растягивания таблицы
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(1, weight=1)

         # --- Фильтрация и подсчёт ---
         # Период для суммы
         tk.Label(root, text="С:").grid(row=5, column=0, sticky="e", padx=5)
         self.start_date = tk.Entry(root)
         self.start_date.grid(row=5, column=1, padx=5)

         tk.Label(root, text="По:").grid(row=6, column=0, sticky="e", padx=5)
         self.end_date = tk.Entry(root)
         self.end_date.grid(row=6, column=1, padx=5)

         self.sum_button = tk.Button(root, text="Сумма за период", command=self.calculate_sum)
         self.sum_button.grid(row=7, columnspan=2, pady=5)

         # Фильтр по категории и дате
         tk.Label(root, text="Фильтр по категории:").grid(row=8, column=0, sticky="e", padx=5)
         self.filter_category = tk.Entry(root)
         self.filter_category.grid(row=8, column=1, padx=5)

         tk.Label(root, text="Фильтр по дате:").grid(row=9, column=0, sticky="e", padx=5)
         self.filter_date = tk.Entry(root)
         self.filter_date.grid(row=9, column=1, padx=5)

         self.filter_button = tk.Button(root, text="Фильтровать", command=self.filter_expenses)
         self.filter_button.grid(row=10, columnspan=2, pady=5)

          # --- Сохранение и загрузка ---
          self.save_button = tk.Button(
              root, text="Сохранить в JSON", command=self.save_to_json
          )
          self.save_button.grid(row=11, columnspan=2, pady=(20, 0))

          self.load_button = tk.Button(
              root, text="Загрузить из JSON", command=self.load_from_json
          )
          self.load_button.grid(row=12, columnspan=2)

    def add_expense(self):
         amount = self.amount_entry.get()
         category = self.category_entry.get()
         date = self.date_entry.get()

          # Валидация суммы
          try:
              amount = float(amount)
              if amount <= 0:
                  raise ValueError("Сумма должна быть положительной")
          except ValueError:
              messagebox.showerror("Ошибка", "Введите корректную сумму (положительное число)")
              return

          # Валидация даты
          try:
              datetime.strptime(date, "%Y-%m-%d")
          except ValueError:
              messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
              return

          if not category:
              messagebox.showerror("Ошибка", "Введите категорию")
              return

          # Добавление в таблицу (Treeview)
          self.tree.insert("", "end", values=(f"{amount:.2f}", category.strip(), date))

          # Очистка полей ввода
          self.amount_entry.delete(0, tk.END)
          self.category_entry.delete(0, tk.END)
          self.date_entry.delete(0, tk.END)

    def calculate_sum(self):
          start = self.start_date.get()
          end = self.end_date.get()
          
          # Валидация дат периода (если указаны обе)
          if start and end:
              try:
                  datetime.strptime(start, "%Y-%m-%d")
                  datetime.strptime(end, "%Y-%m-%d")
              except ValueError:
                  messagebox.showerror("Ошибка", "Даты периода должны быть в формате ГГГГ-ММ-ДД")
                  return

          total = 0.0
          for child in self.tree.get_children():
              values = self.tree.item(child)["values"]
              date_item = values[2]
              
              # Проверка попадания в период (если даты указаны)
              if start and end:
                  if not (start <= date_item <= end):
                      continue

              total += float(values[0])
          
          messagebox.showinfo("Сумма", f"Сумма расходов: {total:.2f}")

    def filter_expenses(self):
          cat_filter = self.filter_category.get().lower()
          date_filter = self.filter_date.get()
          
          # Валидация даты фильтра (если указана)
          if date_filter:
              try:
                  datetime.strptime(date_filter, "%Y-%m-%d")
              except ValueError:
                  messagebox.showerror("Ошибка", "Дата фильтра должна быть в формате ГГГГ-ММ-ДД")
                  return

         
          for child in self.tree.get_children():
              values = self.tree.item(child)["values"]
              
              show = True
              
              # Фильтр по категории (поиск подстроки без учёта регистра)
              if cat_filter and cat_filter not in values[1].lower():
                  show = False
                  
              # Фильтр по дате (точное совпадение)
              if date_filter and date_filter != values[2]:
                  show = False

              # Скрытие/отображение строки
              self.tree.item(child, tags=["hidden"] if not show else [])
         
          # Конфигурация тега для скрытых строк (делаем их серыми и нечитаемыми)
          self.tree.tag_configure("hidden", foreground="#888888", font=(None, 10))

    def save_to_json(self):
          data = []
          for child in self.tree.get_children():
              values = self.tree.item(child)["values"]
              data.append({
                  "amount": float(values[0]),
                  "category": values[1],
                  "date": values[2]
               })
          
           with open("expenses.json", "w") as f:
               json.dump(data, f, ensure_ascii=False, indent=4)
           
           messagebox.showinfo("Сохранение", "Данные успешно сохранены в expenses.json")

    def load_from_json(self):
           try:
               with open("expenses.json", "r") as f:
                   data = json.load(f)
                   
                   # Очистка текущей таблицы перед загрузкой
                   for item in self.tree.get_children():
                       self.tree.delete(item)
                   
                   for item in data:
                       # Проверка структуры данных на случай ошибок в файле
                       if all(key in item for key in ["amount", "category", "date"]):
                           self.tree.insert("", "end", values=(f"{item['amount']:.2f}", item['category'], item['date']))
           
           except FileNotFoundError:
               messagebox.showinfo("Загрузка", "Файл expenses.json не найден. Будет создан при сохранении.")
           except json.JSONDecodeError:
               messagebox.showerror("Ошибка", "Файл expenses.json повреждён или имеет неверный формат.")
           except Exception as e:
               messagebox.showerror("Ошибка загрузки", str(e))
           else:
               messagebox.showinfo("Загрузка", "Данные успешно загружены из expenses.json")


if __name__ == "__main__":
     root = tk.Tk()
     app = ExpenseTrackerApp(root)
     root.mainloop()