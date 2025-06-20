import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import osmnx as ox
from math import radians, sin, cos, sqrt, atan2
from dijkstra import Dijkstra
from PIL import ImageGrab, Image, ImageDraw, ImageTk, ImageFont
import io
import networkx as nx
import os
from datetime import datetime

class MapaTkinter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cores_personalizadas = False
        self.title("Navegador OSM")
        self.configure(bg="#1a1b1e")
        self.geometry("1460x720")
        self.resizable(False, False)  # Impede maximizar
        self.mostrar_distancias = False
        self.img_pil = None
        self.imgtk = None
        self.modo_edicao = False
        self.vertice_selecionado = None
        self.criando_aresta = False
        self.contador_vertices = 0
        
        # Frame principal com padding
        main_frame = tk.Frame(self, bg="#1a1b1e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame horizontal para botões, canvas e histórico
        content_frame = tk.Frame(main_frame, bg="#1a1b1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame vertical de botões à esquerda
        botoes_frame = tk.Frame(content_frame, bg="#232428", width=180, highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        botoes_frame.pack(side=tk.LEFT, padx=(0,20), fill=tk.Y)
        botoes_frame.pack_propagate(False)
        botoes_frame.place = None  # Evita warnings de IDE
        
        # --- Frame Central para Canvas e botões de ação ---
        center_panel = tk.Frame(content_frame, bg="#1a1b1e")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- Frame para botões de ação abaixo do canvas ---
        actions_frame = tk.Frame(center_panel, bg="#1a1b1e")
        actions_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        # Configurar colunas para terem o mesmo peso e se expandirem igualmente
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)

        # Canvas central
        self.canvas = tk.Canvas(center_panel, bg="#2a2b2e", 
                              highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Estilo dos botões
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
        
        # Botões empilhados verticalmente
        self.btn_importar = tk.Button(botoes_frame, text="📂 Importar OSM", command=self.importar_osm, **self.btn_style_normal)
        self.btn_importar.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        self.btn_criar_grafo = tk.Button(botoes_frame, text="✏️ Criar Grafo", command=self.toggle_modo_edicao, **self.btn_style_normal)
        self.btn_criar_grafo.pack(fill=tk.X, pady=5, padx=10)
        
        # Frame para os botões de edição (inicialmente oculto)
        self.edicao_frame = tk.Frame(botoes_frame, bg="#232428")
        # Não usamos .pack() aqui, será controlado pelo toggle_modo_edicao

        self.btn_gerar_vertices = tk.Button(self.edicao_frame, text="🎯 Gerar Vértices", command=self.gerar_vertices_aleatorios, **self.btn_style_normal)
        self.btn_gerar_vertices.pack(fill=tk.X, pady=(5,5), padx=0)
        
        self.btn_gerar_arestas = tk.Button(self.edicao_frame, text="🎲 Gerar Arestas", command=self.gerar_arestas_aleatorias, **self.btn_style_normal)
        self.btn_gerar_arestas.pack(fill=tk.X, pady=(0,5), padx=0)
        
        self.btn_apagar_grafo = tk.Button(botoes_frame, text="🗑️ Apagar Grafo", command=self.apagar_grafo, **self.btn_style_normal)
        self.btn_apagar_grafo.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_copiar = tk.Button(botoes_frame, text="📋 Copiar Imagem", command=self.copiar_imagem_canvas, **self.btn_style_normal)
        self.btn_copiar.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_salvar = tk.Button(botoes_frame, text="💾 Salvar Imagem", command=self.salvar_imagem_canvas, **self.btn_style_normal)
        self.btn_salvar.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_dist = tk.Button(botoes_frame, text="Exibir Distâncias", command=self.toggle_distancias, **self.btn_style_normal)
        self.btn_dist.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_cores = tk.Button(botoes_frame, text="Identificar Ruas", command=self.toggle_cores_ruas, **self.btn_style_normal)
        self.btn_cores.pack(fill=tk.X, pady=5, padx=10)

        # --- Widgets do painel de ações ---
        self.btn_limpar = tk.Button(actions_frame, text="Limpar Seleção", command=self.limpar_selecao, **self.btn_style_normal)
        self.btn_limpar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        # Botão de rota no meio com borda branca
        rota_frame = tk.Frame(actions_frame, bg="#3a3b3e", padx=1.5, pady=1.5)
        rota_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.btn_rota = tk.Button(rota_frame, text="🛣️ Calcular Rota", command=self.calcular_rota, 
                                 **self.btn_style_normal)
        self.btn_rota.pack(fill=tk.BOTH, expand=True)
        
        self.btn_pontos = tk.Button(actions_frame, text="Ocultar Vértices", command=self.toggle_pontos, **self.btn_style_normal)
        self.btn_pontos.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        # Painel de histórico à direita
        historico_frame = tk.Frame(content_frame, bg="#232428", width=320, highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        historico_frame.pack(side=tk.LEFT, padx=(20,0), fill=tk.Y)
        historico_frame.pack_propagate(False)
        
        
        # Frame para o Canvas de cards e scrollbar
        self.historico_canvas = tk.Canvas(historico_frame, bg="#232428", highlightthickness=0, bd=0)
        self.historico_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0), pady=(0,5))
        
        self.historico_scrollbar = tk.Scrollbar(historico_frame, orient="vertical", command=self.historico_canvas.yview, bg="#232428")
        self.historico_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historico_canvas.configure(yscrollcommand=self.historico_scrollbar.set)
        
        self.cards_frame = tk.Frame(self.historico_canvas, bg="#232428")
        
        # Criamos a janela no canvas com âncora 'nw' e margem de 20px
        self.cards_frame_window = self.historico_canvas.create_window(
            (20, 0), 
            window=self.cards_frame, 
            anchor="nw" 
        )
        # Função para ajustar a largura do cards_frame ao canvas, deixando 20px de margem em cada lado
        def ajustar_largura_cards(event):
            canvas_width = event.width
            self.historico_canvas.itemconfig(self.cards_frame_window, width=canvas_width-40)
        self.historico_canvas.bind('<Configure>', ajustar_largura_cards)
        # Configuração do scrollregion
        self.cards_frame.bind(
            "<Configure>",
            lambda e: self.historico_canvas.configure(scrollregion=self.historico_canvas.bbox("all"))
        )
        # Scroll do mouse
        def _on_mousewheel(event):
            self.historico_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.historico_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        self.historico_rotas = []
        self.historico_capturas = []

        self.grafo = None
        self.bbox = None
        self.origem = None
        self.destino = None
        self.pos = None
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        self.caminho = None
        self.mostrar_pontos = True
        self.selecionando = 'origem'
        # Tooltip como Label fixo
        self.tooltip_label = tk.Label(self.canvas, bg="#2a2b2e", fg="#fff", font=("Segoe UI", 9), bd=0, relief=tk.FLAT, padx=8, pady=4)
        self.tooltip_label.place_forget()
        self.tooltip_highlight_nodes = []
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-2>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_click)
        
        # Inicializar estado dos botões
        self.atualizar_estado_botoes()

    def importar_osm(self):
        caminho = filedialog.askopenfilename(filetypes=[("OSM files", "*.osm"), ("Todos arquivos", "*.*")])
        if caminho:
            try:
                self.grafo = ox.graph_from_xml(caminho)
                self.origem = None
                self.destino = None
                self.caminho = None
                self.atualizar_estado_botoes()  # Atualizar estado dos botões após importar
                self.desenhar_grafo()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def recalcular_contador_vertices(self):
        """Recalcula o contador de vértices baseado nos IDs existentes"""
        if self.grafo and self.grafo.nodes():
            self.contador_vertices = max(self.grafo.nodes()) + 1
        else:
            self.contador_vertices = 1  # Começar do ID 1

    def obter_proximo_id_vertice(self):
        """Obtém o próximo ID disponível para um vértice"""
        if not self.grafo or not self.grafo.nodes():
            return 1  # Começar do ID 1 em vez de 0
        
        # Encontrar o menor ID não utilizado
        ids_utilizados = set(self.grafo.nodes())
        proximo_id = 1  # Começar do ID 1
        while proximo_id in ids_utilizados:
            proximo_id += 1
        return proximo_id

    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        R = 6371000  # Raio da Terra em metros
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def show_tooltip(self, text, x, y, highlight_nodes=None):
        # x, y são coordenadas absolutas da tela, converter para canvas
        canvas_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        self.tooltip_label.config(text=text)
        self.tooltip_label.place(x=canvas_x+10, y=canvas_y+10)
        self.tooltip_highlight_nodes = []

    def hide_tooltip(self, event=None):
        self.tooltip_label.place_forget()
        self.tooltip_highlight_nodes = []

    def make_edge_enter_callback(self, tooltip_text, u, v):
        return lambda e: self.show_tooltip(tooltip_text, e.x_root, e.y_root, highlight_nodes=[u, v])

    def make_node_enter_callback(self, node):
        return lambda e: self.show_tooltip(f"Vértice: {node}", e.x_root, e.y_root)

    def desenhar_grafo(self):
        """Função principal que decide qual método de desenho usar"""
        if not self.grafo:
            self.canvas.delete("all")
            self.node_canvas_map = {}  # Limpar o mapeamento de nós
            self.edge_canvas_map = {}  # Limpar o mapeamento de arestas
            return
            
        # Detectar se é um grafo OSM
        grafo_osm = self.eh_grafo_osm()
        
        if grafo_osm:
            self.desenhar_grafo_osm()
        else:
            self.desenhar_grafo_manual()

    def eh_grafo_osm(self):
        """Detecta se o grafo foi importado do OSM"""
        if not self.grafo or len(self.grafo.nodes()) == 0:
            return False
            
        # Verificar se algum nó tem o atributo 'osmid' ou se há arestas com atributos OSM
        for _, data in self.grafo.nodes(data=True):
            if 'osmid' in data:
                return True
        # Se não encontrou nos nós, verificar nas arestas
        if len(self.grafo.edges()) > 0:
            for _, _, data in self.grafo.edges(data=True):
                if 'highway' in data or 'osmid' in data or 'geometry' in data:
                    return True
        return False

    def desenhar_grafo_osm(self):
        """Desenha grafos importados do OSM usando geometria"""
        self.update_idletasks()
        supersample = 4
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        # Fallback para caso o canvas não tenha sido renderizado ainda
        if w <= 1: w = 900
        if h <= 1: h = 600
        
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        try:
            font = ImageFont.truetype("arial.ttf", 5*supersample)
        except Exception:
            font = ImageFont.load_default()
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        
        nodes = list(self.grafo.nodes(data=True))
        xs = [data['x'] for _, data in nodes]
        ys = [data['y'] for _, data in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        def geo_to_canvas(x, y):
            cx = int((x - min_x) / (max_x - min_x) * (w - 40) + 20)
            cy = int((max_y - y) / (max_y - min_y) * (h - 40) + 20)
            return cx * supersample, cy * supersample
            
        # 1. Desenhar as ruas (arestas) primeiro
        for u, v, data in self.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.grafo.nodes[u]['x'], self.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.grafo.nodes[v]['x'], self.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            if self.cores_personalizadas:
                cor = '#2196f3' if oneway else '#ff9800'  # azul para única, laranja para dupla
            else:
                cor = '#77787C'
            if 'geometry' in data:
                xs, ys = data['geometry'].xy
                points = [geo_to_canvas(x, y) for x, y in zip(xs, ys)]
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i+1]], fill=cor, width=1*supersample)
            else:
                draw.line([(x0, y0), (x1, y1)], fill=cor, width=1*supersample)
            # Desenhar distância apenas uma vez por aresta
            if self.mostrar_distancias:
                dist = self.calcular_distancia(
                    self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'],
                    self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x']
                )
                txt = f"{dist:.0f}m"
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
                
        # 2. Desenhar o caminho mais curto (em vermelho)
        if self.caminho:
            for i in range(len(self.caminho)-1):
                n1, n2 = self.caminho[i], self.caminho[i+1]
                x1, y1 = geo_to_canvas(self.grafo.nodes[n1]['x'], self.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.grafo.nodes[n2]['x'], self.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=4*supersample)
                
        # 3. Desenhar os nós (vértices) por cima das arestas
        if self.mostrar_pontos:
            for node, data in self.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node == self.origem or node == self.destino:
                    continue
                r = 3 * supersample
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(245,245,245,200), outline='#CACACC', width=1*supersample)
                
        # 4. Desenhar marcadores de início/fim por último
        for node, data in self.grafo.nodes(data=True):
            if node == self.origem or node == self.destino:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = 10 * supersample
                if node == self.origem:
                    cor = (0,255,204,255)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=2*supersample)
                    draw.text((x-18*supersample, y-22*supersample), "",fill=(0,255,204,255))
                elif node == self.destino:
                    cor = (255,51,102,255)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=2*supersample)
                    draw.text((x-12*supersample, y-22*supersample), "",fill=(255,51,102,255))
                    
        # Redimensionar imagem para o tamanho do canvas com antialiasing
        img = img.resize((w, h), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.imgtk)

    def desenhar_grafo_manual(self):
        """Desenha grafos criados manualmente no modo de edição"""
        self.update_idletasks()
        supersample = 4
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        # Fallback para caso o canvas não tenha sido renderizado ainda
        if w <= 1: w = 900
        if h <= 1: h = 600
        
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        try:
            font = ImageFont.truetype("arial.ttf", 5*supersample)
        except Exception:
            font = ImageFont.load_default()
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        
        # Definir bbox fixo para o modo de edição
        if not self.bbox:
            self.bbox = (0, 0, 900, 650)  # bbox fixo baseado no tamanho do canvas
        min_x, min_y, max_x, max_y = self.bbox
        
        def geo_to_canvas(x, y):
            # Prevenir divisão por zero
            x_range = max_x - min_x
            y_range = max_y - min_y
            if x_range == 0: x_range = 1
            if y_range == 0: y_range = 1
            
            cx = int((x - min_x) / x_range * (w - 40) + 20)
            cy = int((max_y - y) / y_range * (h - 40) + 20)
            return cx * supersample, cy * supersample
            
        # 1. Desenhar as ruas (arestas) primeiro
        for u, v, data in self.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.grafo.nodes[u]['x'], self.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.grafo.nodes[v]['x'], self.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            if self.cores_personalizadas:
                cor = '#2196f3' if oneway else '#ff9800'  # azul para única, laranja para dupla
            else:
                cor = '#77787C'
            
            # Desenhar a linha da aresta
            draw.line([(x0, y0), (x1, y1)], fill=cor, width=1*supersample)
            
            # Desenhar peso da aresta
            if self.mostrar_distancias or self.modo_edicao:
                peso = data.get('weight', 0)
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                txt = f"{peso:.0f}m"
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
                
        # 2. Desenhar o caminho mais curto (em vermelho)
        if self.caminho:
            for i in range(len(self.caminho)-1):
                n1, n2 = self.caminho[i], self.caminho[i+1]
                x1, y1 = geo_to_canvas(self.grafo.nodes[n1]['x'], self.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.grafo.nodes[n2]['x'], self.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=4*supersample)
                
        # 3. Desenhar os nós (vértices)
        if self.mostrar_pontos or self.modo_edicao:
            for node, data in self.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                
                # Pular vértices de origem e destino (serão desenhados separadamente)
                if node == self.origem or node == self.destino:
                    continue
                
                # Definir cor e tamanho do vértice
                cor_vertice = (245,245,245,200)
                r = 3 * supersample
                outline_width = 1 * supersample
                outline_color = '#CACACC'
                
                if node == self.vertice_selecionado:
                    cor_vertice = (255,255,0,255)
                    r = 4 * supersample
                elif self.modo_edicao:
                    r = 4 * supersample
                
                # Desenhar círculo do vértice
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor_vertice, outline=outline_color, width=outline_width)
                
                # Desenhar número do vértice no modo edição
                if self.modo_edicao:
                    draw.text((x, y-15*supersample), str(node), fill="#ffffff", font=font, anchor="mm")
                
        # 4. Desenhar marcadores de início/fim por último
        for node, data in self.grafo.nodes(data=True):
            if node == self.origem or node == self.destino:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = 10 * supersample
                if node == self.origem:
                    cor = (0,255,204,255)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=2*supersample)
                    draw.text((x-18*supersample, y-22*supersample), "", fill=(0,255,204,255))
                elif node == self.destino:
                    cor = (255,51,102,255)
                    draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=2*supersample)
                    draw.text((x-12*supersample, y-22*supersample), "", fill=(255,51,102,255))
                
        # Redimensionar imagem para o tamanho do canvas com antialiasing
        img = img.resize((w, h), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.imgtk)

    def on_canvas_motion(self, event):
        # Verificar se há grafo antes de processar tooltips
        if not self.grafo or not self.node_canvas_map:
            self.hide_tooltip()
            return
            
        # Detectar vértice mais próximo do mouse
        min_dist = float('inf')
        closest_node = None
        for node, (x, y) in self.node_canvas_map.items():
            dist = ((event.x - x)**2 + (event.y - y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        if min_dist < 8:  # raio de detecção
            self.show_tooltip(f'Vértice: {closest_node}', event.x_root, event.y_root)
        else:
            self.hide_tooltip()

    def on_canvas_click(self, event):
        if not self.grafo:
            if self.modo_edicao:
                self.grafo = nx.Graph()
            else:
                return

        if self.modo_edicao:
            if event.num == 1:  # Clique esquerdo
                min_dist = float('inf')
                closest_node = None
                for node, (x, y) in self.node_canvas_map.items():
                    dist = ((event.x - x)**2 + (event.y - y)**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_node = node

                if min_dist < 8:  # Clicou em um vértice existente
                    if not self.vertice_selecionado:  # Primeiro vértice da aresta
                        self.vertice_selecionado = closest_node
                        self.criando_aresta = True
                    else:  # Segundo vértice da aresta
                        if closest_node != self.vertice_selecionado:
                            # Pedir peso da aresta
                            peso = self.pedir_peso_aresta()
                            if peso is not None:
                                self.grafo.add_edge(self.vertice_selecionado, closest_node, weight=peso)
                        self.vertice_selecionado = None
                        self.criando_aresta = False
                else:  # Clicou em espaço vazio - criar novo vértice
                    # Converter coordenadas do canvas para coordenadas geográficas
                    if not self.bbox:
                        self.bbox = (0, 0, 1, 1)  # bbox padrão se não existir
                    min_x, min_y, max_x, max_y = self.bbox
                    x_geo = min_x + (event.x / self.canvas.winfo_width()) * (max_x - min_x)
                    y_geo = max_y - (event.y / self.canvas.winfo_height()) * (max_y - min_y)
                    
                    novo_id = self.obter_proximo_id_vertice()
                    self.grafo.add_node(novo_id, x=x_geo, y=y_geo)
                    
            elif event.num == 2 or event.num == 3:  # Clique direito - remover vértice ou aresta
                min_dist = float('inf')
                closest_node = None
                for node, (x, y) in self.node_canvas_map.items():
                    dist = ((event.x - x)**2 + (event.y - y)**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        closest_node = node

                if min_dist < 8:  # Remover vértice
                    self.grafo.remove_node(closest_node)
                    # Recalcular contador de vértices após remoção
                    self.recalcular_contador_vertices()
                else:
                    # Tentar encontrar uma aresta próxima para remover
                    for u, v, data in self.grafo.edges(data=True):
                        x0, y0 = self.node_canvas_map[u]
                        x1, y1 = self.node_canvas_map[v]
                        # Calcular distância do ponto à linha (aresta)
                        dist = self.distancia_ponto_linha(event.x, event.y, x0, y0, x1, y1)
                        if dist < 5:  # Se o clique foi próximo à aresta
                            self.grafo.remove_edge(u, v)
                            break
            
            self.desenhar_grafo()
        else:
            # Código original para seleção de origem/destino
            min_dist = float('inf')
            closest_node = None
            for node, (x, y) in self.node_canvas_map.items():
                dist = ((event.x - x)**2 + (event.y - y)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest_node = node
            if min_dist < 8:
                if not self.origem:
                    self.origem = closest_node
                    self.selecionando = 'destino'
                elif not self.destino:
                    self.destino = closest_node
                    self.selecionando = 'origem'
                else:
                    self.origem = closest_node
                    self.destino = None
                    self.selecionando = 'destino'
                self.caminho = None
                self.desenhar_grafo()

    def pedir_peso_aresta(self):
        """Abre um diálogo para pedir o peso da aresta"""
        peso = simpledialog.askfloat("Peso da Aresta", 
                                   "Digite o peso (distância) da aresta:",
                                   minvalue=0.0)
        return peso

    def distancia_ponto_linha(self, px, py, x1, y1, x2, y2):
        """Calcula a distância de um ponto (px,py) a uma linha definida por (x1,y1) e (x2,y2)"""
        numerador = abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)
        denominador = sqrt((y2-y1)**2 + (x2-x1)**2)
        if denominador == 0:
            return float('inf')
        return numerador/denominador

    def calcular_rota(self):
        if not self.grafo or not self.origem or not self.destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
            
        # Verificar se os vértices origem e destino existem no grafo
        if self.origem not in self.grafo.nodes() or self.destino not in self.grafo.nodes():
            messagebox.showwarning("Aviso", "Vértices de origem ou destino não existem no grafo!")
            return
            
        # Verificar se há arestas no grafo
        if len(self.grafo.edges()) == 0:
            messagebox.showwarning("Aviso", "Não há arestas no grafo! Adicione arestas para calcular rotas.")
            return
            
        # Converter o grafo do NetworkX para nosso formato
        grafo_dijkstra = {}
        for u, v, data in self.grafo.edges(data=True):
            if u not in grafo_dijkstra:
                grafo_dijkstra[u] = {}
            if v not in grafo_dijkstra:
                grafo_dijkstra[v] = {}
            
            # Usar o peso da aresta se existir, senão calcular a distância
            peso = data.get('weight', None)
            if peso is None:
                peso = self.calcular_distancia(
                    self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'],
                    self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x']
                )
            
            # Adicionar aresta em ambas as direções (grafo não direcionado)
            grafo_dijkstra[u][v] = peso
            grafo_dijkstra[v][u] = peso
        
        # Verificar se os vértices origem e destino estão conectados no grafo
        if self.origem not in grafo_dijkstra or self.destino not in grafo_dijkstra:
            messagebox.showwarning("Aviso", "Vértices de origem ou destino não estão conectados no grafo!")
            return
            
        try:
            # Criar instância do Dijkstra e calcular caminho
            dijkstra = Dijkstra(grafo_dijkstra)
            caminho, dist = dijkstra.encontrar_caminho(self.origem, self.destino)
            # Verificar se existe caminho
            if dist == float('inf') or not caminho or len(caminho) == 1:
                self.caminho = None
                self.desenhar_grafo()
                messagebox.showwarning("Sem caminho", "Não existe caminho entre os pontos selecionados!")
                return
            # Ocultar pontos antes de mostrar a linha da distância
            self.mostrar_pontos = False
            self.btn_pontos.config(text="Mostrar Pontos")
            self.caminho = caminho
            self.desenhar_grafo()
            # Mostrar estatísticas
            stats = dijkstra.get_estatisticas()
            info = {
                'origem': self.origem,
                'destino': self.destino,
                'distancia': dist,
                'tempo': stats['tempo'],
                'nos_explorados': stats['nos_explorados'],
                'caminho': caminho.copy(),
                'datahora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            self.historico_rotas.append(info)
            self.atualizar_historico()
        except KeyError as e:
            messagebox.showwarning("Erro", f"Erro ao calcular rota: vértice {e} não encontrado no grafo!")
            return
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao calcular rota: {str(e)}")
            return

    def atualizar_historico(self):
        # Limpa cards antigos
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        # Combinar rotas e capturas em uma lista única com tipo
        historico_completo = []
        
        # Adicionar rotas
        for info in self.historico_rotas:
            info['tipo'] = 'rota'
            historico_completo.append(info)
        
        # Adicionar capturas
        for info in self.historico_capturas:
            info['tipo'] = 'captura'
            historico_completo.append(info)
        
        # Ordenar por data/hora (mais recente primeiro)
        historico_completo.sort(key=lambda x: datetime.strptime(x['datahora'], '%d/%m/%Y %H:%M:%S'), reverse=True)
        
        for i, info in enumerate(historico_completo, 1):
            card = tk.Frame(self.cards_frame, bg="#262a2f", bd=0, highlightthickness=0)
            card.pack(fill=tk.X, pady=12, padx=0, ipadx=0, ipady=0)
            # Frame interno para padding
            inner = tk.Frame(card, bg="#262a2f")
            inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            
            if info['tipo'] == 'rota':
                # Card de rota
                def refazer_rota(event=None, info=info):
                    caminho_salvo = info.get('caminho', None)
                    if not caminho_salvo or not all(n in self.grafo.nodes for n in caminho_salvo):
                        messagebox.showwarning("Aviso", "Não é possível redesenhar esta rota: o grafo foi alterado ou nós não existem mais.")
                        return
                    self.origem = info['origem']
                    self.destino = info['destino']
                    self.caminho = caminho_salvo.copy()
                    self.mostrar_pontos = False
                    self.btn_pontos.config(text="Mostrar Pontos")
                    self.desenhar_grafo()
                
                # Título
                titulo = tk.Label(inner, text=f"🛣️ #{len(historico_completo)-i+1}  {info['datahora']}", bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"), anchor="w", pady=2)
                titulo.pack(fill=tk.X, padx=0, pady=(0,6))
                # Informações
                info_textos = [
                    ("Origem:", info['origem']),
                    ("Destino:", info['destino']),
                    ("Distância:", f"{info['distancia']:.2f} m"),
                    ("Tempo:", f"{info['tempo']*1000:.2f} ms"),
                    ("Nós explorados:", info['nos_explorados'])
                ]
                for label, valor in info_textos:
                    linha = tk.Frame(inner, bg="#262a2f")
                    linha.pack(fill=tk.X, padx=0, pady=2)
                    l = tk.Label(linha, text=label, bg="#262a2f", fg="#bbbbbb", font=("Segoe UI", 9, "bold"), anchor="w")
                    l.pack(side=tk.LEFT)
                    v = tk.Label(linha, text=valor, bg="#262a2f", fg="#ffffff", font=("Segoe UI", 10), anchor="w")
                    v.pack(side=tk.LEFT, padx=(6,0))
                # Botão de refazer rota (emoji) no canto inferior direito
                btn_refazer = tk.Button(inner, text="🔄", bg="#232428", fg="#00ffcc", font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2", activebackground="#232428", activeforeground="#00ffcc", command=refazer_rota)
                btn_refazer.place(relx=1.0, rely=1.0, anchor='se', x=0, y=-8)
            
            elif info['tipo'] == 'captura':
                # Card de captura
                def abrir_imagem(event=None, info=info):
                    import subprocess
                    import platform
                    
                    try:
                        # Abrir a imagem com o programa padrão do sistema
                        if platform.system() == "Windows":
                            os.startfile(info['caminho'])
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", info['caminho']])
                        else:  # Linux
                            subprocess.run(["xdg-open", info['caminho']])
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao abrir imagem:\n{str(e)}")
                
                # Título com data/hora
                titulo_texto = f"📷 Captura #{len(historico_completo)-i+1}  {info['datahora']}"
                titulo = tk.Label(inner, text=titulo_texto, bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"), anchor="w")
                titulo.pack(fill=tk.X, padx=0, pady=(0,6))

                # Botão de abrir imagem, posicionado abaixo e à direita
                btn_abrir = tk.Button(inner, text="📂", bg="#232428", fg="#00ffcc", font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2", activebackground="#232428", activeforeground="#00ffcc", command=abrir_imagem)
                btn_abrir.pack(side=tk.RIGHT, pady=4)

    def limpar_selecao(self):
        self.origem = None
        self.destino = None
        self.caminho = None
        self.selecionando = 'origem'
        self.mostrar_pontos = True
        self.btn_pontos.config(text="Ocultar Vértices")
        self.desenhar_grafo()

    def toggle_pontos(self):
        self.mostrar_pontos = not self.mostrar_pontos
        self.btn_pontos.config(text="Mostrar Vértices" if not self.mostrar_pontos else "Ocultar Vértices")
        self.desenhar_grafo()

    def toggle_distancias(self):
        self.mostrar_distancias = not self.mostrar_distancias
        self.btn_dist.config(text="Ocultar Distâncias" if self.mostrar_distancias else "Exibir Distâncias")
        self.desenhar_grafo()

    def toggle_cores_ruas(self):
        self.cores_personalizadas = not self.cores_personalizadas
        self.desenhar_grafo()

    def copiar_imagem_canvas(self):
        # Pega as coordenadas do canvas na tela
        self.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        bbox = (x, y, x + w, y + h)
        # Captura a imagem da tela
        img = ImageGrab.grab(bbox)
        
        # Copiar para a área de transferência (Windows)
        output = io.BytesIO()
        img.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()
        try:
            self.clipboard_clear()
            self.clipboard_append('')  # Limpa clipboard texto
            self.update()
            self.clipboard_clear()
            self.update()
            self.clipboard_get()  # Força atualização
        except Exception:
            pass
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            messagebox.showinfo("Imagem copiada", "A imagem do grafo foi copiada para a área de transferência!")
        except Exception as e:
            messagebox.showerror("Erro ao copiar imagem", f"Erro ao copiar imagem para a área de transferência.\n{e}")

    def salvar_imagem_canvas(self):
        # Pega as coordenadas do canvas na tela
        self.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        bbox = (x, y, x + w, y + h)
        # Captura a imagem da tela
        img = ImageGrab.grab(bbox)
        
        # Criar a pasta "capturas" se não existir
        capturas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas")
        if not os.path.exists(capturas_dir):
            os.makedirs(capturas_dir)

        # Salvar a imagem automaticamente na pasta "capturas"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"grafo_{timestamp}.png"
        caminho_arquivo = os.path.join(capturas_dir, nome_arquivo)
        
        try:
            # Salvar a imagem
            img.save(caminho_arquivo)
            
            # Adicionar ao histórico de capturas
            info_captura = {
                'caminho': caminho_arquivo,
                'nome': nome_arquivo,
                'datahora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            self.historico_capturas.append(info_captura)
            self.atualizar_historico()
            
            messagebox.showinfo("Imagem salva", f"Imagem salva com sucesso!\n\nCaminho: {caminho_arquivo}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar imagem:\n{str(e)}")

    def toggle_modo_edicao(self):
        self.modo_edicao = not self.modo_edicao
        if self.modo_edicao:
            self.btn_criar_grafo.configure(**self.btn_style_ativo)
            # Mostra os botões de edição com recuo
            self.edicao_frame.pack(fill=tk.X, padx=(20, 10), pady=0, before=self.btn_apagar_grafo)
            
            if not self.grafo:
                self.grafo = nx.Graph()
            self.origem = None
            self.destino = None
            self.caminho = None
            self.vertice_selecionado = None
            self.criando_aresta = False
        else:
            self.btn_criar_grafo.configure(**self.btn_style_normal)
            # Esconde os botões de edição
            self.edicao_frame.pack_forget()
            self.vertice_selecionado = None
            self.criando_aresta = False
            
        self.atualizar_estado_botoes()
        self.desenhar_grafo()

    def gerar_arestas_aleatorias(self):
        """Gera arestas aleatórias entre os vértices existentes"""
        if not self.grafo or len(self.grafo.nodes()) < 2:
            messagebox.showwarning("Aviso", "É necessário ter pelo menos 2 vértices para gerar arestas!")
            return
            
        import random
        
        # Remover todas as arestas existentes
        self.grafo.remove_edges_from(list(self.grafo.edges()))
        
        # Pegar lista de vértices
        vertices = list(self.grafo.nodes())
        
        # Garantir que todos os vértices estejam conectados (árvore geradora)
        vertices_conectados = {vertices[0]}
        vertices_restantes = set(vertices[1:])
        
        while vertices_restantes:
            v1 = random.choice(list(vertices_conectados))
            v2 = random.choice(list(vertices_restantes))
            peso = random.randint(10, 100)  # Peso entre 10 e 100
            self.grafo.add_edge(v1, v2, weight=peso)
            vertices_conectados.add(v2)
            vertices_restantes.remove(v2)
        
        # Adicionar arestas extras aleatoriamente
        num_arestas_extras = len(vertices) * 2  # Ajuste este número para mais ou menos densidade
        for _ in range(num_arestas_extras):
            v1 = random.choice(vertices)
            v2 = random.choice(vertices)
            if v1 != v2 and not self.grafo.has_edge(v1, v2):
                peso = random.randint(10, 100)
                self.grafo.add_edge(v1, v2, weight=peso)
        
        self.desenhar_grafo()

    def gerar_vertices_aleatorios(self):
        """Gera vértices aleatórios no grafo"""
        # Pedir quantidade de vértices ao usuário
        quantidade = simpledialog.askinteger("Gerar Vértices", 
                                           "Quantos vértices deseja gerar?",
                                           minvalue=1, maxvalue=10000, initialvalue=10)
        
        if quantidade is None:  # Usuário cancelou
            return
            
        if not self.grafo:
            self.grafo = nx.Graph()
            
        import random
        
        # Gerar vértices aleatórios
        for _ in range(quantidade):
            x = random.uniform(50, 850)  # Margem de 50px das bordas
            y = random.uniform(50, 600)  # Margem de 50px das bordas
            novo_id = self.obter_proximo_id_vertice()
            self.grafo.add_node(novo_id, x=x, y=y)
        
        self.desenhar_grafo()
        # Atualizar estado dos botões
        self.atualizar_estado_botoes()

    def atualizar_estado_botoes(self):
        """Atualiza o estado dos botões baseado no modo de edição e se o grafo é OSM"""
        # Detectar se o grafo foi importado do OSM
        grafo_osm = self.eh_grafo_osm()
        
        # "Apagar Grafo" sempre disponível se há um grafo
        if self.grafo and len(self.grafo.nodes()) > 0:
            self.btn_apagar_grafo.config(state=tk.NORMAL)
        else:
            self.btn_apagar_grafo.config(state=tk.DISABLED)
        
        if self.modo_edicao:
            # No modo de edição, desabilitar botões não relacionados à edição
            self.btn_importar.config(state=tk.DISABLED)
            self.btn_rota.config(state=tk.DISABLED)
            self.btn_limpar.config(state=tk.DISABLED)
            self.btn_pontos.config(state=tk.DISABLED)
            self.btn_copiar.config(state=tk.DISABLED)
            self.btn_salvar.config(state=tk.DISABLED)
            self.btn_dist.config(state=tk.DISABLED)
            self.btn_cores.config(state=tk.DISABLED)
            # Desabilitar "Criar Grafo" se for grafo OSM
            if grafo_osm:
                self.btn_criar_grafo.config(state=tk.DISABLED)
                self.btn_gerar_arestas.config(state=tk.DISABLED)
                self.btn_gerar_vertices.config(state=tk.DISABLED)
            else:
                self.btn_criar_grafo.config(state=tk.NORMAL)
                self.btn_gerar_arestas.config(state=tk.NORMAL)
                self.btn_gerar_vertices.config(state=tk.NORMAL)
        else:
            # Fora do modo de edição, habilitar todos os botões exceto os de edição
            self.btn_importar.config(state=tk.NORMAL)
            self.btn_rota.config(state=tk.NORMAL)
            self.btn_limpar.config(state=tk.NORMAL)
            self.btn_pontos.config(state=tk.NORMAL)
            self.btn_copiar.config(state=tk.NORMAL)
            self.btn_salvar.config(state=tk.NORMAL)
            self.btn_dist.config(state=tk.NORMAL)
            self.btn_cores.config(state=tk.NORMAL)
            # Desabilitar "Criar Grafo" se for grafo OSM
            if grafo_osm:
                self.btn_criar_grafo.config(state=tk.DISABLED)
            else:
                self.btn_criar_grafo.config(state=tk.NORMAL)
            # Os botões de edição já estão ocultos, então não precisam ser desabilitados aqui.

    def apagar_grafo(self):
        """Apaga o grafo inteiro e reseta todas as variáveis relacionadas"""
        if not self.grafo or len(self.grafo.nodes()) == 0:
            return
        # Esconder tooltip imediatamente
        self.hide_tooltip()
        # Apagar o grafo
        self.grafo = None
        # Resetar variáveis relacionadas
        self.origem = None
        self.destino = None
        self.caminho = None
        self.vertice_selecionado = None
        self.criando_aresta = False
        self.contador_vertices = 1
        self.bbox = None
        # Limpar histórico de rotas
        self.historico_rotas = []
        self.historico_capturas = []
        self.atualizar_historico()
        # Redesenhar o canvas
        self.desenhar_grafo()
        # Atualizar estado dos botões
        self.atualizar_estado_botoes()

if __name__ == '__main__':
    app = MapaTkinter()
    app.mainloop() 