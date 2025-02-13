import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import mysql.connector

# Підключення до бази даних MySQL
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Vlados1597_",  # Вкажіть ваш пароль
            database="BankingOperations"
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Помилка підключення", f"Не вдалося підключитись до бази даних: {err}")
        return None

# Функція для центрування вікон
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Функція для перемикання екранів
def show_frame(frame):
    frame.tkraise()

def calculate_risk(expected_return):
    try:
        expected_return = float(expected_return)
        risk_factor = expected_return / 10
        if expected_return <= 5:
            return "Low", risk_factor
        elif expected_return <= 8:
            return "Medium", risk_factor
        else:
            return "High", risk_factor
    except ValueError:
        return None, None

def create_investor():
    for widget in frame_create_investor.winfo_children():
        widget.destroy()

    tk.Label(frame_create_investor, text="Ім'я інвестора", font=("Arial", 12)).grid(row=0,  padx=(10, 10), pady=(80, 5))
    tk.Label(frame_create_investor, text="Tип інвестиції", font=("Arial", 12)).grid(row=1,  padx=(7, 10), pady=5)
    tk.Label(frame_create_investor, text="Очікуваний прибуток (%)", font=("Arial", 12)).grid(row=2, padx=(80, 10), pady=5)
    tk.Label(frame_create_investor, text="Рівень ризику", font=("Arial", 12)).grid(row=3, padx=(10, 10), pady=5)
    tk.Label(frame_create_investor, text="Фактор ризику", font=("Arial", 12)).grid(row=4, padx=(10, 10), pady=5)

    entry_name = tk.Entry(frame_create_investor)
    entry_type = tk.Entry(frame_create_investor)
    entry_return = tk.Entry(frame_create_investor)
    label_risk_level = tk.Label(frame_create_investor, text="", font=("Arial", 12))
    label_risk_factor = tk.Label(frame_create_investor, text="", font=("Arial", 12))

    entry_name.grid(row=0, padx=(400, 10), pady=(80, 5))
    entry_type.grid(row=1, padx=(400, 10), pady=5)
    entry_return.grid(row=2, padx=(400, 10), pady=5)
    label_risk_level.grid(row=3, padx=(400, 10), pady=5)
    label_risk_factor.grid(row=4, padx=(400, 10), pady=5)

    def update_risk_labels(event=None):
        expected_return = entry_return.get()
        risk_level, risk_factor = calculate_risk(expected_return)
        if risk_level and risk_factor:
            label_risk_level.config(text=risk_level)
            label_risk_factor.config(text=f"{risk_factor:.2f}")
        else:
            label_risk_level.config(text="Невірно")
            label_risk_factor.config(text="Невірно")

    entry_return.bind("<KeyRelease>", update_risk_labels)

    def save_investor():
        investor_name = entry_name.get()
        investment_type = entry_type.get()
        expected_return = entry_return.get()
        risk_level, risk_factor = calculate_risk(float(expected_return))

        if not investor_name or not investment_type or not expected_return or not risk_level:
            messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля.")
            return

        try:
            connection = connect_to_database()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO PotentialInvestments (investment_name, investment_type, expected_return)
                    VALUES (%s, %s, %s)
                """, (investor_name, investment_type, float(expected_return)))

                investment_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO RiskAssessment (investment_id, risk_level, risk_factor)
                    VALUES (%s, %s, %s)
                """, (investment_id, risk_level, risk_factor))
                connection.commit()
                connection.close()
                messagebox.showinfo("Успіх", "Новий інвестор успішно доданий!")
                show_frame(frame_main)
        except ValueError:
            messagebox.showerror("Помилка", "Невірно введені дані.")

    tk.Button(frame_create_investor, text="Зберегти", font=("Arial", 12), command=save_investor).grid(row=5, padx=(220, 5), pady=10)
    tk.Button(frame_create_investor, text="Назад", font=("Arial", 12), command=lambda: show_frame(frame_main)).grid(row=6, padx=(220, 5), pady=10)

