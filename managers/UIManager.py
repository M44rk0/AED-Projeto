import tkinter as tk

class UIManager:
    def __init__(self, main_app):
        self.main_app = main_app
    
    def mostrar_botoes_centrais(self):
        #Mostra botões centrais quando não há grafo
        if self.main_app.graph_manager.existe_grafo() or self.main_app.modo_edicao:
            return

        if hasattr(self.main_app, 'central_frame'):
            self.main_app.central_frame.destroy()

        central_frame = tk.Frame(self.main_app.canvas, bg="#2a2b2e", bd=0, highlightthickness=0)

        btn_central_style = {
            "bg": "#232428",
            "fg": "#ffffff",
            "activebackground": "#3a3b3e",
            "activeforeground": "#00ffcc",
            "font": ("Segoe UI", 12, "bold"),
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": "#3a3b3e",
            "padx": 25,
            "pady": 15,
            "cursor": "hand2"
        }

        btn_importar_central = tk.Button(central_frame, text="📂 Importar Mapa OSM",
                                         command=self.main_app.importar_osm, **btn_central_style)
        btn_importar_central.pack(pady=(0, 20))

        btn_criar_central = tk.Button(central_frame, text="✏️ Criar Grafo Manual",
                                      command=self.main_app.toggle_modo_edicao, **btn_central_style)
        btn_criar_central.pack()

        central_frame.update_idletasks()
        frame_width = central_frame.winfo_reqwidth()
        frame_height = central_frame.winfo_reqheight()

        canvas_width = self.main_app.canvas.winfo_width()
        canvas_height = self.main_app.canvas.winfo_height()

        if canvas_width <= 1:
            canvas_width = 900
        if canvas_height <= 1:
            canvas_height = 600

        x = (canvas_width - frame_width) // 2
        y = (canvas_height - frame_height) // 2

        self.main_app.canvas.create_window(x, y, window=central_frame, anchor="nw")
        self.main_app.central_frame = central_frame

    def ocultar_botoes_centrais(self):
        #Oculta os botões centrais
        if hasattr(self.main_app, 'central_frame'):
            self.main_app.central_frame.destroy()
            delattr(self.main_app, 'central_frame')
    
    def atualizar_estado_botoes(self):
        #Atualiza o estado de todos os botões
        grafo_osm = self.main_app.graph_manager.eh_grafo_osm() if self.main_app.graph_manager.existe_grafo() else False
        tem_grafo_valido = self.main_app.graph_manager.existe_grafo()
        tem_vertices = self.main_app.graph_manager.existe_grafo() and len(self.main_app.graph_manager.grafo.nodes) > 0
        
        if self.main_app.modo_edicao:
            self.main_app.sidebar.configurar_estado_apagar_grafo(True)
            self.main_app.sidebar.habilitar_botoes_principais(False)
            self.main_app.action_panel.habilitar_botoes(False)
            self.main_app.zoom_panel.habilitar_botoes(False)
            self.main_app.zoom_panel.ocultar()
            self.main_app.sidebar.configurar_estado_criar_grafo(not grafo_osm)
            self.main_app.sidebar.habilitar_botoes_edicao(True)
            self.main_app.sidebar.configurar_estado_distancias(not grafo_osm and tem_grafo_valido)
        else:
            if tem_grafo_valido:
                self.main_app.sidebar.configurar_estado_apagar_grafo(tem_vertices)
                self.main_app.sidebar.habilitar_botoes_principais(True)
                self.main_app.action_panel.habilitar_botoes(True)
                self.main_app.zoom_panel.habilitar_botoes(True)
                self.main_app.zoom_panel.mostrar()
                self.main_app.sidebar.configurar_estado_distancias(not grafo_osm)
            else:
                self.main_app.sidebar.configurar_estado_apagar_grafo(False)
                self.main_app.sidebar.habilitar_botoes_principais(False)
                self.main_app.action_panel.habilitar_botoes(False)
                self.main_app.zoom_panel.habilitar_botoes(False)
                self.main_app.zoom_panel.ocultar()
                self.main_app.sidebar.configurar_estado_distancias(False)
            self.main_app.sidebar.configurar_estado_criar_grafo(not grafo_osm)