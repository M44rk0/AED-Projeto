from PIL import Image, ImageDraw, ImageTk, ImageFont
from math import sqrt

class GraphDrawer:
    def __init__(self, canvas, graph_manager):
        self.canvas = canvas
        self.graph_manager = graph_manager
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        self.grid_cell_size = 50
    
    def obter_dimensoes_canvas(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        return w if w > 1 else 900, h if h > 1 else 600
    
    def obter_supersample(self, zoom_level):
        # Para zoom fluido, usar supersample menor
        if zoom_level != 1.0:
            return 2  # Supersample otimizado para zoom fluido
        return 3  # Supersample otimizado para zoom padrão
    
    def obter_tamanho_fonte(self, supersample, zoom_level):
        return int(5 * supersample * min(zoom_level, 2.0))
    
    def obter_tamanho_vertice(self, supersample, zoom_level, multiplicador=1):
        return int(3 * supersample * min(zoom_level, 2.0) * multiplicador)
    
    def obter_tamanho_marcador(self, supersample, zoom_level):
        return int(6 * supersample * min(zoom_level, 2.0))
    
    def desenhar_grid_fundo(self, draw, w, h, supersample):
        grid_color = '#151618'
        cell_size = self.grid_cell_size * supersample
        for x in range(0, w * supersample, cell_size):
            draw.line([(x, 0), (x, h * supersample)], fill=grid_color, width=1)
        for y in range(0, h * supersample, cell_size):
            draw.line([(0, y), (w * supersample, y)], fill=grid_color, width=1)
    
    def tem_zoom_ativo(self, zoom_level, pan_x, pan_y):
        return zoom_level != 1.0 or pan_x != 0 or pan_y != 0
    
    def desenhar_grafo_apropriado(self, zoom_level=1.0, pan_x=0, pan_y=0, 
                                mostrar_distancias=False, cores_personalizadas=False,
                                caminho=None, origem=None, destino=None,
                                mostrar_pontos=True, modo_edicao=False, vertice_selecionado=None):
        if not self.graph_manager.existe_grafo():
            return self.desenhar_canvas_vazio()
        
        if self.tem_zoom_ativo(zoom_level, pan_x, pan_y):
            return self.desenhar_grafo_otimizado(zoom_level, pan_x, pan_y, 
                                               mostrar_distancias, cores_personalizadas,
                                               caminho, origem, destino, mostrar_pontos, 
                                               modo_edicao, vertice_selecionado)
        else:
            return self.desenhar_grafo(zoom_level, pan_x, pan_y, 
                                     mostrar_distancias, cores_personalizadas,
                                     caminho, origem, destino, mostrar_pontos, 
                                     modo_edicao, vertice_selecionado)
    
    def desenhar_grafo_otimizado(self, zoom_level=1.0, pan_x=0, pan_y=0, 
                               mostrar_distancias=False, cores_personalizadas=False,
                               caminho=None, origem=None, destino=None,
                               mostrar_pontos=True, modo_edicao=False, vertice_selecionado=None):
        if self.graph_manager.eh_grafo_osm():
            return self.desenhar_grafo_osm_otimizado(zoom_level, pan_x, pan_y, 
                                                   mostrar_distancias, cores_personalizadas,
                                                   caminho, origem, destino, mostrar_pontos)
        else:
            return self.desenhar_grafo_manual_otimizado(zoom_level, pan_x, pan_y, 
                                                      mostrar_distancias, cores_personalizadas,
                                                      caminho, origem, destino, mostrar_pontos, 
                                                      modo_edicao, vertice_selecionado)
    
    def desenhar_grafo_osm_otimizado(self, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos):
        supersample = self.obter_supersample(zoom_level)
        w, h = self.obter_dimensoes_canvas()
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        self.desenhar_grid_fundo(draw, w, h, supersample)
        try:
            font_size = self.obter_tamanho_fonte(supersample, zoom_level)
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        nodes = list(self.graph_manager.grafo.nodes(data=True))
        xs = [data['x'] for _, data in nodes]
        ys = [data['y'] for _, data in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / zoom_level
        range_y = (max_y - min_y) / zoom_level
        zoomed_min_x = center_x - range_x / 2 + pan_x
        zoomed_max_x = center_x + range_x / 2 + pan_x
        zoomed_min_y = center_y - range_y / 2 + pan_y
        zoomed_max_y = center_y + range_y / 2 + pan_y
        def geo_to_canvas(x, y):
            cx = int((x - zoomed_min_x) / (zoomed_max_x - zoomed_min_x) * (w - 40) + 20)
            cy = int((zoomed_max_y - y) / (zoomed_max_y - zoomed_min_y) * (h - 40) + 20)
            return cx * supersample, cy * supersample
        for u, v, data in self.graph_manager.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.graph_manager.grafo.nodes[u]['x'], self.graph_manager.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[v]['x'], self.graph_manager.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            cor = '#2196f3' if (cores_personalizadas and oneway) else '#ff9800' if cores_personalizadas else '#77787C'
            if 'geometry' in data:
                xs, ys = data['geometry'].xy
                points = [geo_to_canvas(x, y) for x, y in zip(xs, ys)]
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i+1]], fill=cor, width=int(1*supersample*zoom_level))
            else:
                draw.line([(x0, y0), (x1, y1)], fill=cor, width=int(1*supersample*zoom_level))
            if mostrar_distancias:
                dist = self.graph_manager.calcular_distancia(
                    self.graph_manager.grafo.nodes[u]['y'], self.graph_manager.grafo.nodes[u]['x'],
                    self.graph_manager.grafo.nodes[v]['y'], self.graph_manager.grafo.nodes[v]['x']
                )
                txt = f"{dist:.0f}m"
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        if mostrar_pontos:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                r = self.obter_tamanho_vertice(supersample, zoom_level)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(245,245,245,200), outline='#CACACC', width=int(1*supersample*min(zoom_level, 2.0)))
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = self.obter_tamanho_marcador(supersample, zoom_level)
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk

    def desenhar_grafo_manual_otimizado(self, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos, modo_edicao, vertice_selecionado):
        supersample = self.obter_supersample(zoom_level)
        w, h = self.obter_dimensoes_canvas()
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        self.desenhar_grid_fundo(draw, w, h, supersample)
        try:
            font_size = self.obter_tamanho_fonte(supersample, zoom_level)
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        min_x, min_y, max_x, max_y = self.graph_manager.bbox or (0, 0, 900, 650)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / zoom_level
        range_y = (max_y - min_y) / zoom_level
        zoomed_min_x = center_x - range_x / 2 + pan_x
        zoomed_max_x = center_x + range_x / 2 + pan_x
        zoomed_min_y = center_y - range_y / 2 + pan_y
        zoomed_max_y = center_y + range_y / 2 + pan_y
        def geo_to_canvas(x, y):
            x_range = zoomed_max_x - zoomed_min_x
            y_range = zoomed_max_y - zoomed_min_y
            if x_range == 0: x_range = 1
            if y_range == 0: y_range = 1
            cx = int((x - zoomed_min_x) / x_range * (w - 40) + 20)
            cy = int((zoomed_max_y - y) / y_range * (h - 40) + 20)
            return cx * supersample, cy * supersample
        for u, v, data in self.graph_manager.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.graph_manager.grafo.nodes[u]['x'], self.graph_manager.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[v]['x'], self.graph_manager.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            cor = '#2196f3' if (cores_personalizadas and oneway) else '#ff9800' if cores_personalizadas else '#77787C'
            draw.line([(x0, y0), (x1, y1)], fill=cor, width=int(1*supersample*zoom_level))
            if mostrar_distancias or modo_edicao:
                peso = data.get('weight', 0)
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                txt = f"{peso:.0f}m"
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        if mostrar_pontos or modo_edicao:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                cor_vertice = (245,245,245,200)
                r = self.obter_tamanho_vertice(supersample, zoom_level)
                outline_width = int(1 * supersample * min(zoom_level, 2.0))
                outline_color = '#CACACC'
                if node == vertice_selecionado:
                    cor_vertice = (255,255,0,255)
                    r = self.obter_tamanho_vertice(supersample, zoom_level, 1.33)
                elif modo_edicao:
                    r = self.obter_tamanho_vertice(supersample, zoom_level, 1.33)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor_vertice, outline=outline_color, width=outline_width)
                if modo_edicao:
                    draw.text((x, y-int(15*supersample*min(zoom_level, 2.0))), str(node), fill="#ffffff", font=font, anchor="mm")
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = self.obter_tamanho_marcador(supersample, zoom_level)
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk

    def desenhar_grafo(self, zoom_level=1.0, pan_x=0, pan_y=0, 
                      mostrar_distancias=False, cores_personalizadas=False,
                      caminho=None, origem=None, destino=None,
                      mostrar_pontos=True, modo_edicao=False, vertice_selecionado=None):
        supersample = 4
        w, h = self.obter_dimensoes_canvas()
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        self.desenhar_grid_fundo(draw, w, h, supersample)
        
        try:
            font = ImageFont.truetype("arial.ttf", int(5*supersample*min(zoom_level, 2.0)))
        except Exception:
            font = ImageFont.load_default()
        
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        
        if self.graph_manager.eh_grafo_osm():
            self.desenhar_grafo_osm(draw, w, h, supersample, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos, font)
        else:
            self.desenhar_grafo_manual(draw, w, h, supersample, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos, modo_edicao, vertice_selecionado, font)
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk

    def desenhar_grafo_osm(self, draw, w, h, supersample, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos, font):
        nodes = list(self.graph_manager.grafo.nodes(data=True))
        xs = [data['x'] for _, data in nodes]
        ys = [data['y'] for _, data in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / zoom_level
        range_y = (max_y - min_y) / zoom_level
        zoomed_min_x = center_x - range_x / 2 + pan_x
        zoomed_max_x = center_x + range_x / 2 + pan_x
        zoomed_min_y = center_y - range_y / 2 + pan_y
        zoomed_max_y = center_y + range_y / 2 + pan_y
        def geo_to_canvas(x, y):
            cx = int((x - zoomed_min_x) / (zoomed_max_x - zoomed_min_x) * (w - 40) + 20)
            cy = int((zoomed_max_y - y) / (zoomed_max_y - zoomed_min_y) * (h - 40) + 20)
            return cx * supersample, cy * supersample
        for u, v, data in self.graph_manager.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.graph_manager.grafo.nodes[u]['x'], self.graph_manager.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[v]['x'], self.graph_manager.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            cor = '#2196f3' if (cores_personalizadas and oneway) else '#ff9800' if cores_personalizadas else '#77787C'
            if 'geometry' in data:
                xs, ys = data['geometry'].xy
                points = [geo_to_canvas(x, y) for x, y in zip(xs, ys)]
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i+1]], fill=cor, width=int(1*supersample*zoom_level))
            else:
                draw.line([(x0, y0), (x1, y1)], fill=cor, width=int(1*supersample*zoom_level))
            if mostrar_distancias:
                dist = self.graph_manager.calcular_distancia(
                    self.graph_manager.grafo.nodes[u]['y'], self.graph_manager.grafo.nodes[u]['x'],
                    self.graph_manager.grafo.nodes[v]['y'], self.graph_manager.grafo.nodes[v]['x']
                )
                txt = f"{dist:.0f}m"
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        if mostrar_pontos:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                r = int(3 * supersample * min(zoom_level, 2.0))
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(245,245,245,200), outline='#CACACC', width=int(1*supersample*min(zoom_level, 2.0)))
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = int(6 * supersample * min(zoom_level, 2.0))
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))

    def desenhar_grafo_manual(self, draw, w, h, supersample, zoom_level, pan_x, pan_y, mostrar_distancias, cores_personalizadas, caminho, origem, destino, mostrar_pontos, modo_edicao, vertice_selecionado, font):
        min_x, min_y, max_x, max_y = self.graph_manager.bbox or (0, 0, 900, 650)
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / zoom_level
        range_y = (max_y - min_y) / zoom_level
        zoomed_min_x = center_x - range_x / 2 + pan_x
        zoomed_max_x = center_x + range_x / 2 + pan_x
        zoomed_min_y = center_y - range_y / 2 + pan_y
        zoomed_max_y = center_y + range_y / 2 + pan_y
        def geo_to_canvas(x, y):
            x_range = zoomed_max_x - zoomed_min_x
            y_range = zoomed_max_y - zoomed_min_y
            if x_range == 0: x_range = 1
            if y_range == 0: y_range = 1
            cx = int((x - zoomed_min_x) / x_range * (w - 40) + 20)
            cy = int((zoomed_max_y - y) / y_range * (h - 40) + 20)
            return cx * supersample, cy * supersample
        for u, v, data in self.graph_manager.grafo.edges(data=True):
            x0, y0 = geo_to_canvas(self.graph_manager.grafo.nodes[u]['x'], self.graph_manager.grafo.nodes[u]['y'])
            x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[v]['x'], self.graph_manager.grafo.nodes[v]['y'])
            oneway = data.get('oneway', False)
            cor = '#2196f3' if (cores_personalizadas and oneway) else '#ff9800' if cores_personalizadas else '#77787C'
            draw.line([(x0, y0), (x1, y1)], fill=cor, width=int(1*supersample*zoom_level))
            if mostrar_distancias or modo_edicao:
                peso = data.get('weight', 0)
                mx = (x0 + x1) // 2
                my = (y0 + y1) // 2
                txt = f"{peso:.0f}m"
                draw.text((mx, my), txt, fill="#bbbbbb", font=font, anchor="mm")
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        if mostrar_pontos or modo_edicao:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                cor_vertice = (245,245,245,200)
                r = int(3 * supersample * min(zoom_level, 2.0))
                outline_width = int(1 * supersample * min(zoom_level, 2.0))
                outline_color = '#CACACC'
                if node == vertice_selecionado:
                    cor_vertice = (255,255,0,255)
                    r = int(4 * supersample * min(zoom_level, 2.0))
                elif modo_edicao:
                    r = int(4 * supersample * min(zoom_level, 2.0))
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor_vertice, outline=outline_color, width=outline_width)
                if modo_edicao:
                    draw.text((x, y-int(15*supersample*min(zoom_level, 2.0))), str(node), fill="#ffffff", font=font, anchor="mm")
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = int(6 * supersample * min(zoom_level, 2.0))
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))

    def encontrar_vertice_proximo(self, event_x, event_y, raio=8):
        min_dist = float('inf')
        closest_node = None
        for node, (x, y) in self.node_canvas_map.items():
            dist = ((event_x - x)**2 + (event_y - y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        return closest_node if min_dist < raio else None

    def distancia_ponto_linha(self, px, py, x1, y1, x2, y2):
        numerador = abs((y2-y1)*px - (x2-x1)*py + x2*y1 - y2*x1)
        denominador = sqrt((y2-y1)**2 + (x2-x1)**2)
        return numerador/denominador if denominador != 0 else float('inf')

    def desenhar_canvas_vazio(self):
        w, h = self.obter_dimensoes_canvas()
        supersample = 4
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        self.desenhar_grid_fundo(draw, w, h, supersample)
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk