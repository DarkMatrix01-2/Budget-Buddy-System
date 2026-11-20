import matplotlib.pyplot as plt
import os
import json
import datetime
from abc import ABC, abstractmethod


# ================= DATE =================

def get_today():
    return datetime.date.today().isoformat()


# ================= DISPLAY HELPERS =================

def header(title):
    print("\n" + "═" * 40)
    print(f"  {title}")
    print("═" * 40)

def divider():
    print("─" * 40)

def success(msg):
    print(f"\n  ✔  {msg}")

def error(msg):
    print(f"\n  ✘  {msg}")

def info(msg):
    print(f"  →  {msg}")


# ================= LOGIN SYSTEM =================

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_password(self, password):
        return self.password == password


class LoginManager:
    def __init__(self, file="users.txt"):
        self.file = file
        self.users = {}
        self.load_users()

    def load_users(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, "r") as f:
            for line in f:
                username, password = line.strip().split(",")
                self.users[username] = User(username, password)

    def save_user(self, username, password):
        with open(self.file, "a") as f:
              f.write(f"{username},{password}\n")

    def register(self):
        header("CREATE ACCOUNT")
        username = input("  Username : ")
        password = input("  Password : ")
        divider()
        if username in self.users:
            error("Username already exists.")
            return None
        user = User(username, password)
        self.users[username] = user
        self.save_user(username, password)
        success("Account created successfully!")
        return user

    def login(self):
        header("LOGIN")
        username = input("  Username : ")
        password = input("  Password : ")
        divider()
        user = self.users.get(username)
        if user and user.check_password(password):
            success(f"Welcome back, {username}!")
            return user
        error("Invalid username or password.")
        return None

    def delete_user(self):
        header("DELETE ACCOUNT")
        username = input("  Username : ")
        password = input("  Password : ")
        divider()

        user = self.users.get(username)

        if not user or not user.check_password(password):
            error("Invalid username or password.")
            return

        confirm = input("  Type DELETE to confirm : ")
        divider()

        if confirm != "DELETE":
            error("Deletion cancelled.")
            return

        del self.users[username]

        with open(self.file, "w") as f:
            for uname, u in self.users.items():
                f.write(f"{uname},{u.password}\n")

        data_file = f"data_{username}.json"
        if os.path.exists(data_file):
            os.remove(data_file)

        success(f"Account '{username}' has been deleted.")

    def start(self):
        while True:
            header("BUDGET BUDDY")
            print("  [1]  Login")
            print("  [2]  Register")
            print("  [3]  Delete Account")
            print("  [4]  Exit")
            divider()
            choice = input("  >> ")
            if choice == "1":
                user = self.login()
                if user:
                    return user
            elif choice == "2":
                user = self.register()
                if user:
                    return user
            elif choice == "3":
                self.delete_user()
                input("\n  Press Enter to continue...")
            elif choice == "4":
                exit()
            else:
                error("Invalid choice.")


# ================= DATA MANAGER =================

class DataManager:
    def __init__(self, username):
        self.filename = f"data_{username}.json"

    def load_data(self):
        default = {
            "daily_allowance": 1000,
            "allowance": 1000,
            "expenses": {
                "Food": [],
                "Transportation": [],
                "Bills": [],
                "Others": []
            },
            "savings": [],
            "history": {}
        }
        if not os.path.exists(self.filename):
            return default
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except:
            error("Data corrupted. Resetting...")
            return default

    def save_data(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)


# ================= OOP CRUD =================

class ExpenseAction(ABC):
    def __init__(self, category):
        self.category = category

    @abstractmethod
    def execute(self, data):
        pass


class AddExpense(ExpenseAction):
    def execute(self, data):
        header(f"ADD  ›  {self.category.upper()}")
        info(f"Current allowance: ₱{data['allowance']:.2f}")
        divider()
        try:
            amount = float(input("  Amount : ₱"))
        except ValueError:
            error("Please enter a valid number.")
            return
        divider()
        if 0 < amount <= data["allowance"]:
            data["expenses"][self.category].append(amount)
            data["allowance"] -= amount
            success(f"₱{amount:.2f} added to {self.category}.")
            info(f"Remaining allowance: ₱{data['allowance']:.2f}")
        else:
            error("Invalid amount. Must be > 0 and within your allowance.")


