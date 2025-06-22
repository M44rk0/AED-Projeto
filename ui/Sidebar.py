import tkinter as tk

class Sidebar:
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
        self.btn_style_ativo = self.btn_style_normal.copy()
        self.btn_style_ativo.update({
            "bg": "#00ffcc",
            "fg": "#1a1b1e",
            "activebackground": "#00ddaa",
            "activeforeground": "#1a1b1e"
        })
        self.criar_sidebar()
    
    def criar_sidebar(self):
        #Cria o painel lateral com todos os botões
        self.frame = tk.Frame(self.parent, bg="#232428", width=180)
        self.frame.pack(side=tk.LEFT, padx=(0,10), fill=tk.Y)
        self.frame.pack_propagate(False)
        
        # Botões principais
        self.buttons['importar'] = tk.Button(self.frame, text="📂 Importar OSM", 
                                           command=self.main_app.importar_osm, **self.btn_style_normal)
        self.buttons['importar'].pack(fill=tk.X, pady=(10, 5), padx=10)
        
        self.buttons['criar_grafo'] = tk.Button(self.frame, text="✏️ Criar Grafo", 
                                              command=self.main_app.toggle_modo_edicao, **self.btn_style_normal)
        self.buttons['criar_grafo'].pack(fill=tk.X, pady=5, padx=10)
        
        # Frame de edição
        self.edicao_frame = tk.Frame(self.frame, bg="#232428")
        
        self.buttons['gerar_vertices'] = tk.Button(self.edicao_frame, text="🎯 Gerar Vértices", 
                                                 command=self.main_app.gerar_vertices_aleatorios, **self.btn_style_normal)
        self.buttons['gerar_vertices'].pack(fill=tk.X, pady=(5,5), padx=0)
        
        self.buttons['gerar_arestas'] = tk.Button(self.edicao_frame, text="🎲 Gerar Arestas", 
                                                command=self.main_app.gerar_arestas_aleatorias, **self.btn_style_normal)
        self.buttons['gerar_arestas'].pack(fill=tk.X, pady=(0,5), padx=0)
        
        self.buttons['apagar_grafo'] = tk.Button(self.frame, text="🗑️ Apagar Grafo", 
                                               command=self.main_app.apagar_grafo, **self.btn_style_normal)
        self.buttons['apagar_grafo'].pack(fill=tk.X, pady=5, padx=10)
        
        self.buttons['copiar'] = tk.Button(self.frame, text="📋 Copiar Imagem", 
                                         command=self.main_app.copiar_imagem_canvas, **self.btn_style_normal)
        self.buttons['copiar'].pack(fill=tk.X, pady=5, padx=10)
        
        self.buttons['salvar'] = tk.Button(self.frame, text="💾 Salvar Imagem", 
                                         command=self.main_app.salvar_imagem_canvas, **self.btn_style_normal)
        self.buttons['salvar'].pack(fill=tk.X, pady=5, padx=10)
        
        self.buttons['dist'] = tk.Button(self.frame, text="Exibir Distâncias", 
                                       command=self.main_app.toggle_distancias, **self.btn_style_normal)
        self.buttons['dist'].pack(fill=tk.X, pady=5, padx=10)
        
        self.buttons['cores'] = tk.Button(self.frame, text="Identificar Vias", 
                                        command=self.main_app.toggle_cores_ruas, **self.btn_style_normal)
        self.buttons['cores'].pack(fill=tk.X, pady=5, padx=10)
    
    def mostrar_frame_edicao(self):
        #Mostra o frame de edição
        self.edicao_frame.pack(fill=tk.X, padx=(20, 10), pady=0, before=self.buttons['apagar_grafo'])
    
    def ocultar_frame_edicao(self):
        #Oculta o frame de edicao
        self.edicao_frame.pack_forget()
    
    def configurar_botao_edicao(self, ativo=False):
        #Configura o botão de edição como ativo ou normal
        if ativo:
            self.buttons['criar_grafo'].configure(**self.btn_style_ativo)
        else:
            self.buttons['criar_grafo'].configure(**self.btn_style_normal)
    
    def habilitar_botoes_principais(self, habilitar=True):
        #Habilita ou desabilita os botões principais
        estado = tk.NORMAL if habilitar else tk.DISABLED
        # O botão importar sempre deve ficar habilitado
        self.buttons['importar'].config(state=tk.NORMAL)
        self.buttons['copiar'].config(state=estado)
        self.buttons['salvar'].config(state=estado)
        self.buttons['dist'].config(state=estado)
        self.buttons['cores'].config(state=estado)
    
    def habilitar_botoes_edicao(self, habilitar=True):
        #Habilita ou desabilita os botões de edição
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.buttons['gerar_vertices'].config(state=estado)
        
        # Botão de gerar arestas só fica habilitado se há pelo menos 2 vértices
        if habilitar and self.main_app.graph_manager.existe_grafo():
            tem_vertices_suficientes = len(self.main_app.graph_manager.grafo.nodes) >= 2
            estado_arestas = tk.NORMAL if tem_vertices_suficientes else tk.DISABLED
        else:
            estado_arestas = estado
        self.buttons['gerar_arestas'].config(state=estado_arestas)
    
    def configurar_estado_apagar_grafo(self, habilitar=True):
        #Configura o estado do botão apagar grafo
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.buttons['apagar_grafo'].config(state=estado)
    
    def configurar_estado_criar_grafo(self, habilitar=True):
        #Configura o estado do botão criar grafo
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.buttons['criar_grafo'].config(state=estado)
    
    def configurar_estado_distancias(self, habilitar=True):
        #Configura o estado do botão de distâncias (mostrar pesos das arestas)
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.buttons['dist'].config(state=estado)