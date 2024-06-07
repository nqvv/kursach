import tkinter as tk
import os
from tkinter import messagebox, ttk
import csv
import random
from datetime import datetime, timedelta

agent_id = None
user_id = None

def read_csv(filename):
    data = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        messagebox.showerror("Ошибка", f"Файл {filename} не найден.")
    return data

def generate_unique_id(existing_ids):
    while True:
        new_id = ''.join(random.choices('0123456789', k=5))
        if new_id not in existing_ids:
            return new_id
        
def validate_registration(fullname, phone, email, password):
    if not fullname or not phone or not email or not password:
        messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля.")
        return False
    if not phone.startswith(('8', '+7')) or len(phone) < 6:
        messagebox.showerror("Ошибка", "Неверный номер телефона.")
        return False
    return True

def authenticate_user():
    global user_id
    global agent_id
    phone_number = phone_entry.get()
    password = password_entry.get()
    user_type = user_type_var.get()

    def validate_user(data, is_agent=False):
        global user_id
        global agent_id
        for user in data:
            if user.get('phone') == phone_number and user.get('password') == password:
                user_id = user.get('ID')
                if is_agent:
                    agent_id = user.get('ID')
                return True
        return False

    if not phone_number.startswith(('8', '+7')) or len(phone_number) < 6:
        messagebox.showerror("Ошибка!", "Неверный номер телефона.")
    elif not password:
        messagebox.showerror("Ошибка!", "Пожалуйста, введите пароль.")
    else:
        if user_type == "Пользователь" and validate_user(clients):
            messagebox.showinfo("Успешно!", "Вы успешно авторизованы.")
            root.withdraw()
            open_dashboard(user_type)
        elif user_type == "Агент" and validate_user(employees, is_agent=True):
            messagebox.showinfo("Успешно!", "Вы успешно авторизованы.")
            root.withdraw()
            open_dashboard(user_type)
        elif user_type == "Администратор" and validate_user(admins):
            messagebox.showinfo("Успешно!", "Вы успешно авторизованы.")
            root.withdraw()
            open_dashboard(user_type)
        else:
            messagebox.showerror("Ошибка", "Неверный номер телефона или пароль.")       

