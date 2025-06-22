import tkinter as tk

class ZoomPanel:
    def __init__(self, canvas, main_app):
        self.canvas = canvas
        self.main_app = main_app
        self.overlay = None
        self.buttons = {}
        self.criar_zoom_panel()
    
    def criar_zoom_panel(self):
        #Cria o painel de zoom flutuante
        self.overlay = tk.Frame(self.canvas, bg=self.canvas['bg'], 
                              highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        self.overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        self.buttons['zoom_out'] = tk.Button(self.overlay, text="🔍-", 
                                           command=self.main_app.zoom_out, 
                                           bg=self.canvas['bg'], fg="#ffffff", 
                                           font=("Segoe UI", 10, "bold"),
                                           bd=0, relief="flat", padx=8, pady=4, 
                                           cursor="hand2", width=4, height=1)
        self.buttons['zoom_out'].pack(side=tk.LEFT, padx=(0, 2))
        
        self.buttons['zoom_reset'] = tk.Button(self.overlay, text="🔍", 
                                             command=self.main_app.zoom_reset,
                                             bg=self.canvas['bg'], fg="#00ffcc", 
                                             font=("Segoe UI", 10, "bold"),
                                             bd=0, relief="flat", padx=8, pady=4, 
                                             cursor="hand2", width=4, height=1)
        self.buttons['zoom_reset'].pack(side=tk.LEFT, padx=2)
        
        self.buttons['zoom_in'] = tk.Button(self.overlay, text="🔍+", 
                                          command=self.main_app.zoom_in,
                                          bg=self.canvas['bg'], fg="#ffffff", 
                                          font=("Segoe UI", 10, "bold"),
                                          bd=0, relief="flat", padx=8, pady=4, 
                                          cursor="hand2", width=4, height=1)
        self.buttons['zoom_in'].pack(side=tk.LEFT, padx=(2, 0))
    
    def mostrar(self):
        #Mostra o painel de zoom
        self.overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
    
    def ocultar(self):
        #Oculta o painel de zoom
        self.overlay.place_forget()
    
    def habilitar_botoes(self, habilitar=True):
        #Habilita ou desabilita os botões de zoom
        estado = tk.NORMAL if habilitar else tk.DISABLED
        cursor = "hand2" if habilitar else "arrow"
        for button in self.buttons.values():
            button.config(state=estado, cursor=cursor)
    
    def atualizar_texto_zoom(self, zoom_percent):
        #Atualiza o texto do botão de reset
        self.buttons['zoom_reset'].config(text=f"{zoom_percent}%")