class EditExpense(ExpenseAction):
    def execute(self, data):
        header(f"EDIT  ›  {self.category.upper()}")
        if not data["expenses"][self.category]:
            error("No expenses found in this category.")
            return
        print()
        for i, val in enumerate(data["expenses"][self.category]):
            print(f"  [{i}]  ₱{val:.2f}")
        divider()
        index = int(input(" Select index : "))

        
        error("/n Please enter a valid number.")
        return
        if index < 0 or index >= len(data["expenses"][self.category]):
            error("Index out of range.")
            return
        try:
            new = float(input("  New amount  : ₱"))
        except ValueError:
            error("Please enter a valid number.")
            return
        divider()
        old = data["expenses"][self.category][index]
        data["allowance"] += (old - new)
        data["expenses"][self.category][index] = new
        success(f"Entry updated: ₱{old:.2f}  →  ₱{new:.2f}")
        info(f"Remaining allowance: ₱{data['allowance']:.2f}")


class DeleteExpense(ExpenseAction):
    def execute(self, data):
        header(f"DELETE  ›  {self.category.upper()}")
        if not data["expenses"][self.category]:
            error("No expenses found in this category.")
            return
        print()
        for i, val in enumerate(data["expenses"][self.category]):
            print(f"  [{i}]  ₱{val:.2f}")
        divider()
        try:
            index = int(input("  Select index : "))
        except ValueError:
            error("Please enter a valid number.")
            return
        if index < 0 or index >= len(data["expenses"][self.category]):
            error("Index out of range.")
            return
        divider()
        removed = data["expenses"][self.category].pop(index)
        data["allowance"] += removed
        success(f"₱{removed:.2f} deleted from {self.category}.")
        info(f"Remaining allowance: ₱{data['allowance']:.2f}")


# ================= CORE =================

def view_expenses(data):
    header("TODAY'S EXPENSES")
    total = 0
    print()
    for cat, values in data["expenses"].items():
        cat_total = sum(values)
        total += cat_total
        entries = len(values)
        print(f"  {cat:<16} ₱{cat_total:>8.2f}   ({entries} item{'s' if entries != 1 else ''})")
    divider()
    print(f"  {'TOTAL':<16} ₱{total:>8.2f}")
    print()


def end_day(data):
    header("END DAY")
    today = get_today()
    if today in data["history"]:
        error("Today has already been ended.")
        return
    saved = data["allowance"]
    data["savings"].append(saved)
    data["history"][today] = {
        "Food": sum(data["expenses"]["Food"]),
        "Transportation": sum(data["expenses"]["Transportation"]),
        "Bills": sum(data["expenses"]["Bills"]),
        "Others": sum(data["expenses"]["Others"]),
        "Savings": saved
    }
    divider()
    print(f"  Date    : {today}")
    print(f"  Saved   : ₱{saved:.2f}")
    print(f"  Resetting to  : ₱{data['daily_allowance']:.2f}")
    print(f"  Total days recorded : {len(data['savings'])}")
    divider()
    data["allowance"] = data["daily_allowance"]
    for cat in data["expenses"]:
        data["expenses"][cat] = []
    success("Day ended. Allowance has been reset.")
    info(f"New allowance: ₱{data['daily_allowance']:.2f}")


def change_allowance(data):
    header("CHANGE ALLOWANCE")
    info(f"Current daily allowance: ₱{data['daily_allowance']:.2f}")
    divider()
    try:
        new = float(input("  New allowance : ₱"))
    except ValueError:
        error("Please enter a valid number.")
        return
    divider()
    if new <= 0:
        error("Allowance must be greater than ₱0.")
        return
    data["daily_allowance"] = new
    data["allowance"] = new
    success(f"Daily allowance updated to ₱{new:.2f}")


# ================= CHARTS =================

