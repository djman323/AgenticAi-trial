import tkinter as tk
import math

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("Calculator")

        self.display = tk.Entry(master, width=30, borderwidth=5)
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Define buttons
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+',
            'sqrt', 'C'
        ]

        # Create buttons
        row_val = 1
        col_val = 0
        for button in buttons:
            tk.Button(master, text=button, padx=20, pady=20,
                      command=lambda b=button: self.button_click(b)).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

    def button_click(self, button):
        if button == '=':
            try:
                result = eval(self.display.get())
                self.display.delete(0, tk.END)
                self.display.insert(0, result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
        elif button == 'C':
            self.display.delete(0, tk.END)
        elif button == 'sqrt':
            try:
                result = math.sqrt(float(self.display.get()))
                self.display.delete(0, tk.END)
                self.display.insert(0, result)
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Error")
        else:
            current = self.display.get()
            self.display.delete(0, tk.END)
            self.display.insert(0, str(current) + button)


root = tk.Tk()
my_calculator = Calculator(root)
root.mainloop()
