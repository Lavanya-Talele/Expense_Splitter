import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from matplotlib import pyplot as plt

people = []
expenses = []


def add_person():
    name = entry_person.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter a name.")
        return
    if name not in people:
        people.append(name)
        update_output(f"Added {name} to the group.")
        entry_person.delete(0, tk.END)
    else:
        messagebox.showinfo("Duplicate", f"{name} is already in the group.")


def add_expense():
    payer = entry_payer.get().strip()
    amount = entry_amount.get().strip()
    desc = entry_desc.get().strip()

    if not (payer and amount and desc):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    if payer not in people:
        messagebox.showerror("Error", "Payer not found! Add the person first.")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Invalid amount entered.")
        return

    expenses.append({"payer": payer, "amount": amount, "desc": desc})
    update_output(f"Added expense: {payer} paid ₹{amount:.2f} for {desc}.")
    entry_payer.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_desc.delete(0, tk.END)


def show_expenses():
    if not expenses:
        update_output("No expenses recorded yet.")
        return

    output = "\nAll Expenses:\n\n"
    for i, e in enumerate(expenses, 1):
        output += f"{i}. {e['payer']} paid ₹{e['amount']:.2f} for {e['desc']}\n"
    update_output(output)


def calculate_split():
    if not people:
        messagebox.showwarning("Warning", "No people added.")
        return
    if not expenses:
        messagebox.showwarning("Warning", "No expenses recorded.")
        return

    total = sum(e["amount"] for e in expenses)
    share = total / len(people)
    balances = {p: -share for p in people}

    for e in expenses:
        balances[e["payer"]] += e["amount"]

    output = f"\nTotal Group Expense: ₹{total:.2f}\n"
    output += f"Individual Fair Share: ₹{share:.2f}\n\nBalances:\n\n"

    for p, bal in balances.items():
        status = "gets back" if bal > 0.01 else "owes"
        output += f"{p} {status} ₹{abs(bal):.2f}\n"

    output += "\nSuggested Settlements:\n\n"
    output += settle_balances(balances)
    update_output(output)


def settle_balances(balances):
    debtors = [(p, -bal) for p, bal in balances.items() if bal < -0.01]
    creditors = [(p, bal) for p, bal in balances.items() if bal > 0.01]

    debtors.sort(key=lambda x: x[1])
    creditors.sort(key=lambda x: x[1], reverse=True)

    result = ""
    i, j = 0, 0
    count = 0

    while i < len(debtors) and j < len(creditors):
        debtor, debt_amt = debtors[i]
        creditor, cred_amt = creditors[j]
        payment = min(debt_amt, cred_amt)
        result += f"{debtor} pays ₹{payment:.2f} to {creditor}\n"
        debt_amt -= payment
        cred_amt -= payment
        count += 1
        if debt_amt < 0.01:
            i += 1
        else:
            debtors[i] = (debtor, debt_amt)
        if cred_amt < 0.01:
            j += 1
        else:
            creditors[j] = (creditor, cred_amt)

    result += f"\nSettlement complete in {count} transactions.\n"
    return result


def show_chart():
    if not expenses:
        messagebox.showwarning("No Data", "No expenses to display.")
        return

    totals = {}
    for e in expenses:
        totals[e["payer"]] = totals.get(e["payer"], 0) + e["amount"]

    labels = list(totals.keys())
    values = list(totals.values())

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Expense Distribution by Member")
    plt.tight_layout()
    plt.show()


def save_data():
    data = {"people": people, "expenses": expenses}
    with open("group_data.json", "w") as f:
        json.dump(data, f, indent=4)
    messagebox.showinfo("Saved", "Data saved to group_data.json")


def load_data():
    global people, expenses
    try:
        with open("group_data.json", "r") as f:
            data = json.load(f)
        people = data.get("people", [])
        expenses = data.get("expenses", [])
        messagebox.showinfo("Loaded", "Data loaded successfully.")
    except FileNotFoundError:
        messagebox.showerror("Error", "No saved file found.")


def update_output(text):
    output_box.configure(state="normal")
    output_box.insert(tk.END, text + "\n\n")
    output_box.configure(state="disabled")
    output_box.see(tk.END)


root = tk.Tk()
root.title("Expense Splitter")
root.geometry("700x600")
root.resizable(False, False)

frame_person = tk.LabelFrame(root, text="Add Person")
frame_person.pack(fill="x", padx=10, pady=10)

tk.Label(frame_person, text="Name:").pack(side="left", padx=5)
entry_person = tk.Entry(frame_person)
entry_person.pack(side="left", padx=5)
tk.Button(frame_person, text="Add", command=add_person).pack(side="left", padx=5)

frame_expense = tk.LabelFrame(root, text="Add Expense")
frame_expense.pack(fill="x", padx=10, pady=10)

tk.Label(frame_expense, text="Payer:").grid(row=0, column=0, padx=5, pady=5)
entry_payer = tk.Entry(frame_expense, width=12)
entry_payer.grid(row=0, column=1, padx=5)

tk.Label(frame_expense, text="Amount:").grid(row=0, column=2, padx=5)
entry_amount = tk.Entry(frame_expense, width=10)
entry_amount.grid(row=0, column=3, padx=5)

tk.Label(frame_expense, text="Description:").grid(row=0, column=4, padx=5)
entry_desc = tk.Entry(frame_expense, width=15)
entry_desc.grid(row=0, column=5, padx=5)

tk.Button(frame_expense, text="Add Expense", command=add_expense).grid(row=0, column=6, padx=5)


frame_buttons = tk.Frame(root)
frame_buttons.pack(fill="x", pady=10)

tk.Button(frame_buttons, text="Show Expenses", width=15, command=show_expenses).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Calculate Split", width=15, command=calculate_split).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Show Chart", width=15, command=show_chart).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Save Data", width=15, command=save_data).pack(side="left", padx=10)
tk.Button(frame_buttons, text="Load Data", width=15, command=load_data).pack(side="left", padx=10)


output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, state="disabled")
output_box.pack(padx=10, pady=10)


root.mainloop()