import tkinter as tk

class HistoryPanel:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.canvas = None
        self.scrollbar = None
        self.cards_frame = None
        self.cards_frame_window = None
        self.criar_history_panel()
    
    def criar_history_panel(self):
        #Cria o painel de histórico
        self.frame = tk.Frame(self.parent, bg="#232428", width=320)
        self.frame.pack(side=tk.LEFT, padx=(10,0), fill=tk.Y)
        self.frame.pack_propagate(False)
        
        self.canvas = tk.Canvas(self.frame, bg="#232428", highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0), pady=(0,5))
        
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", 
                                    command=self.canvas.yview, bg="#232428")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.cards_frame = tk.Frame(self.canvas, bg="#232428")
        self.cards_frame_window = self.canvas.create_window((20, 0), window=self.cards_frame, anchor="nw")
        
        # Configurar ajuste de largura
        def ajustar_largura_cards(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.cards_frame_window, width=canvas_width-40)
        self.canvas.bind('<Configure>', ajustar_largura_cards)
        
        # Configurar scroll do mouse
        def _bind_mousewheel(event):
            self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Enter>', _bind_mousewheel)
        
        def _unbind_mousewheel(event):
            self.canvas.unbind_all('<MouseWheel>')
        self.canvas.bind('<Leave>', _unbind_mousewheel)
    
    def _on_mousewheel(self, event):
        #Manipula o scroll do mouse
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
    
    def limpar_cards(self):
        #Limpa todos os cards do histórico
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
    
    def atualizar_scrollregion(self):
        #Atualiza a região de scroll
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))