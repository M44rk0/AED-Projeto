import tkinter as tk

class TooltipManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.tooltip_label = tk.Label(canvas, bg="#2a2b2e", fg="#fff", 
                                    font=("Segoe UI", 9), bd=0, relief=tk.FLAT, 
                                    padx=8, pady=4)
        self.tooltip_label.place_forget()
    
    def show_tooltip(self, text, x, y, is_contextual=False):
        #Mostra um tooltip na posição especificada
        canvas_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        
        if is_contextual:
            # Estilo para dicas contextuais
            self.tooltip_label.config(
                text=text,
                bg="#ffffcc",
                fg="#000000",
                font=("Segoe UI", 8),
                bd=1,
                relief=tk.SOLID
            )
        else:
            # Estilo padrão
            self.tooltip_label.config(
                text=text,
                bg="#2a2b2e",
                fg="#fff",
                font=("Segoe UI", 9),
                bd=0,
                relief=tk.FLAT
            )
        
        self.tooltip_label.place(x=canvas_x+10, y=canvas_y+10)
    
    def hide_tooltip(self):
        #Oculta o tooltip
        self.tooltip_label.place_forget()