import tkinter as tk

class TelemetryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F1 Car Overview")
        self.root.geometry("400x500")
        self.canvas = tk.Canvas(self.root, bg="black", width=400, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw simple F1 car shape (body + wings)
        self.body = self.canvas.create_rectangle(170, 220, 230, 380, fill="red")
        self.front_wing = self.canvas.create_rectangle(150, 200, 250, 220, fill="darkred")
        self.rear_wing = self.canvas.create_rectangle(150, 380, 250, 400, fill="darkred")

        # Draw tires (colored by wear)
        self.tires = {
            "FL": self.canvas.create_oval(110, 180, 140, 210, fill="gray"),
            "FR": self.canvas.create_oval(260, 180, 290, 210, fill="gray"),
            "RL": self.canvas.create_oval(110, 410, 140, 440, fill="gray"),
            "RR": self.canvas.create_oval(260, 410, 290, 440, fill="gray")
        }

        self.texts = {
            "FL": self.canvas.create_text(125, 170, text="", fill="white"),
            "FR": self.canvas.create_text(275, 170, text="", fill="white"),
            "RL": self.canvas.create_text(125, 450, text="", fill="white"),
            "RR": self.canvas.create_text(275, 450, text="", fill="white"),
            "Tip": self.canvas.create_text(200, 470, text="", fill="white")
        }

    def update(self, data):
        for tire in ["FL", "FR", "RL", "RR"]:
            wear = data.get(tire, None)
            if wear is not None:
                color = self.get_wear_color(wear)
                self.canvas.itemconfig(self.tires[tire], fill=color)
                self.canvas.itemconfig(self.texts[tire], text=f"{tire}: {wear}%")

        tip = data.get("Strategy Tip", "")
        self.canvas.itemconfig(self.texts["Tip"], text=tip)

    def get_wear_color(self, wear):
        if wear < 30:
            return "green"
        elif wear < 60:
            return "yellow"
        else:
            return "red"

    def run(self):
        self.root.mainloop()
