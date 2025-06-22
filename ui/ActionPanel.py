import tkinter as tk

class ActionPanel:
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.frame = None
        self.buttons = {}
        self.btn_style_normal = {
            "bg": "#2a2b2e",
            "fg": "#ffffff",
            "activebackground": "#3a3b3e",
            "activeforeground": "#00ffcc",
            "font": ("Segoe UI", 10),
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        self.btn_style_desabilitado = self.btn_style_normal.copy()
        self.btn_style_desabilitado.update({
            "cursor": "arrow"
        })
        self.criar_action_panel()
    
    def criar_action_panel(self):
        #Cria o painel de ações inferiores
        self.frame = tk.Frame(self.parent, bg="#1a1b1e")
        self.frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        
        # Botão Limpar Seleção
        self.buttons['limpar'] = tk.Button(self.frame, text="Limpar Seleção", 
                                         command=self.main_app.limpar_selecao, 
                                         **self.btn_style_normal, width=15, height=1)
        self.buttons['limpar'].grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Botão Calcular Rota (com frame especial)
        rota_frame = tk.Frame(self.frame, bg="#3a3b3e", padx=2.5, pady=2.5)
        rota_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.buttons['rota'] = tk.Button(rota_frame, text="🛣️ Calcular Rota", 
                                       command=self.main_app.calcular_rota, 
                                       **self.btn_style_normal, width=15, height=1)
        self.buttons['rota'].pack(fill=tk.BOTH, expand=True)
        
        # Botão Mostrar/Ocultar Vértices
        self.buttons['pontos'] = tk.Button(self.frame, text="Ocultar Vértices", 
                                         command=self.main_app.toggle_pontos, 
                                         **self.btn_style_normal, width=15, height=1)
        self.buttons['pontos'].grid(row=0, column=2, sticky="nsew", padx=(5, 0))
    
    def habilitar_botoes(self, habilitar=True):
        #Habilita ou desabilita todos os botões do painel
        estado = tk.NORMAL if habilitar else tk.DISABLED
        estilo = self.btn_style_normal if habilitar else self.btn_style_desabilitado
        for button in self.buttons.values():
            button.config(state=estado, cursor=estilo["cursor"])
    
    def configurar_texto_pontos(self, mostrar=True):
        #Configura o texto do botão de pontos
        texto = "Mostrar Vértices" if not mostrar else "Ocultar Vértices"
        self.buttons['pontos'].config(text=texto)