# Функция для открытия окна регистрации
def open_registration_window():
    root.withdraw()
    registration_window = tk.Toplevel(root)
    registration_window.title("Окно регистрации")

    tk.Label(registration_window, text="Регистрация", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Label(registration_window, text="ФИО:").pack()
    fullname_entry = tk.Entry(registration_window)
    fullname_entry.pack()

    tk.Label(registration_window, text="Номер телефона:").pack()
    phone_entry_reg = tk.Entry(registration_window)
    phone_entry_reg.pack()

    tk.Label(registration_window, text="Почта:").pack()
    email_entry = tk.Entry(registration_window)
    email_entry.pack()

    tk.Label(registration_window, text="Пароль:").pack()
    password_entry_reg = tk.Entry(registration_window, show="*")
    password_entry_reg.pack()

    def register_user():
        fullname = fullname_entry.get()
        phone = phone_entry_reg.get()
        email = email_entry.get()
        password = password_entry_reg.get()
        
        global clients
        existing_ids = [user['ID'] for user in clients]

        if validate_registration(fullname, phone, email, password):
            user_id = generate_unique_id(existing_ids)
            user_data = {"fullname": fullname, "email": email, "phone": phone, "password": password, "ID": user_id}
            try:
                with open('Client.csv', mode='a', newline='', encoding='utf-8') as file:
                    for client in clients:
                        if phone == client["phone"]:
                            messagebox.showerror("Ошибка", "Данный номер телефона уже используется")
                            return

                    fieldnames = ['fullname', 'email', 'phone', 'password', 'ID']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writerow(user_data)

                messagebox.showinfo("Успешно!", "Пользователь успешно зарегистрирован.")
                registration_window.destroy()
                root.deiconify()

                clients = read_csv('Client.csv')

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось записать данные: {e}")

    tk.Button(registration_window, text="Зарегистрироваться", command=register_user).pack(pady=10)
    tk.Button(registration_window, text="Назад", command=lambda: (registration_window.destroy(), root.deiconify())).pack(pady=10)

# Функции для создания панели управления
def open_dashboard(user_type):
    if user_type == "Пользователь":
        user_dashboard()
    elif user_type == "Агент":
        agent_dashboard()
    elif user_type == "Администратор":
        admin_dashboard()

def user_dashboard():
    user_window = tk.Toplevel(root)
    user_window.title("Панель пользователя")

    def go_back():
        user_window.destroy()
        root.deiconify()

    tk.Label(user_window, text="Пользователь", font=("Arial", 16, "bold")).pack()
    tk.Button(user_window, text="Главная панель", command=lambda: open_main_panel(user_window)).pack()
    tk.Button(user_window, text="Договоры", command=lambda: open_contracts_list(user_window, "Пользователь")).pack()
    tk.Button(user_window, text="Выход", command=go_back).pack(pady=10)

def agent_dashboard():
    agent_window = tk.Toplevel(root)
    agent_window.title("Панель агента")

    def go_back():
        agent_window.destroy()
        root.deiconify()
        
    tk.Label(agent_window, text="Агент", font=("Arial", 16, "bold")).pack()
    tk.Button(agent_window, text="Договоры", command=lambda: open_contracts_list(agent_window, "Агент")).pack()
    tk.Button(agent_window, text="Заключить договор", command=lambda: open_contract_creation_window(agent_window)).pack()
    tk.Button(agent_window, text="Выход", command=go_back).pack(pady=10)

def admin_dashboard():
    admin_window = tk.Toplevel(root)
    admin_window.title("Панель администратора")

    tk.Label(admin_window, text="Администратор", font=("Arial", 16, "bold")).pack()
    tk.Button(admin_window, text="Посмотреть договора", command=lambda: open_contracts_management_window(admin_window)).pack()
    tk.Button(admin_window, text="Посмотреть агентов", command=lambda: open_agents_details_window(admin_window)).pack(pady=10)
    tk.Button(admin_window, text="Выход", command=lambda: (admin_window.destroy(), root.deiconify())).pack(pady=10)

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())

        _hits = []
        for item in self._completion_list:
            if item.lower().startswith(self.get().lower()):
                _hits.append(item)

        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        if _hits:
            self._hits = _hits
            self._hit_index = (self._hit_index + delta) % len(_hits)
            self.delete(0, tk.END)
            self.insert(0, _hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym in ('BackSpace', 'Left', 'Right', 'Up', 'Down'):
            self._hits = []
        if event.keysym == 'BackSpace':
            self.position = len(self.get())
        if event.keysym == 'Left':
            self.position = max(0, self.position - 1)
        if event.keysym == 'Right':
            self.position = min(len(self.get()), self.position + 1)
        if event.keysym == 'Up':
            self.autocomplete(-1)
        if event.keysym == 'Down':
            self.autocomplete(1)
        if len(event.keysym) == 1:
            self.autocomplete()

def open_main_panel(previous_window):
    previous_window.destroy()
    main_panel_window = tk.Toplevel(root)
    main_panel_window.title("Главная панель")

    user_type = user_type_var.get()
    button_user_type = tk.Button(main_panel_window, text=user_type, command=lambda: (main_panel_window.destroy(), open_dashboard(user_type)))
    button_user_type.pack(anchor='nw')

    tk.Label(main_panel_window, text="УСЛУГИ КОМПАНИИ", font=("Arial", 16, "bold")).pack()

    frame = tk.Frame(main_panel_window)
    frame.pack(pady=10)

    def open_insurance_calc():
        main_panel_window.destroy()
        open_insurance_calculation_window()

    service1 = tk.LabelFrame(frame, text="АВТОСТРАХОВАНИЕ", padx=10, pady=10)
    service1.pack(side="left", padx=10)
    tk.Label(service1, text="КАСКО ПРОФЕССИОНАЛ").pack()
    tk.Label(service1, text="ОСАГО").pack()
    tk.Button(service1, text="ЗАКАЗАТЬ", command=open_insurance_calc).pack(pady=5)

def open_insurance_calculation_window():
    global user_id
    insurance_window = tk.Toplevel(root)
    insurance_window.title("Расчет автострахования")

    def go_back():
        insurance_window.destroy()
        open_main_panel(insurance_window)

    def calculate_sum():
        cars  = read_csv("cars.csv")

        try:

            if any([table =="" for table in [year_of_manufacture_entry.get(),engine_power_entry.get(),driver_experience_entry.get(),car_make_combo.get(),start_date_entry.get(),insurer_combo.get()]]):
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            year_of_manufacture = year_of_manufacture_entry.get()
            if year_of_manufacture.isdigit() and (1900 <= int(year_of_manufacture) <= 2024):
                year_of_manufacture = int(year_of_manufacture)
            else:
               messagebox.showerror("Ошибка", "Введите год выпуска от 1900г до 2024г")
               return


            engine_power = engine_power_entry.get()
            if engine_power.isdigit() and (30 <= float(engine_power) <= 2000):
                engine_power = float(engine_power)
            else:
                messagebox.showerror("Ошибка", "Введите мощность двигателя от 30 до 2000 л.с.")
                return

            driver_experience = driver_experience_entry.get()
            if driver_experience.isdigit() and (1 <= int(driver_experience) <= 100):
                driver_experience = int(driver_experience)
            else:
                messagebox.showerror("Ошибка", "Введите стаж водителя от 1 до 100 лет")
                return
            
            name_of_car = car_make_combo.get()

            for car in cars:
                if name_of_car == car["name"]:
                    car_factor = float(car["factor"])

            base_amount = 1000
            age_factor = max(2024 - year_of_manufacture, 1) * 10 
            power_factor = engine_power * 2 
            experience_factor = max(driver_experience, 1) * 50 
            
            total_sum = (base_amount + age_factor + power_factor - experience_factor)*car_factor

            insurer = insurer_combo.get()
            car_make = car_make_combo.get()
            if insurer == "РОСГОССТРАХ":
                total_sum *= 1.1
            elif insurer == "Альфа страхование":
                total_sum *= 1.05
            elif insurer == "ИНГОССТРАХ":
                total_sum *= 1.07
            elif insurer == "Согласие":
                total_sum *= 1.03
            elif insurer == "Совкомбанк":
                total_sum *= 1.08
            elif insurer == "СОГАЗ":
                total_sum *= 1.09

            sum_var.set(f"{total_sum:.2f} руб.")
        except ValueError as e:
            sum_var.set(f"Ошибка: {e}")

    def save_contract():
        try:
            year_of_manufacture = int(year_of_manufacture_entry.get())
            engine_power = float(engine_power_entry.get())
            driver_experience = int(driver_experience_entry.get())
            start_date_str = start_date_entry.get()
            start_date = datetime.strptime(start_date_str, "%d.%m.%Y")
            end_date = start_date + timedelta(days=365)
            insurer = insurer_combo.get()
            car_make = car_make_combo.get()
            total_sum = sum_var.get()
            

            contract_id = generate_unique_id([])

            file_exists = os.path.isfile('Orders.csv')
            with open('Orders.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Contract ID", "User ID", "Car Make", "Year of Manufacture", "Engine Power", "Driver Experience", "Insurer", "Start Date", "End Date", "Total Sum"])
                writer.writerow([contract_id, user_id, car_make, year_of_manufacture, engine_power, driver_experience, insurer, start_date.strftime("%d.%m.%Y"), end_date.strftime("%d.%m.%Y"), total_sum])

            messagebox.showinfo("Успешно", "Контракт успешно сохранен!")
            insurance_window.destroy()
            open_main_panel(insurance_window)

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    with open('car_makes.txt', 'r', encoding='utf-8') as file:
        car_makes = file.read().splitlines()

    tk.Label(insurance_window, text="Марка автомобиля").grid(row=0, column=0, padx=10, pady=5)
    car_make_combo = AutocompleteCombobox(insurance_window)
    car_make_combo.set_completion_list(car_makes)
    car_make_combo.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Год выпуска").grid(row=1, column=0, padx=10, pady=5)
    year_of_manufacture_entry = tk.Entry(insurance_window)
    year_of_manufacture_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Мощность двигателя (л.с.)").grid(row=2, column=0, padx=10, pady=5)
    engine_power_entry = tk.Entry(insurance_window)
    engine_power_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Стаж водителя (лет)").grid(row=3, column=0, padx=10, pady=5)
    driver_experience_entry = tk.Entry(insurance_window)
    driver_experience_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Страхователь").grid(row=4, column=0, padx=10, pady=5)
    insurer_combo = ttk.Combobox(insurance_window, values=[
        "РОСГОССТРАХ", "Альфа страхование", "ИНГОССТРАХ", "Согласие", "Совкомбанк", "СОГАЗ"
    ])
    insurer_combo.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Дата начала (дд.мм.гггг)").grid(row=5, column=0, padx=10, pady=5)
    start_date_entry = tk.Entry(insurance_window)
    start_date_entry.grid(row=5, column=1, padx=10, pady=5)

    tk.Label(insurance_window, text="Страховая сумма").grid(row=6, column=0, padx=10, pady=5)
    sum_var = tk.StringVar()
    sum_insured_entry = tk.Entry(insurance_window, textvariable=sum_var, state='readonly')
    sum_insured_entry.grid(row=6, column=1, padx=10, pady=5)

    tk.Button(insurance_window, text="Рассчитать", command=calculate_sum).grid(row=7, column=0, padx=10, pady=10)
    tk.Button(insurance_window, text="Сохранить", command=save_contract).grid(row=7, column=1, padx=10, pady=10)
    tk.Button(insurance_window, text="Назад", command=go_back).grid(row=7, column=2, padx=10, pady=10)

def open_contracts_list(previous_window, user_type):
    previous_window.destroy()
    contracts_window = tk.Toplevel(root)
    contracts_window.title("Список договоров")

    tree = ttk.Treeview(contracts_window)
    tree.pack(expand=True, fill="both")

    with open("Orders.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        for row in reader:
            tree.insert("", "end", values=row)

    tree["columns"] = headers
    for col in headers:
        tree.column(col, anchor=tk.CENTER, width=150)
        tree.heading(col, text=col, anchor=tk.CENTER)

    tree.column("#0", width=0, stretch=tk.NO)

    def go_back():
        contracts_window.destroy()
        if user_type == "Пользователь":
            open_dashboard("Пользователь")
        elif user_type == "Агент":
            open_dashboard("Агент")

    tk.Button(contracts_window, text="Назад", command=go_back).pack(side="bottom", padx=10, pady=10)

def open_contract_creation_window(agent_window):
    global agent_id
    agent_window.destroy()
    contract_creation_window = tk.Toplevel(root)
    contract_creation_window.title("Заключение договора")

    def go_back():
        contract_creation_window.destroy()
        open_dashboard("Агент")

    tk.Label(contract_creation_window, text="Выберите договор для подтверждения:", font=("Arial", 16, "bold")).pack(pady=10)

    contracts_frame = tk.Frame(contract_creation_window)
    contracts_frame.pack(pady=10)

    selected_contract = tk.StringVar()
    contracts_list = read_csv('Orders.csv')

    headers = ["Contract ID", "User ID", "Car Make", "Year of Manufacture", "Engine Power", "Driver Experience", "Insurer", "Start Date", "End Date", "Total Sum"]

    for contract in contracts_list:
        contract_text = "\n".join([f"{header}: {contract[header]}" for header in headers])
        contract_frame = tk.Radiobutton(contracts_frame, text=contract_text, variable=selected_contract, value=contract["Contract ID"], anchor='w', justify='left')
        contract_frame.pack(fill="both", expand="yes", padx=10, pady=5)

    def confirm_contract():
        if not selected_contract.get():
            messagebox.showwarning("Предупреждение", "Выберите договор для подтверждения.")
            return

        contract_id = selected_contract.get()
        selected_contract_data = None
        remaining_contracts = []

        with open('Orders.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Contract ID"] == contract_id:
                    row["agent ID"] = agent_id
                    selected_contract_data = row
                else:
                    remaining_contracts.append(row)

        if selected_contract_data:
            with open('Confirmed Orders.csv', mode='a', newline='', encoding='utf-8') as file:
                fieldnames = headers + ["agent ID"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow(selected_contract_data)

            with open('Orders.csv', mode='w', newline='', encoding='utf-8') as file:
                fieldnames = headers
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(remaining_contracts)

            messagebox.showinfo("Успешно!", "Договор подтвержден.")
            contract_creation_window.destroy()
            open_dashboard("Агент")

    tk.Button(contract_creation_window, text="Подтвердить", command=confirm_contract).pack(side="left", padx=5, pady=5)
    tk.Button(contract_creation_window, text="Назад", command=go_back).pack(side="left", padx=5, pady=5)

def read_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def open_agents_details_window(previous_window):
    previous_window.destroy()
    agents_details_window = tk.Toplevel(root)
    agents_details_window.title("Подробности об агентах")

    def go_back():
        agents_details_window.destroy()
        admin_dashboard()

    tk.Label(agents_details_window, text="Агенты", font=("Arial", 16, "bold")).pack(pady=10)

    agents_frame = tk.Frame(agents_details_window)
    agents_frame.pack(pady=10)

    selected_agent = tk.StringVar()
    agents_list = read_csv('Employee.csv')

    for agent in agents_list:
        agent_frame = tk.Radiobutton(agents_frame, text=f"{agent['fullname']}\nПочта: {agent['email']}\nТелефон: {agent['phone']}\nID: {agent['ID']}", 
                                     variable=selected_agent, value=agent['phone'], anchor='w', justify='left')
        agent_frame.pack(fill="both", expand="yes", padx=10, pady=5)

    tk.Button(agents_details_window, text="Изменить", command=lambda: open_edit_agent_window(agents_details_window, selected_agent.get())).pack(side="left", padx=5, pady=5)
    tk.Button(agents_details_window, text="Добавить", command=lambda: open_add_agent_window(agents_details_window)).pack(side="left", padx=5, pady=5)
    tk.Button(agents_details_window, text="Удалить", command=lambda: delete_agent(agents_details_window, selected_agent.get())).pack(side="left", padx=5, pady=5)
    tk.Button(agents_details_window, text="Назад", command=go_back).pack(side="left", padx=5, pady=5)

def open_add_agent_window(previous_window):
    previous_window.destroy()
    add_agent_window = tk.Toplevel(root)
    add_agent_window.title("Добавить агента")

    tk.Label(add_agent_window, text="ФИО:").pack()
    fullname_entry = tk.Entry(add_agent_window)
    fullname_entry.pack()

    tk.Label(add_agent_window, text="Номер телефона:").pack()
    phone_entry = tk.Entry(add_agent_window)
    phone_entry.pack()

    tk.Label(add_agent_window, text="Почта:").pack()
    email_entry = tk.Entry(add_agent_window)
    email_entry.pack()

    tk.Label(add_agent_window, text="Пароль:").pack()
    password_entry = tk.Entry(add_agent_window, show="*")
    password_entry.pack()

    def add_agent():
        global agent_id
        fullname = fullname_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        global employees
        existing_ids = [user['ID'] for user in employees]

        if validate_registration(fullname, phone, email, password):
            agent_id = generate_unique_id(existing_ids)
            agent_data = {"fullname": fullname, "email": email, "phone": phone, "password": password, "ID": agent_id}

            try:
                with open('Employee.csv', mode='a', newline='', encoding='utf-8') as file:
                    fieldnames = ['fullname', 'email', 'phone', 'password', 'ID']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writerow(agent_data)

                messagebox.showinfo("Успешно!", "Агент успешно добавлен.")
                add_agent_window.destroy()
                admin_dashboard()

                employees = read_csv('Employee.csv')

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить агента: {e}")

    tk.Button(add_agent_window, text="Добавить агента", command=add_agent).pack(pady=10)
    tk.Button(add_agent_window, text="Назад", command=lambda: (add_agent_window.destroy(), admin_dashboard())).pack(pady=10)

def open_edit_agent_window(previous_window, phone):
    if not phone:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите агента для изменения.")
        return

    previous_window.destroy()
    edit_agent_window = tk.Toplevel(root)
    edit_agent_window.title("Изменить агента")

    selected_agent = None
    for agent in employees:
        if agent['phone'] == phone:
            selected_agent = agent
            break

    if not selected_agent:
        messagebox.showerror("Ошибка", "Агент не найден.")
        return

    tk.Label(edit_agent_window, text="ФИО:").pack()
    fullname_entry = tk.Entry(edit_agent_window)
    fullname_entry.insert(0, selected_agent['fullname'])
    fullname_entry.pack()

    tk.Label(edit_agent_window, text="Номер телефона:").pack()
    phone_entry = tk.Entry(edit_agent_window)
    phone_entry.insert(0, selected_agent['phone'])
    phone_entry.pack()

    tk.Label(edit_agent_window, text="Почта:").pack()
    email_entry = tk.Entry(edit_agent_window)
    email_entry.insert(0, selected_agent['email'])
    email_entry.pack()

    tk.Label(edit_agent_window, text="Пароль:").pack()
    password_entry = tk.Entry(edit_agent_window, show="*")
    password_entry.insert(0, selected_agent['password'])
    password_entry.pack()

    tk.Label(edit_agent_window, text="ID:").pack()
    id_entry = tk.Entry(edit_agent_window)
    id_entry.insert(0, selected_agent['ID'])
    id_entry.pack()

    def edit_agent():
        fullname = fullname_entry.get()
        phone = phone_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        agent_id = id_entry.get()

        global employees
        if validate_registration(fullname, phone, email, password):
            if agent_id != selected_agent['ID'] and agent_id in [agent['ID'] for agent in employees]:
                messagebox.showerror("Ошибка", "ID уже существует. Пожалуйста, введите уникальный ID.")
                return

            agent_data = {"fullname": fullname, "email": email, "phone": phone, "password": password, "ID": agent_id}

            try:
                with open('Employee.csv', mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                for row in rows:
                    if row['phone'] == selected_agent['phone']:
                        row.update(agent_data)
                        break

                with open('Employee.csv', mode='w', newline='', encoding='utf-8') as file:
                    fieldnames = ['fullname', 'email', 'phone', 'password', 'ID']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)

                messagebox.showinfo("Успешно!", "Данные агента успешно обновлены.")
                edit_agent_window.destroy()
                admin_dashboard()

                employees = read_csv('Employee.csv')

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить данные агента: {e}")

    tk.Button(edit_agent_window, text="Сохранить изменения", command=edit_agent).pack(pady=10)
    tk.Button(edit_agent_window, text="Назад", command=lambda: (edit_agent_window.destroy(), admin_dashboard())).pack(pady=10)

def delete_agent(previous_window, phone):
    if not phone:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите агента для удаления.")
        return

    try:
        with open('Employee.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            employees = list(reader)
            agent = next((row for row in employees if row['phone'] == phone), None)

        if not agent:
            messagebox.showerror("Ошибка", "Агент не найден.")
            return

        agent_id = agent['ID']

        with open('Confirmed Orders.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if any(row['agent ID'] == agent_id for row in reader):
                messagebox.showerror("Ошибка", "У данного агента есть заключенные договора.")
                return

        rows = [row for row in employees if row['phone'] != phone]

        with open('Employee.csv', mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['fullname', 'email', 'phone', 'password', 'ID']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        messagebox.showinfo("Успешно!", "Агент успешно удален.")
        previous_window.destroy()
        admin_dashboard()

        employees = read_csv('Employee.csv')

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить агента: {e}")


def open_contracts_management_window(previous_window):
    previous_window.destroy()
    contracts_management_window = tk.Toplevel(root)
    contracts_management_window.title("Список договоров")

    def go_back():
        contracts_management_window.destroy()
        admin_dashboard()

    tk.Label(contracts_management_window, text="Договоры", font=("Arial", 16, "bold")).pack(pady=10)

    contracts_frame = tk.Frame(contracts_management_window)
    contracts_frame.pack(pady=10)

    headers = ["Contract ID", "User ID", "Car Make", "Year of Manufacture", "Engine Power", "Driver Experience", "Insurer", "Start Date", "End Date", "Total Sum", "agent ID"]

    contracts_list = read_csv('Confirmed Orders.csv')

    selected_contract_id = tk.StringVar()

    for contract in contracts_list:
        contract_text = "\n".join([f"{header}: {contract[header]}" for header in headers])
        contract_frame = tk.Frame(contracts_frame)
        contract_frame.pack(fill="both", expand="yes", padx=10, pady=5)
        
        rb = tk.Radiobutton(contract_frame, text=f"Contract ID: {contract['Contract ID']}", variable=selected_contract_id, value=contract["Contract ID"], anchor='w', justify='left')
        rb.pack(side="left")
        
        tk.Label(contract_frame, text=contract_text).pack(side="left", padx=10)

    def edit_selected_contract():
        if not selected_contract_id.get():
            messagebox.showwarning("Предупреждение", "Выберите договор для редактирования.")
            return
        selected_contract = next((contract for contract in contracts_list if contract["Contract ID"] == selected_contract_id.get()), None)
        if selected_contract:
            open_contract_editing_window(contracts_management_window, selected_contract)

    tk.Button(contracts_management_window, text="Изменить", command=edit_selected_contract).pack(side="left", padx=10, pady=10)
    tk.Button(contracts_management_window, text="Назад", command=go_back).pack(side="right", padx=10, pady=10)

def open_contract_editing_window(previous_window, contract):
    previous_window.destroy()
    contract_editing_window = tk.Toplevel(root)
    contract_editing_window.title("Редактирование договора")

    def go_back():
        contract_editing_window.destroy()
        open_contracts_management_window(contract_editing_window)

    tk.Label(contract_editing_window, text="Редактирование договора", font=("Arial", 16, "bold")).pack(pady=10)

    edit_frame = tk.Frame(contract_editing_window)
    edit_frame.pack(pady=10)

    entries = {}

    for key, value in contract.items():
        tk.Label(edit_frame, text=f"{key}:").pack(pady=5)
        entry = tk.Entry(edit_frame)
        entry.insert(0, value)
        entry.pack(pady=5)
        entries[key] = entry

    def edit_contract():
        for key in entries:
            contract[key] = entries[key].get()

        try:
            with open('Confirmed Orders.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            for row in rows:
                if row['Contract ID'] == contract['Contract ID']:
                    row.update(contract)
                    break

            with open('Confirmed Orders.csv', mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['Contract ID', 'User ID', 'Car Make', 'Year of Manufacture', 'Engine Power', 'Driver Experience', 'Insurer', 'Start Date', 'End Date', 'Total Sum', 'agent ID']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            messagebox.showinfo("Успешно!", "Данные договора успешно обновлены.")
            contract_editing_window.destroy()
            open_contracts_management_window(contract_editing_window)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить данные договора: {e}")

    tk.Button(contract_editing_window, text="Готово", command=edit_contract).pack(side="left", padx=10, pady=10)
    tk.Button(contract_editing_window, text="Назад", command=go_back).pack(side="right", padx=10, pady=10)

# Глобальные переменные для хранения данных
clients = read_csv('Client.csv')
admins = read_csv('Admin.csv')
employees = read_csv('Employee.csv')

# Основное окно
root = tk.Tk()
root.title("Аутентификация")

tk.Label(root, text="Аутентификация", font=("Arial", 16, "bold")).pack(pady=10)

tk.Label(root, text="Номер телефона:").pack()
phone_entry = tk.Entry(root)
phone_entry.pack()

tk.Label(root, text="Пароль:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

user_type_var = tk.StringVar(value="Пользователь")
tk.Radiobutton(root, text="Пользователь", variable=user_type_var, value="Пользователь").pack()
tk.Radiobutton(root, text="Агент", variable=user_type_var, value="Агент").pack()
tk.Radiobutton(root, text="Администратор", variable=user_type_var, value="Администратор").pack()

tk.Button(root, text="Войти", command=authenticate_user).pack(pady=10)
tk.Button(root, text="Зарегистрироваться", command=open_registration_window).pack(pady=10)

root.mainloop()