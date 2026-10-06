import tkinter as tk

# Create window
root = tk.Tk()
root.title("Calculator")
root.geometry("300x400")

# Entry box
display = tk.Entry(root, font=("Arial", 24), justify="right")
display.pack(fill="both", padx=10, pady=10, ipady=10)


# Functions
def click(value):
    display.insert(tk.END, value)


def clear():
    display.delete(0, tk.END)


def backspace():
    text = display.get()
    display.delete(0, tk.END)
    display.insert(0, text[:-1])


def calculate():
    try:
        result = eval(display.get())
        display.delete(0, tk.END)
        display.insert(0, result)
    except:
        display.delete(0, tk.END)
        display.insert(0, "Error")


# Buttons
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"]
]

for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    for button in row:
        if button == "=":
            command = calculate
        else:
            command = lambda x=button: click(x)

        tk.Button(
            frame,
            text=button,
            font=("Arial", 18),
            command=command
        ).pack(
            side="left",
            expand=True,
            fill="both",
            padx=2,
            pady=2
        )


# Clear and Backspace buttons
frame = tk.Frame(root)
frame.pack(expand=True, fill="both")

tk.Button(
    frame,
    text="Clear",
    font=("Arial", 14),
    command=clear
).pack(side="left", expand=True, fill="both", padx=2, pady=2)

tk.Button(
    frame,
    text="⌫",
    font=("Arial", 14),
    command=backspace
).pack(side="left", expand=True, fill="both", padx=2, pady=2)


# Run application
root.mainloop()

How to run

Save it as:

calculator.py

Then run:

python calculator.py

It will open a calculator window with +, -, ×, ÷, decimal, =, Clear, and Backspace.