# Функція для створення нового депозиту
def create_deposit():
    for widget in frame_create.winfo_children():
        widget.destroy()

    def update_investor_details(event):
        investor = investor_combobox.get()
        if not investor:
            return
        
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT PI.expected_return, RA.risk_level 
                FROM PotentialInvestments PI
                JOIN RiskAssessment RA ON PI.investment_id = RA.investment_id
                WHERE PI.investment_name = %s
            """, (investor,))
            details = cursor.fetchone()
            connection.close()

            if details:
                expected_return_label.config(text=f"{details[0]}%")
                risk_level_label.config(text=details[1])
                calculate_profit()
            else:
                expected_return_label.config(text="N/A")
                risk_level_label.config(text="N/A")

    def calculate_profit(*args):
        try:
            deposit_amount = float(entry_amount.get())
            deposit_date = datetime.strptime(entry_date.get(), "%Y-%m-%d")
            maturity_date = datetime.strptime(entry_maturity.get(), "%Y-%m-%d")
            duration_years = (maturity_date - deposit_date).days / 365.0
            expected_return = float(expected_return_label.cget("text").strip('%'))
            profit = deposit_amount * (expected_return / 100) * duration_years
            profit_label.config(text=f"{profit:.2f}")
        except ValueError:
            profit_label.config(text="N/A")

    def save_deposit():
        customer_name = entry_name.get()
        deposit_amount = entry_amount.get()
        deposit_date = entry_date.get()
        maturity_date = entry_maturity.get()
        investor = investor_combobox.get()

        if not customer_name or not deposit_amount or not deposit_date or not maturity_date or not investor:
            messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля.")
            return
        
        try:
            deposit_amount = float(deposit_amount)
            connection = connect_to_database()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT investment_id FROM PotentialInvestments WHERE investment_name = %s", (investor,))
                investor_id = cursor.fetchone()
                if investor_id:
                    investor_id = investor_id[0]
                else:
                    messagebox.showerror("Помилка", "Обраний інвестор не знайдений.")
                    return

                cursor.execute("""
                    INSERT INTO Deposits (customer_name, deposit_amount, deposit_date, maturity_date, investment_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (customer_name, deposit_amount, deposit_date, maturity_date, investor_id))
                connection.commit()
                connection.close()
                messagebox.showinfo("Успіх", "Новий депозит успішно додано!")
                show_frame(frame_main)
        except ValueError:
            messagebox.showerror("Помилка", "Невірно введена сума депозиту.")

    tk.Label(frame_create, text="Ім'я клієнта", font=("Arial", 12)).grid(row=0, column=0, padx=(130, 10), pady=5, sticky="e")
    tk.Label(frame_create, text="Сума депозиту", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Label(frame_create, text="Дата депозиту", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    tk.Label(frame_create, text="Дата погашення", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="e")
    tk.Label(frame_create, text="Обрати інвестора", font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=5, sticky="w")
    tk.Label(frame_create, text="Очікуваний прибуток", font=("Arial", 12)).grid(row=1, column=2, padx=10, pady=5, sticky="w")
    tk.Label(frame_create, text="Рівень ризику", font=("Arial", 12)).grid(row=2, column=2, padx=10, pady=5, sticky="w")
    tk.Label(frame_create, text="Чистий прибуток", font=("Arial", 12)).grid(row=3, column=2, padx=10, pady=5, sticky="w")

    entry_name = tk.Entry(frame_create)
    entry_amount = tk.Entry(frame_create)
    entry_date = tk.Entry(frame_create, fg="gray")
    entry_maturity = tk.Entry(frame_create, fg="gray")

    entry_name.grid(row=0, column=1, padx=10, pady=5)
    entry_amount.grid(row=1, column=1, padx=10, pady=5)
    entry_date.grid(row=2, column=1, padx=10, pady=5)
    entry_maturity.grid(row=3, column=1, padx=10, pady=5)

    entry_date.insert(0, "рррр-мм-дд")
    entry_maturity.insert(0, "рррр-мм-дд")

    def on_entry_click(event, entry):
        if entry.get() == "рррр-мм-дд":
            entry.delete(0, "end")
            entry.config(fg="black")

    def on_focus_out(event, entry):
        if entry.get() == "":
            entry.insert(0, "рррр-мм-дд")
            entry.config(fg="gray")

    entry_date.bind("<FocusIn>", lambda event: on_entry_click(event, entry_date))
    entry_date.bind("<FocusOut>", lambda event: on_focus_out(event, entry_date))
    entry_maturity.bind("<FocusIn>", lambda event: on_entry_click(event, entry_maturity))
    entry_maturity.bind("<FocusOut>", lambda event: on_focus_out(event, entry_maturity))

    entry_amount.bind("<KeyRelease>", calculate_profit)
    entry_date.bind("<KeyRelease>", calculate_profit)
    entry_maturity.bind("<KeyRelease>", calculate_profit)

    def auto_format_date(event, entry):
        text = entry.get()
        if len(text) == 4 or len(text) == 7:  # Додавати "-" після року і місяця
            entry.insert(tk.END, "-")

    def limit_date_length(entry):
        text = entry.get()
        if len(text) > 10:  # Обмеження на довжину до 10 символів (формат YYYY-MM-DD)
            entry.delete(10, tk.END)

    def validate_date_input(text):
        return text.isdigit() or text in ["-", ""]

    vcmd_date = (root.register(validate_date_input), "%P")
    entry_date.config(validatecommand=vcmd_date)
    entry_maturity.config(validatecommand=vcmd_date)

    entry_date.bind("<KeyRelease>", lambda event: [auto_format_date(event, entry_date), limit_date_length(entry_date)])
    entry_maturity.bind("<KeyRelease>", lambda event: [auto_format_date(event, entry_maturity), limit_date_length(entry_maturity)])

    connection = connect_to_database()
    investor_names = []
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT investment_name FROM PotentialInvestments")
        investor_names = [row[0] for row in cursor.fetchall()]
        connection.close()

    investor_combobox = ttk.Combobox(frame_create, values=investor_names, state="readonly")
    investor_combobox.grid(row=0, column=3, padx=10, pady=5)
    investor_combobox.set("Оберіть інвестора")
    investor_combobox.bind("<<ComboboxSelected>>", update_investor_details)

    expected_return_label = tk.Label(frame_create, text="N/A", font=("Arial", 12))
    expected_return_label.grid(row=1, column=3, padx=10, pady=5, sticky="w")

    risk_level_label = tk.Label(frame_create, text="N/A", font=("Arial", 12))
    risk_level_label.grid(row=2, column=3, padx=10, pady=5, sticky="w")

    profit_label = tk.Label(frame_create, text="N/A", font=("Arial", 12))
    profit_label.grid(row=3, column=3, padx=10, pady=5, sticky="w")

    tk.Button(frame_create, text="Зберегти депозит", font=("Arial", 12), command=save_deposit).grid(row=4, columnspan=3, pady=10, padx=(270, 10))
    tk.Button(frame_create, text="Назад", font=("Arial", 12), command=lambda: show_frame(frame_main)).grid(row=5,  columnspan=3, pady=10, padx=(270, 10))

# Функція для перегляду депозитів
def view_deposits():
    # Очищаємо старі віджети, якщо вони є
    for widget in frame_view_deposits.winfo_children():
        widget.destroy()

    # Створюємо Treeview для відображення таблиці депозитів
    tree = ttk.Treeview(frame_view_deposits, columns=("ID", "Customer", "Amount", "Deposit Date", "Maturity Date", "Investor"), show="headings")
    tree.grid(row=0, column=0, padx=30, pady=10, sticky="nsew")

    # Налаштування колонок
    tree.column("ID", width=50, anchor="center")
    tree.column("Customer", width=150, anchor="center")
    tree.column("Amount", width=125, anchor="center")
    tree.column("Deposit Date", width=125, anchor="center")
    tree.column("Maturity Date", width=125, anchor="center")
    tree.column("Investor", width=150, anchor="center")

    tree.heading("ID", text="ID")
    tree.heading("Customer", text="Ім'я клієнта")
    tree.heading("Amount", text="Сума депозиту")
    tree.heading("Deposit Date", text="Дата депозиту")
    tree.heading("Maturity Date", text="Дата погашення")
    tree.heading("Investor", text="Інвестор")

    # Отримуємо дані з бази даних
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT D.deposit_id, D.customer_name, D.deposit_amount, D.deposit_date, D.maturity_date, PI.investment_name
            FROM Deposits D
            JOIN PotentialInvestments PI ON D.investment_id = PI.investment_id
        """)
        rows = cursor.fetchall()
        connection.close()

        # Додаємо отримані дані в таблицю
        for row in rows:
            tree.insert("", "end", values=row)

    
    # Форма для введення ID депозиту для видалення
    delete_frame = tk.Frame(frame_view_deposits)
    delete_frame.grid(row=1, column=0, pady=10, sticky="w")
    if admin:
        tk.Label(delete_frame, text="Напишіть ID для видалення", font=("Arial", 12)).grid(row=0, column=0, padx=(100, 10))
        delete_id_entry = tk.Entry(delete_frame)
        delete_id_entry.grid(row=0, column=0, padx=(450, 10), pady=10)

        def delete_deposit():
            deposit_id = delete_id_entry.get()
            if not deposit_id:
                messagebox.showerror("Помилка", "Будь ласка, введіть ID депозиту для видалення.")
                return
            try:
                deposit_id = int(deposit_id)
                connection = connect_to_database()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM Deposits WHERE deposit_id = %s", (deposit_id,))
                    connection.commit()
                    connection.close()
                    messagebox.showinfo("Успіх", "Депозит успішно видалено!")
                    show_frame(frame_main)
                else:
                    messagebox.showerror("Помилка", "Не вдалося підключитись до бази даних.")
            except ValueError:
                messagebox.showerror("Помилка", "ID депозиту має бути числом.")

        tk.Button(delete_frame, text="Видалити", font=("Arial", 12), command=delete_deposit).grid(row=1, column=0, pady=10, padx=(170, 10))
    tk.Button(delete_frame, text="Назад", font=("Arial", 12), command=lambda: show_frame(frame_main)).grid(row=1, column=0, pady=10, padx=(370, 10))

# Функція для перевірки логіну та паролю
def attempt_login(entry_username, entry_password):
    username = entry_username.get()
    password = entry_password.get()
    
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT is_admin FROM Users WHERE username = %s AND password = %s
        """, (username, password))
        result = cursor.fetchone()
        connection.close()
        
        if result:
            is_admin = result[0]
            if is_admin:
                global admin
                admin = True
                messagebox.showinfo("Успіх", "Ви увійшли як адміністратор.")
                create_main_menu()
                show_frame(frame_main)
            else:
                messagebox.showinfo("Успіх", "Ви увійшли як фінансовий менеджер.")
                create_main_menu()
                show_frame(frame_main)
        else:
            messagebox.showerror("Помилка", "Невірний логін або пароль.")
    else:
        messagebox.showerror("Помилка", "Не вдалося підключитись до бази даних.")

# Вхід
def login_screen():

    tk.Label(frame_login, text="Вас вітає банківський застосунок", font=("Arial", 20, "bold")).grid(row=0, padx=(200, 10), pady=(20, 5))
    tk.Label(frame_login, text="Введіть ваш логін і пароль", font=("Arial", 16)).grid(row=1, padx=(200, 10), pady=(20, 5))
    tk.Label(frame_login, text="Логін", font=("Arial", 12)).grid(row=2, column=0, padx=(30, 10), pady=(10, 5))
    tk.Label(frame_login, text="Пароль", font=("Arial", 12)).grid(row=3, column=0, padx=(30, 10), pady=5)

    entry_username = tk.Entry(frame_login)
    entry_password = tk.Entry(frame_login, show="*")

    entry_username.grid(row=2, padx=(300, 10), pady=(10, 5))
    entry_password.grid(row=3, padx=(300, 10), pady=5)

    tk.Button(frame_login, text="Увійти", font=("Arial", 12), command=lambda: attempt_login(entry_username, entry_password)).grid(row=4,  columnspan=2, padx=(150, 10), pady=10)



def create_account():
    for widget in frame_create_account.winfo_children():
        widget.destroy()

    #Введення логіну
    tk.Label(frame_create_account, text="Логін", font=("Arial", 12)).grid(row=0, column=0, padx=(80, 10), pady=(60,10))
    entry_username = tk.Entry(frame_create_account)
    entry_username.grid(row=0, padx=(400, 10), pady=(60, 10))

    # Введення паролю
    tk.Label(frame_create_account, text="Пароль", font=("Arial", 12)).grid(row=1, column=0, padx=(80, 10), pady=10)
    entry_password = tk.Entry(frame_create_account, show="*")
    entry_password.grid(row=1, padx=(400, 10), pady=10)

    # Чекбокс для адміністраторських прав
    var_is_admin = tk.BooleanVar()
    chk_admin = tk.Checkbutton(frame_create_account, text="Адміністратор", font=("Arial", 12), variable=var_is_admin)
    chk_admin.grid(row=2, padx=(130, 10), pady=10)


    # Функція для збереження аккаунту в базі даних
    def save_account():
        username = entry_username.get()
        password = entry_password.get()
        is_admin = var_is_admin.get()

        if not username or not password:
            messagebox.showerror("Помилка", "Будь ласка, заповніть всі поля.")
            return

        try:
            connection = connect_to_database()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO Users (username, password, is_admin)
                    VALUES (%s, %s, %s)
                """, (username, password, is_admin))
                connection.commit()
                connection.close()
                messagebox.showinfo("Успіх", "Обліковий запис успішно створено!")
                show_frame(frame_login)  # Перехід до екрану входу після успішного створення
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося створити обліковий запис: {e}")

    # Кнопка для збереження облікового запису
    tk.Button(frame_create_account, text="Зберегти", font=("Arial", 12), command=save_account).grid(row=3, padx=(250, 10), pady=10)

    # Кнопка для повернення до екрану входу
    tk.Button(frame_create_account, text="Назад", font=("Arial", 12), command=lambda: show_frame(frame_main)).grid(row=4, padx=(250, 10), pady=10)
    show_frame(frame_create_account)




# Основне вікно
root = tk.Tk()
root.title("Банківська діяльність - Розміщення коштів")
root.geometry("800x400")
center_window(root)

frame_main = tk.Frame(root)
frame_create = tk.Frame(root)
frame_view_deposits = tk.Frame(root)
frame_login = tk.Frame(root)
frame_create_account = tk.Frame(root)
frame_create_investor = tk.Frame(root)

def create_main_menu():
    for widget in frame_main.winfo_children():
        widget.destroy()

    tk.Label(frame_main, text="Вас вітає банківський застосунок", font=("Arial", 20, "bold")).pack(padx=(10, 10), pady=(20, 5))
    # Додаємо кнопки на головному екрані
    tk.Button(frame_main, text="Переглянути депозити", font=("Arial", 12), width=30, command=lambda: [view_deposits(), show_frame(frame_view_deposits)]).pack(pady=(10, 10), padx=280)
    tk.Button(frame_main, text="Створити новий депозит", font=("Arial", 12), width=30, command=lambda: [create_deposit(), show_frame(frame_create)]).pack(pady=10)

    if admin:
        tk.Button(frame_main, text="Додати нового інвестора", font=("Arial", 12), width=30, command=lambda: [create_investor(), show_frame(frame_create_investor)]).pack(pady=10)
        tk.Button(frame_main, text="Створити аккаунт", font=("Arial", 12), width=30, command=lambda: [create_account(), show_frame(frame_create_account)]).pack(pady=10)

    tk.Button(frame_main, text="Вихід", font=("Arial", 12), width=30, command=root.quit).pack(pady=10)

# Перемикання екранів
for frame in (frame_main, frame_create, frame_view_deposits, frame_create_investor, frame_create_account, frame_login):
    frame.grid(row=0, column=0, sticky="nsew")

frame_main.columnconfigure(0, weight=1)
frame_main.rowconfigure(0, weight=1)

is_admin = False
admin = False

# Показуємо головний екран
login_screen()
show_frame(frame_login)
root.mainloop()