def savings_chart(data):
    while not data["savings"]:
        error("No savings data yet.")
        return
    days = range(1, len(data["savings"]) + 1)
    plt.plot(days, data["savings"], marker="o")
    plt.title("Savings Over Time")
    plt.show()


def monthly_chart(data):
    totals = {"Food": 0, "Transportation": 0, "Bills": 0, "Others": 0}
    current_month = get_today()[:7]
    for date, record in data["history"].items():
        if date[:7] == current_month:
            for cat in totals:
                totals[cat] += record.get(cat, 0)
    if sum(totals.values()) == 0:
        error("No data for this month.")
        return
    plt.bar(totals.keys(), totals.values())
    plt.title("Monthly Spending (Bar Chart)")
    plt.show()


def category_pie_chart(data):
    totals = {"Food": 0, "Transportation": 0, "Bills": 0, "Others": 0}
    current_month = get_today()[:7]
    for date, record in data["history"].items():
        if date[:7] == current_month:
            for cat in totals:
                totals[cat] += record.get(cat, 0)
    if sum(totals.values()) == 0:
        error("No data for this month.")
        return
    plt.pie(totals.values(), labels=totals.keys(), autopct="%1.1f%%")
    plt.title("Spending Distribution (Pie Chart)")
    plt.show()


# ================= CHART MENU =================

def chart_menu(data):
    while True:
        header("CHARTS")
        print("  [1]  Savings Over Time")
        print("  [2]  Monthly Bar Chart")
        print("  [3]  Spending Pie Chart")
        print("  [4]  Back")
        divider()
        choice == input(" >> ")
        if choice == "1":
            savings_chart(data)
        elif choice == "2":
            monthly_chart(data)
        elif choice == "3":
         category_pie_chart(data)
        elif choice == "4":
            break
        else:
         error("Invalid choice.")


# ================= CATEGORY PICKER =================

def pick_category():
    header("SELECT CATEGORY")
    print("  [1]  Food")
    print("  [2]  Transportation")
    print("  [3]  Bills")
    print("  [4]  Others")
    divider()
    return input("  >> ")


# ================= MAIN =================

login = LoginManager()
user = login.start()

dm = DataManager(user.username)
data = dm.load_data()

mapping = {
    "1": "Food",
    "2": "Transportation",
    "3": "Bills",
    "4": "Others"
}

while True:
    header("BUDGET BUDDY")
    print(f"  User      : {user.username}")
    print(f"  Allowance : ₱{data['allowance']:.2f}")
    print(f"  Date      : {get_today()}")
    divider()
    print("  [1]  Add Expense")
    print("  [2]  View Expenses")
    print("  [3]  Edit Expense")
    print("  [4]  Delete Expense")
    print("  [5]  End Day")
    print("  [6]  Charts")
    print("  [7]  Change Allowance")
    print("  [8]  Save & Exit")
    divider()
    choice = input("  >> ")

    while choice == "1":
        cat = pick_category()
        if cat in mapping:
            AddExpense(mapping[cat]).execute(data)
            dm.save_data(data)
            input("\n  Press Enter to go back")

        elif choice == "2":
            view_expenses(data)
            input("\n  Press Enter to go back")

        elif choice == "3":
            cat = pick_category()
    if cat in mapping:
            EditExpense(mapping[cat]).execute(data)
            dm.save_data(data)
            input("\n  Press Enter to go back")

    elif choice == "4":
        cat = pick_category()
        if cat in mapping:
            DeleteExpense(mapping[cat]).execute(data)
            dm.save_data(data)
            input("\n  Press Enter to go back")
    elif choice == "5":
        end_day(data)
        dm.save_data(data)
        input("\n  Press Enter to go back")
    elif choice == "6":
        chart_menu(data)
    elif choice == "7":
        change_allowance(data)
        dm.save_data(data)
        input("\n Press Enter to go back")

    elif choice == "8":
        header("GOODBYE")
        info(f"Data saved. See you next time, {user.username}!")
        dm.save_data(data)
        break

    else:
        error("Invalid choice.")
        ("\n  Press Enter to go back")