import tkinter as tk
from tkinter import filedialog, messagebox
import osmnx as ox
from math import radians, sin, cos, sqrt, atan2
from dijkstra import Dijkstra
from PIL import ImageGrab, Image, ImageDraw, ImageTk, ImageFont
import io

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
        
        # Frame principal com padding
        main_frame = tk.Frame(self, bg="#1a1b1e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame horizontal para botões, canvas e histórico
        content_frame = tk.Frame(main_frame, bg="#1a1b1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame vertical de botões à esquerda
        botoes_frame = tk.Frame(content_frame, bg="#232428", width=180, height=650, highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        botoes_frame.pack(side=tk.LEFT, padx=(0,20))
        botoes_frame.pack_propagate(False)
        botoes_frame.place = None  # Evita warnings de IDE
        # Estilo dos botões
        btn_style = {
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
        # Botões empilhados verticalmente
        self.btn_importar = tk.Button(botoes_frame, text="📂 Importar Mapa", command=self.importar_osm, **btn_style)
        self.btn_importar.pack(fill=tk.X, pady=(10, 5), padx=10)
        self.btn_rota = tk.Button(botoes_frame, text="🛣️ Calcular Rota", command=self.calcular_rota, **btn_style)
        self.btn_rota.pack(fill=tk.X, pady=5, padx=10)
        self.btn_limpar = tk.Button(botoes_frame, text="🗑️ Limpar", command=self.limpar_selecao, **btn_style)
        self.btn_limpar.pack(fill=tk.X, pady=5, padx=10)
        self.btn_pontos = tk.Button(botoes_frame, text="👁️ Ocultar Pontos", command=self.toggle_pontos, **btn_style)
        self.btn_pontos.pack(fill=tk.X, pady=5, padx=10)
        self.btn_copiar = tk.Button(botoes_frame, text="📋 Copiar Imagem", command=self.copiar_imagem_canvas, **btn_style)
        self.btn_copiar.pack(fill=tk.X, pady=5, padx=10)
        self.btn_dist = tk.Button(botoes_frame, text="Exibir Distâncias", command=self.toggle_distancias, **btn_style)
        self.btn_dist.pack(fill=tk.X, pady=5, padx=10)
        self.btn_cores = tk.Button(botoes_frame, text="Cores das Ruas", command=self.toggle_cores_ruas, **btn_style)
        self.btn_cores.pack(fill=tk.X, pady=5, padx=10)

        # Canvas central
        self.canvas = tk.Canvas(content_frame, bg="#2a2b2e", width=900, height=650, 
                              highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        self.canvas.pack(side=tk.LEFT)
        
        # Painel de histórico à direita (mantém 320 de largura)
        historico_frame = tk.Frame(content_frame, bg="#232428", width=320, height=650, highlightthickness=1, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        historico_frame.pack(side=tk.LEFT, padx=(20,0))
        historico_frame.pack_propagate(False)
        
        # Título fixo
        titulo_hist = tk.Label(historico_frame, text="Histórico de Rotas", bg="#232428", fg="#00ffcc", font=("Segoe UI", 13, "bold"), pady=10)
        titulo_hist.pack(fill=tk.X)
        
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

    def importar_osm(self):
        caminho = filedialog.askopenfilename(filetypes=[("OSM files", "*.osm"), ("Todos arquivos", "*.*")])
        if caminho:
            try:
                self.grafo = ox.graph_from_xml(caminho)
                self.origem = None
                self.destino = None
                self.caminho = None
                self.desenhar_grafo()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

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
        supersample = 4
        w, h = 900, 650
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        try:
            font = ImageFont.truetype("arial.ttf", 5*supersample)
        except Exception:
            font = ImageFont.load_default()
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        if not self.grafo:
            self.canvas.delete("all")
            return
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

    def on_canvas_motion(self, event):
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
            return
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

    def calcular_rota(self):
        if not self.grafo or not self.origem or not self.destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
        # Converter o grafo do NetworkX para nosso formato
        grafo_dijkstra = {}
        for u, v, data in self.grafo.edges(data=True):
            if u not in grafo_dijkstra:
                grafo_dijkstra[u] = {}
            if v not in grafo_dijkstra:
                grafo_dijkstra[v] = {}
            # Calcular a distância real entre os nós
            dist = self.calcular_distancia(
                self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'],
                self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x']
            )
            # Verificar se é uma via de mão única
            oneway = data.get('oneway', False)
            # Adicionar aresta na direção u->v
            grafo_dijkstra[u][v] = dist
            # Se não for mão única, adicionar aresta na direção v->u
            if not oneway:
                grafo_dijkstra[v][u] = dist
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
        from datetime import datetime
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

    def atualizar_historico(self):
        # Limpa cards antigos
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for i, info in enumerate(reversed(self.historico_rotas), 1):
            card = tk.Frame(self.cards_frame, bg="#262a2f", bd=0, highlightthickness=0)
            card.pack(fill=tk.X, pady=12, padx=0, ipadx=0, ipady=0)
            # Frame interno para padding
            inner = tk.Frame(card, bg="#262a2f")
            inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)
            # Botão de refazer rota (emoji)
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
            titulo = tk.Label(inner, text=f"#{len(self.historico_rotas)-i+1}  {info['datahora']}", bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"), anchor="w", pady=2)
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

    def limpar_selecao(self):
        self.origem = None
        self.destino = None
        self.caminho = None
        self.selecionando = 'origem'
        self.mostrar_pontos = True
        self.btn_pontos.config(text="Ocultar Pontos")
        self.desenhar_grafo()

    def toggle_pontos(self):
        self.mostrar_pontos = not self.mostrar_pontos
        self.btn_pontos.config(text="Mostrar Pontos" if not self.mostrar_pontos else "Ocultar Pontos")
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
        # Copia para a área de transferência (Windows)
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

if __name__ == '__main__':
    app = MapaTkinter()
    app.mainloop() 