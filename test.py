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
import random

# ================================================
# Classe GraphManager - Gerencia operações do grafo
# ================================================
class GraphManager:
    def __init__(self):
        self.grafo = None
        self.bbox = None
        self.contador_vertices = 0
        self.reset_contador()
    
    def reset_contador(self):
        self.contador_vertices = 1
    
    def importar_osm(self, caminho):
        try:
            self.grafo = ox.graph_from_xml(caminho)
            return True
        except Exception as e:
            return str(e)
    
    def criar_grafo_vazio(self):
        self.grafo = nx.Graph()
        self.bbox = (0, 0, 900, 650)
        return True
    
    def existe_grafo(self):
        return self.grafo is not None and len(self.grafo.nodes) > 0
    
    def eh_grafo_osm(self):
        if not self.existe_grafo():
            return False
            
        for _, data in self.grafo.nodes(data=True):
            if 'osmid' in data:
                return True
                
        for _, _, data in self.grafo.edges(data=True):
            if 'highway' in data or 'osmid' in data or 'geometry' in data:
                return True
        return False
    
    def obter_proximo_id_vertice(self):
        if not self.grafo or not self.grafo.nodes():
            return 1
            
        ids_utilizados = set(self.grafo.nodes())
        proximo_id = 1
        while proximo_id in ids_utilizados:
            proximo_id += 1
        return proximo_id
    
    def recalcular_contador(self):
        if self.grafo and self.grafo.nodes():
            self.contador_vertices = max(self.grafo.nodes()) + 1
        else:
            self.contador_vertices = 1
    
    def adicionar_vertice(self, x, y):
        novo_id = self.obter_proximo_id_vertice()
        self.grafo.add_node(novo_id, x=x, y=y)
        return novo_id
    
    def adicionar_aresta(self, u, v, peso):
        self.grafo.add_edge(u, v, weight=peso)
        return True
    
    def remover_vertice(self, node):
        self.grafo.remove_node(node)
        self.recalcular_contador()
        return True
    
    def remover_aresta(self, u, v):
        self.grafo.remove_edge(u, v)
        return True
    
    def gerar_vertices_aleatorios(self, quantidade):
        if not self.existe_grafo():
            self.criar_grafo_vazio()
            
        for _ in range(quantidade):
            x = random.uniform(50, 850)
            y = random.uniform(50, 600)
            novo_id = self.obter_proximo_id_vertice()
            self.grafo.add_node(novo_id, x=x, y=y)
        return True
    
    def gerar_arestas_aleatorias(self):
        if not self.existe_grafo() or len(self.grafo.nodes()) < 2:
            return False
            
        self.grafo.remove_edges_from(list(self.grafo.edges()))
        vertices = list(self.grafo.nodes())
        
        # Árvore geradora mínima
        vertices_conectados = {vertices[0]}
        vertices_restantes = set(vertices[1:])
        
        while vertices_restantes:
            v1 = random.choice(list(vertices_conectados))
            v2 = random.choice(list(vertices_restantes))
            peso = random.randint(10, 100)
            self.grafo.add_edge(v1, v2, weight=peso)
            vertices_conectados.add(v2)
            vertices_restantes.remove(v2)
        
        # Arestas extras
        num_arestas_extras = len(vertices) * 2
        for _ in range(num_arestas_extras):
            v1 = random.choice(vertices)
            v2 = random.choice(vertices)
            if v1 != v2 and not self.grafo.has_edge(v1, v2):
                peso = random.randint(10, 100)
                self.grafo.add_edge(v1, v2, weight=peso)
        return True
    
    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        R = 6371000
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def calcular_rota(self, origem, destino):
        if not self.existe_grafo():
            return None, "Grafo não existe!"
            
        grafo_dijkstra = {}
        for u, v, data in self.grafo.edges(data=True):
            if u not in grafo_dijkstra:
                grafo_dijkstra[u] = {}
            if v not in grafo_dijkstra:
                grafo_dijkstra[v] = {}
            
            peso = data.get('weight', None)
            if peso is None:
                peso = self.calcular_distancia(
                    self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'],
                    self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x']
                )
            
            grafo_dijkstra[u][v] = peso
            grafo_dijkstra[v][u] = peso
        
        try:
            dijkstra = Dijkstra(grafo_dijkstra)
            caminho, dist = dijkstra.encontrar_caminho(origem, destino)
            stats = dijkstra.get_estatisticas()
            return {
                'caminho': caminho,
                'distancia': dist,
                'tempo': stats['tempo'],
                'nos_explorados': stats['nos_explorados']
            }
        except Exception as e:
            return None, str(e)
    
    def limpar_grafo(self):
        self.grafo = None
        self.bbox = None
        self.reset_contador()

# ================================================
# Classe GraphDrawer - Responsável pelo desenho do grafo
# ================================================
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
        """Obtém o valor de supersample baseado no zoom"""
        return 2 if zoom_level > 2.0 else 4
    
    def obter_tamanho_fonte(self, supersample, zoom_level):
        """Calcula o tamanho da fonte baseado no zoom"""
        return int(5 * supersample * min(zoom_level, 2.0))
    
    def obter_tamanho_vertice(self, supersample, zoom_level, multiplicador=1):
        """Calcula o tamanho do vértice baseado no zoom"""
        return int(3 * supersample * min(zoom_level, 2.0) * multiplicador)
    
    def obter_tamanho_marcador(self, supersample, zoom_level):
        """Calcula o tamanho do marcador baseado no zoom"""
        return int(6 * supersample * min(zoom_level, 2.0))
    
    def desenhar_grid_fundo(self, draw, w, h, supersample):
        grid_color = '#151618'
        cell_size = self.grid_cell_size * supersample
        
        for x in range(0, w * supersample, cell_size):
            draw.line([(x, 0), (x, h * supersample)], fill=grid_color, width=1)
        
        for y in range(0, h * supersample, cell_size):
            draw.line([(0, y), (w * supersample, y)], fill=grid_color, width=1)
    
    def tem_zoom_ativo(self, zoom_level, pan_x, pan_y):
        """Verifica se há zoom ou pan ativo"""
        return zoom_level != 1.0 or pan_x != 0 or pan_y != 0
    
    def desenhar_grafo_apropriado(self, zoom_level=1.0, pan_x=0, pan_y=0, 
                                mostrar_distancias=False, cores_personalizadas=False,
                                caminho=None, origem=None, destino=None,
                                mostrar_pontos=True, modo_edicao=False, vertice_selecionado=None):
        """Escolhe entre versão otimizada ou normal baseado no zoom"""
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
        """Versão otimizada do desenho para zoom fluido"""
        if not self.graph_manager.existe_grafo():
            self.desenhar_canvas_vazio()
            return
        
        # Detectar se é um grafo OSM
        if self.graph_manager.eh_grafo_osm():
            return self.desenhar_grafo_osm_otimizado(zoom_level, pan_x, pan_y, 
                                                   mostrar_distancias, cores_personalizadas,
                                                   caminho, origem, destino, mostrar_pontos)
        else:
            return self.desenhar_grafo_manual_otimizado(zoom_level, pan_x, pan_y, 
                                                      mostrar_distancias, cores_personalizadas,
                                                      caminho, origem, destino, mostrar_pontos, 
                                                      modo_edicao, vertice_selecionado)
    
    def desenhar_grafo_osm_otimizado(self, zoom_level, pan_x, pan_y, 
                                   mostrar_distancias, cores_personalizadas,
                                   caminho, origem, destino, mostrar_pontos):
        """Versão otimizada para grafos OSM"""
        supersample = self.obter_supersample(zoom_level)
        w, h = self.obter_dimensoes_canvas()
        
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Desenhar grid de fundo primeiro
        self.desenhar_grid_fundo(draw, w, h, supersample)
        
        try:
            font_size = self.obter_tamanho_fonte(supersample, zoom_level)
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        
        # Obter bbox e calcular zoom
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
        
        # 1. Desenhar arestas
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
                
        # 2. Desenhar caminho
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
                
        # 3. Desenhar vértices
        if mostrar_pontos:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                r = self.obter_tamanho_vertice(supersample, zoom_level)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(245,245,245,200), outline='#CACACC', width=int(1*supersample*min(zoom_level, 2.0)))
                
        # 4. Desenhar marcadores
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = self.obter_tamanho_marcador(supersample, zoom_level)
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))
                    
        # Finalizar desenho
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk
    
    def desenhar_grafo_manual_otimizado(self, zoom_level, pan_x, pan_y, 
                                      mostrar_distancias, cores_personalizadas,
                                      caminho, origem, destino, mostrar_pontos, 
                                      modo_edicao, vertice_selecionado):
        """Versão otimizada para grafos manuais"""
        supersample = self.obter_supersample(zoom_level)
        w, h = self.obter_dimensoes_canvas()
        
        W, H = w * supersample, h * supersample
        img = Image.new('RGB', (W, H), color='#2a2b2e')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Desenhar grid de fundo primeiro
        self.desenhar_grid_fundo(draw, w, h, supersample)
        
        try:
            font_size = self.obter_tamanho_fonte(supersample, zoom_level)
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
        
        self.node_canvas_map = {}
        self.edge_canvas_map = {}
        
        # Obter bbox e calcular zoom
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
        
        # 1. Desenhar arestas
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
                
        # 2. Desenhar caminho
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
                
        # 3. Desenhar vértices
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
                
        # 4. Desenhar marcadores
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = self.obter_tamanho_marcador(supersample, zoom_level)
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))
                
        # Finalizar desenho
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk
    
    def desenhar_grafo(self, zoom_level=1.0, pan_x=0, pan_y=0, 
                      mostrar_distancias=False, cores_personalizadas=False,
                      caminho=None, origem=None, destino=None,
                      mostrar_pontos=True, modo_edicao=False, vertice_selecionado=None):
        if not self.graph_manager.existe_grafo():
            self.desenhar_canvas_vazio()
            return
        
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
            self.desenhar_grafo_osm(draw, w, h, supersample, zoom_level, pan_x, pan_y, 
                                  mostrar_distancias, cores_personalizadas, 
                                  caminho, origem, destino, mostrar_pontos, font)
        else:
            self.desenhar_grafo_manual(draw, w, h, supersample, zoom_level, pan_x, pan_y, 
                                     mostrar_distancias, cores_personalizadas, 
                                     caminho, origem, destino, mostrar_pontos, 
                                     modo_edicao, vertice_selecionado, font)
        
        img = img.resize((w, h), Image.LANCZOS)
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
        return imgtk
    
    def desenhar_grafo_osm(self, draw, w, h, supersample, zoom_level, pan_x, pan_y,
                         mostrar_distancias, cores_personalizadas, 
                         caminho, origem, destino, mostrar_pontos, font):
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
        
        # Arestas
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
        
        # Caminho
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        
        # Vértices
        if mostrar_pontos:
            for node, data in self.graph_manager.grafo.nodes(data=True):
                x, y = geo_to_canvas(data['x'], data['y'])
                self.node_canvas_map[node] = (x // supersample, y // supersample)
                if node in [origem, destino]:
                    continue
                r = int(3 * supersample * min(zoom_level, 2.0))
                draw.ellipse([x-r, y-r, x+r, y+r], fill=(245,245,245,200), outline='#CACACC', width=int(1*supersample*min(zoom_level, 2.0)))
        
        # Marcadores
        for node, data in self.graph_manager.grafo.nodes(data=True):
            if node in [origem, destino]:
                x, y = geo_to_canvas(data['x'], data['y'])
                r = int(6 * supersample * min(zoom_level, 2.0))
                cor = (0,255,204,255) if node == origem else (255,51,102,255)
                draw.ellipse([x-r, y-r, x+r, y+r], fill=cor, outline=(255,255,255,255), width=int(2*supersample*min(zoom_level, 2.0)))
    
    def desenhar_grafo_manual(self, draw, w, h, supersample, zoom_level, pan_x, pan_y,
                            mostrar_distancias, cores_personalizadas, 
                            caminho, origem, destino, mostrar_pontos, 
                            modo_edicao, vertice_selecionado, font):
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
        
        # Arestas
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
        
        # Caminho
        if caminho:
            for i in range(len(caminho)-1):
                n1, n2 = caminho[i], caminho[i+1]
                x1, y1 = geo_to_canvas(self.graph_manager.grafo.nodes[n1]['x'], self.graph_manager.grafo.nodes[n1]['y'])
                x2, y2 = geo_to_canvas(self.graph_manager.grafo.nodes[n2]['x'], self.graph_manager.grafo.nodes[n2]['y'])
                draw.line([(x1, y1), (x2, y2)], fill='#ff3333', width=int(4*supersample*zoom_level))
        
        # Vértices
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
        
        # Marcadores
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

# ================================================
# Classe HistoryManager - Gerencia histórico de rotas
# ================================================
class HistoryManager:
    def __init__(self, canvas, cards_frame):
        self.historico_canvas = canvas
        self.cards_frame = cards_frame
        self.historico_rotas = []
        self.historico_capturas = []
        
    def adicionar_rota(self, info_rota):
        info_rota['datahora'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.historico_rotas.append(info_rota)
        self.atualizar_historico()
    
    def adicionar_captura(self, info_captura):
        info_captura['datahora'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.historico_capturas.append(info_captura)
        self.atualizar_historico()
    
    def atualizar_historico(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        historico_completo = []
        for info in self.historico_rotas:
            info['tipo'] = 'rota'
            historico_completo.append(info)
        for info in self.historico_capturas:
            info['tipo'] = 'captura'
            historico_completo.append(info)
        
        historico_completo.sort(key=lambda x: datetime.strptime(x['datahora'], '%d/%m/%Y %H:%M:%S'), reverse=True)
        
        for i, info in enumerate(historico_completo, 1):
            card = tk.Frame(self.cards_frame, bg="#262a2f", bd=0, highlightthickness=0)
            card.pack(fill=tk.X, pady=12, padx=0)
            inner = tk.Frame(card, bg="#262a2f")
            inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            
            if info['tipo'] == 'rota':
                tk.Label(inner, text=f"{len(historico_completo)-i+1}.", bg="#262a2f", fg="#00ffcc", 
                       font=("Segoe UI", 11, "bold"), anchor="w", pady=2).pack(fill=tk.X, padx=0, pady=(0,6))
                
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
                    tk.Label(linha, text=label, bg="#262a2f", fg="#bbbbbb", 
                           font=("Segoe UI", 9, "bold"), anchor="w").pack(side=tk.LEFT)
                    tk.Label(linha, text=valor, bg="#262a2f", fg="#ffffff", 
                           font=("Segoe UI", 10), anchor="w").pack(side=tk.LEFT, padx=6)
                
                btn_refazer = tk.Button(inner, text="🔄", bg="#232428", fg="#00ffcc", 
                                     font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2",
                                     command=lambda info=info: self.refazer_rota(info))
                btn_refazer.place(relx=1.0, rely=1.0, anchor='se', x=0, y=-8)
            
            elif info['tipo'] == 'captura':
                tk.Label(inner, text=f"📷 Captura #{len(historico_completo)-i+1}  {info['datahora']}", 
                       bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"), anchor="w").pack(fill=tk.X, padx=0, pady=(0,6))
                
                btn_abrir = tk.Button(inner, text="📂", bg="#232428", fg="#00ffcc", 
                                    font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2",
                                    command=lambda info=info: self.abrir_imagem(info))
                btn_abrir.pack(side=tk.RIGHT, pady=4)
        
        self.historico_canvas.update_idletasks()
        self.historico_canvas.configure(scrollregion=self.historico_canvas.bbox("all"))
    
    def refazer_rota(self, info):
        return info['caminho']
    
    def abrir_imagem(self, info):
        import subprocess
        import platform
        try:
            if platform.system() == "Windows":
                os.startfile(info['caminho'])
            elif platform.system() == "Darwin":
                subprocess.run(["open", info['caminho']])
            else:
                subprocess.run(["xdg-open", info['caminho']])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir imagem:\n{str(e)}")

# ================================================
# Classe ZoomPanTool - Gerencia zoom e pan
# ================================================
class ZoomPanTool:
    def __init__(self):
        self.zoom_level = 1.0
        self.zoom_min = 1.0
        self.zoom_max = 5.0
        self.zoom_step = 0.2
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False
        self.last_pan_x = 0
        self.last_pan_y = 0
    
    def reset_zoom_pan(self):
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.panning = False
    
    def zoom_in(self):
        if self.zoom_level < self.zoom_max:
            self.zoom_level = min(self.zoom_level + self.zoom_step, self.zoom_max)
            return True
        return False
    
    def zoom_out(self):
        if self.zoom_level > self.zoom_min:
            self.zoom_level = max(self.zoom_level - self.zoom_step, self.zoom_min)
            return True
        return False
    
    def on_pan_start(self, event):
        self.panning = True
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        return "fleur"
    
    def on_pan_move(self, event, graph_manager, canvas_width, canvas_height):
        if not self.panning:
            return False
            
        dx = event.x - self.last_pan_x
        dy = event.y - self.last_pan_y
        
        if graph_manager.eh_grafo_osm():
            nodes = list(graph_manager.grafo.nodes(data=True))
            xs = [data['x'] for _, data in nodes]
            ys = [data['y'] for _, data in nodes]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, min_y, max_x, max_y = graph_manager.bbox or (0, 0, 900, 650)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / self.zoom_level
        range_y = (max_y - min_y) / self.zoom_level
        
        world_dx = (dx / (canvas_width - 40)) * range_x
        world_dy = (dy / (canvas_height - 40)) * range_y
        
        self.pan_x -= world_dx
        self.pan_y += world_dy
        self.last_pan_x = event.x
        self.last_pan_y = event.y
        return True
    
    def on_pan_end(self):
        self.panning = False
        return ""
    
    def on_mousewheel_zoom(self, event, graph_manager, canvas_width, canvas_height):
        if graph_manager.eh_grafo_osm():
            nodes = list(graph_manager.grafo.nodes(data=True))
            xs = [data['x'] for _, data in nodes]
            ys = [data['y'] for _, data in nodes]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            min_x, min_y, max_x, max_y = graph_manager.bbox or (0, 0, 900, 650)
        
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        range_x = (max_x - min_x) / self.zoom_level
        range_y = (max_y - min_y) / self.zoom_level
        
        mouse_offset_x = event.x - canvas_width / 2
        mouse_offset_y = event.y - canvas_height / 2
        
        world_offset_x = (mouse_offset_x / (canvas_width - 40)) * range_x
        world_offset_y = (mouse_offset_y / (canvas_height - 40)) * range_y
        
        zoom_in = event.delta > 0
        new_zoom = self.zoom_level + self.zoom_step if zoom_in else self.zoom_level - self.zoom_step
        new_zoom = max(self.zoom_min, min(new_zoom, self.zoom_max))
        
        if new_zoom == self.zoom_level:
            return False
            
        zoom_factor = new_zoom / self.zoom_level
        self.zoom_level = new_zoom
        
        if zoom_in:
            self.pan_x -= world_offset_x * (zoom_factor - 1)
            self.pan_y += world_offset_y * (zoom_factor - 1)
        else:
            self.pan_x += world_offset_x * (1 - zoom_factor)
            self.pan_y -= world_offset_y * (1 - zoom_factor)
            
        return True

# ================================================
# Classe principal MapaTkinter
# ================================================
class MapaTkinter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Navegador OSM")
        self.configure(bg="#1a1b1e")
        self.geometry("1460x720")
        self.resizable(False, False)
        
        # Inicializar gerenciadores
        self.graph_manager = GraphManager()
        self.history_manager = None
        self.zoom_pan_tool = ZoomPanTool()
        
        # Variáveis de estado
        self.cores_personalizadas = False
        self.mostrar_distancias = False
        self.modo_edicao = False
        self.vertice_selecionado = None
        self.criando_aresta = False
        self.origem = None
        self.destino = None
        self.caminho = None
        self.mostrar_pontos = True
        self.selecionando = 'origem'
        
        # Configurar interface
        self.criar_widgets()
        self.criar_bindings()
        self.atualizar_estado_botoes()
        self.zoom_pan_tool.atualizar_texto_zoom = self.atualizar_texto_zoom
        
    def criar_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#1a1b1e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de conteúdo
        content_frame = tk.Frame(main_frame, bg="#1a1b1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de botões à esquerda
        botoes_frame = tk.Frame(content_frame, bg="#232428", width=180)
        botoes_frame.pack(side=tk.LEFT, padx=(0,10), fill=tk.Y)
        botoes_frame.pack_propagate(False)
        
        # Frame central
        center_panel = tk.Frame(content_frame, bg="#1a1b1e")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame de ações
        actions_frame = tk.Frame(center_panel, bg="#1a1b1e")
        actions_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)

        # Canvas principal
        self.canvas = tk.Canvas(center_panel, bg="#2a2b2e", 
                              highlightthickness=3, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configurar estilo dos botões
        self.configurar_estilos()
        
        # Botões
        self.criar_botoes_esquerda(botoes_frame)
        self.criar_botoes_centro(actions_frame)
        self.criar_botoes_zoom()
        
        # Painel de histórico
        self.criar_painel_historico(content_frame)
        
        # Tooltip
        self.tooltip_label = tk.Label(self.canvas, bg="#2a2b2e", fg="#fff", 
                                    font=("Segoe UI", 9), bd=0, relief=tk.FLAT, 
                                    padx=8, pady=4)
        self.tooltip_label.place_forget()
        
        # Inicializar GraphDrawer
        self.graph_drawer = GraphDrawer(self.canvas, self.graph_manager)
    
    def configurar_estilos(self):
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
    
    def criar_botoes_esquerda(self, parent):
        self.btn_importar = tk.Button(parent, text="📂 Importar OSM", 
                                    command=self.importar_osm, **self.btn_style_normal)
        self.btn_importar.pack(fill=tk.X, pady=(10, 5), padx=10)
        
        self.btn_criar_grafo = tk.Button(parent, text="✏️ Criar Grafo", 
                                      command=self.toggle_modo_edicao, **self.btn_style_normal)
        self.btn_criar_grafo.pack(fill=tk.X, pady=5, padx=10)
        
        self.edicao_frame = tk.Frame(parent, bg="#232428")
        
        self.btn_gerar_vertices = tk.Button(self.edicao_frame, text="🎯 Gerar Vértices", 
                                          command=self.gerar_vertices_aleatorios, **self.btn_style_normal)
        self.btn_gerar_vertices.pack(fill=tk.X, pady=(5,5), padx=0)
        
        self.btn_gerar_arestas = tk.Button(self.edicao_frame, text="🎲 Gerar Arestas", 
                                         command=self.gerar_arestas_aleatorias, **self.btn_style_normal)
        self.btn_gerar_arestas.pack(fill=tk.X, pady=(0,5), padx=0)
        
        self.btn_apagar_grafo = tk.Button(parent, text="🗑️ Apagar Grafo", 
                                       command=self.apagar_grafo, **self.btn_style_normal)
        self.btn_apagar_grafo.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_copiar = tk.Button(parent, text="📋 Copiar Imagem", 
                                 command=self.copiar_imagem_canvas, **self.btn_style_normal)
        self.btn_copiar.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_salvar = tk.Button(parent, text="💾 Salvar Imagem", 
                                  command=self.salvar_imagem_canvas, **self.btn_style_normal)
        self.btn_salvar.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_dist = tk.Button(parent, text="Exibir Distâncias", 
                               command=self.toggle_distancias, **self.btn_style_normal)
        self.btn_dist.pack(fill=tk.X, pady=5, padx=10)
        
        self.btn_cores = tk.Button(parent, text="Identificar Ruas", 
                                 command=self.toggle_cores_ruas, **self.btn_style_normal)
        self.btn_cores.pack(fill=tk.X, pady=5, padx=10)
    
    def criar_botoes_centro(self, parent):
        self.btn_limpar = tk.Button(parent, text="Limpar Seleção", 
                                  command=self.limpar_selecao, 
                                  **self.btn_style_normal, width=15, height=1)
        self.btn_limpar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        rota_frame = tk.Frame(parent, bg="#3a3b3e", padx=2.5, pady=2.5)
        rota_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.btn_rota = tk.Button(rota_frame, text="🛣️ Calcular Rota", 
                                command=self.calcular_rota, 
                                **self.btn_style_normal, width=15, height=1)
        self.btn_rota.pack(fill=tk.BOTH, expand=True)
        
        self.btn_pontos = tk.Button(parent, text="Ocultar Vértices", 
                                  command=self.toggle_pontos, 
                                  **self.btn_style_normal, width=15, height=1)
        self.btn_pontos.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
    
    def criar_botoes_zoom(self):
        self.zoom_overlay = tk.Frame(self.canvas, bg=self.canvas['bg'], 
                                   highlightthickness=1, highlightbackground="#3a3b3e",
                                   bd=0, relief='flat')
        self.zoom_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        self.btn_zoom_out = tk.Button(self.zoom_overlay, text="🔍-", 
                                    command=self.zoom_out, 
                                    bg=self.canvas['bg'], fg="#ffffff", 
                                    font=("Segoe UI", 10, "bold"),
                                    bd=0, relief="flat", padx=8, pady=4, 
                                    cursor="hand2", width=4, height=1)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=(0, 2))
        
        self.btn_zoom_reset = tk.Button(self.zoom_overlay, text="🔍", 
                                      command=self.zoom_reset,
                                      bg=self.canvas['bg'], fg="#00ffcc", 
                                      font=("Segoe UI", 10, "bold"),
                                      bd=0, relief="flat", padx=8, pady=4, 
                                      cursor="hand2", width=4, height=1)
        self.btn_zoom_reset.pack(side=tk.LEFT, padx=2)
        
        self.btn_zoom_in = tk.Button(self.zoom_overlay, text="🔍+", 
                                   command=self.zoom_in,
                                   bg=self.canvas['bg'], fg="#ffffff", 
                                   font=("Segoe UI", 10, "bold"),
                                   bd=0, relief="flat", padx=8, pady=4, 
                                   cursor="hand2", width=4, height=1)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=(2, 0))
    
    def criar_painel_historico(self, parent):
        historico_frame = tk.Frame(parent, bg="#232428", width=320)
        historico_frame.pack(side=tk.LEFT, padx=(10,0), fill=tk.Y)
        historico_frame.pack_propagate(False)
        
        self.historico_canvas = tk.Canvas(historico_frame, bg="#232428", highlightthickness=0, bd=0)
        self.historico_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,0), pady=(0,5))
        
        self.historico_scrollbar = tk.Scrollbar(historico_frame, orient="vertical", 
                                             command=self.historico_canvas.yview, bg="#232428")
        self.historico_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historico_canvas.configure(yscrollcommand=self.historico_scrollbar.set)
        
        self.cards_frame = tk.Frame(self.historico_canvas, bg="#232428")
        self.cards_frame_window = self.historico_canvas.create_window((20, 0), window=self.cards_frame, anchor="nw")
        
        self.history_manager = HistoryManager(self.historico_canvas, self.cards_frame)
        
        def ajustar_largura_cards(event):
            canvas_width = event.width
            self.historico_canvas.itemconfig(self.cards_frame_window, width=canvas_width-40)
        self.historico_canvas.bind('<Configure>', ajustar_largura_cards)
        
        def _bind_mousewheel(event):
            self.historico_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.historico_canvas.bind('<Enter>', _bind_mousewheel)
        
        def _unbind_mousewheel(event):
            self.historico_canvas.unbind_all('<MouseWheel>')
        self.historico_canvas.bind('<Leave>', _unbind_mousewheel)
    
    def _on_mousewheel(self, event):
        self.historico_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"
    
    def criar_bindings(self):
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Button-2>", self.on_canvas_click)
        self.canvas.bind("<Button-3>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel_zoom)
        self.canvas.bind("<ButtonPress-2>", self.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_end)
        self.canvas.bind("<Control-ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<Control-B1-Motion>", self.on_pan_move)
        self.canvas.bind("<Control-ButtonRelease-1>", self.on_pan_end)
        self.canvas.bind("<Leave>", self.hide_tooltip)
    
    def desenhar_grafo(self):
        self.imgtk = self.graph_drawer.desenhar_grafo_apropriado(
            zoom_level=self.zoom_pan_tool.zoom_level,
            pan_x=self.zoom_pan_tool.pan_x,
            pan_y=self.zoom_pan_tool.pan_y,
            mostrar_distancias=self.mostrar_distancias,
            cores_personalizadas=self.cores_personalizadas,
            caminho=self.caminho,
            origem=self.origem,
            destino=self.destino,
            mostrar_pontos=self.mostrar_pontos,
            modo_edicao=self.modo_edicao,
            vertice_selecionado=self.vertice_selecionado
        )
    
    # ================================================
    # Métodos de eventos e operações
    # ================================================
    def importar_osm(self):
        caminho = filedialog.askopenfilename(filetypes=[("OSM files", "*.osm"), ("Todos arquivos", "*.*")])
        if caminho:
            resultado = self.graph_manager.importar_osm(caminho)
            if resultado is True:
                self.limpar_selecao()
                self.zoom_pan_tool.reset_zoom_pan()
                self.atualizar_estado_botoes()
                self.desenhar_grafo()
            else:
                messagebox.showerror("Erro", resultado)
    
    def toggle_modo_edicao(self):
        self.modo_edicao = not self.modo_edicao
        if self.modo_edicao:
            self.btn_criar_grafo.configure(**self.btn_style_ativo)
            self.edicao_frame.pack(fill=tk.X, padx=(20, 10), pady=0, before=self.btn_apagar_grafo)
            self.zoom_pan_tool.reset_zoom_pan()
            if not self.graph_manager.existe_grafo():
                self.graph_manager.criar_grafo_vazio()
            self.limpar_selecao()
        else:
            self.btn_criar_grafo.configure(**self.btn_style_normal)
            self.edicao_frame.pack_forget()
            self.vertice_selecionado = None
            self.criando_aresta = False
            if not self.graph_manager.existe_grafo():
                self.graph_manager.limpar_grafo()
                self.zoom_pan_tool.reset_zoom_pan()
        self.atualizar_estado_botoes()
        self.desenhar_grafo()
    
    def gerar_vertices_aleatorios(self):
        quantidade = simpledialog.askinteger("Gerar Vértices", 
                                           "Quantos vértices deseja gerar?",
                                           minvalue=1, maxvalue=10000, initialvalue=10)
        if quantidade:
            self.graph_manager.gerar_vertices_aleatorios(quantidade)
            self.desenhar_grafo()
            self.atualizar_estado_botoes()
    
    def gerar_arestas_aleatorias(self):
        if self.graph_manager.gerar_arestas_aleatorias():
            self.desenhar_grafo()
        else:
            messagebox.showwarning("Aviso", "É necessário ter pelo menos 2 vértices para gerar arestas!")
    
    def apagar_grafo(self):
        self.graph_manager.limpar_grafo()
        self.limpar_selecao()
        self.zoom_pan_tool.reset_zoom_pan()
        self.desenhar_grafo()
        self.atualizar_estado_botoes()
    
    def on_canvas_motion(self, event):
        if self.modo_edicao and self.graph_manager.existe_grafo():
            num_vertices = len(self.graph_manager.grafo.nodes())
            num_arestas = len(self.graph_manager.grafo.edges())
            
            closest_node = self.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
            if closest_node:
                self.show_tooltip(f'Vértice: {closest_node}', event.x_root, event.y_root)
                return
            
            if num_vertices == 0:
                self.show_tooltip('Clique para criar um vértice', event.x_root, event.y_root)
            elif num_vertices == 1:
                self.show_tooltip('Clique para adicionar outro vértice', event.x_root, event.y_root)
            elif num_vertices >= 2 and num_arestas == 0:
                self.show_tooltip('Clique em um vértice, depois em outro para criar uma aresta', event.x_root, event.y_root)
            else:
                self.hide_tooltip()
            return
        
        if self.graph_manager.existe_grafo():
            closest_node = self.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
            if closest_node:
                self.show_tooltip(f'Vértice: {closest_node}', event.x_root, event.y_root)
            else:
                self.hide_tooltip()
        else:
            self.hide_tooltip()
    
    def on_canvas_click(self, event):
        if self.zoom_pan_tool.panning:
            return
            
        if not self.graph_manager.existe_grafo():
            if self.modo_edicao:
                self.graph_manager.criar_grafo_vazio()
                self.zoom_pan_tool.reset_zoom_pan()
            else:
                return

        if self.modo_edicao:
            closest_node = self.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
            if event.num == 1:  # Clique esquerdo
                if closest_node:
                    if not self.vertice_selecionado:
                        self.vertice_selecionado = closest_node
                        self.criando_aresta = True
                    else:
                        if closest_node != self.vertice_selecionado:
                            peso = simpledialog.askfloat("Peso da Aresta", 
                                                      "Digite o peso (distância) da aresta:",
                                                      minvalue=0.0)
                            if peso is not None:
                                self.graph_manager.adicionar_aresta(self.vertice_selecionado, closest_node, peso)
                        self.vertice_selecionado = None
                        self.criando_aresta = False
                else:
                    min_x, min_y, max_x, max_y = self.graph_manager.bbox or (0, 0, 900, 650)
                    x_geo = min_x + (event.x / self.canvas.winfo_width()) * (max_x - min_x)
                    y_geo = max_y - (event.y / self.canvas.winfo_height()) * (max_y - min_y)
                    self.graph_manager.adicionar_vertice(x_geo, y_geo)
            elif event.num in [2, 3]:  # Clique direito
                if closest_node:
                    self.graph_manager.remover_vertice(closest_node)
                else:
                    for u, v, data in self.graph_manager.grafo.edges(data=True):
                        x0, y0 = self.graph_drawer.node_canvas_map[u]
                        x1, y1 = self.graph_drawer.node_canvas_map[v]
                        dist = self.graph_drawer.distancia_ponto_linha(event.x, event.y, x0, y0, x1, y1)
                        if dist < 5:
                            self.graph_manager.remover_aresta(u, v)
                            break
            self.desenhar_grafo()
        else:
            closest_node = self.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
            if closest_node:
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
        if not self.graph_manager.existe_grafo() or not self.origem or not self.destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
            
        resultado = self.graph_manager.calcular_rota(self.origem, self.destino)
        if resultado and isinstance(resultado, dict):
            self.caminho = resultado['caminho']
            self.mostrar_pontos = False
            self.btn_pontos.config(text="Mostrar Vértices")
            self.desenhar_grafo()
            
            info_rota = {
                'origem': self.origem,
                'destino': self.destino,
                'distancia': resultado['distancia'],
                'tempo': resultado['tempo'],
                'nos_explorados': resultado['nos_explorados'],
                'caminho': self.caminho.copy()
            }
            self.history_manager.adicionar_rota(info_rota)
        else:
            messagebox.showwarning("Sem caminho", "Não existe caminho entre os pontos selecionados!")
    
    def limpar_selecao(self):
        self.origem = None
        self.destino = None
        self.caminho = None
        self.vertice_selecionado = None
        self.criando_aresta = False
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
        if self.zoom_overlay.winfo_viewable():
            self.zoom_overlay.place_forget()
        
        self.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        bbox = (x, y, x + w, y + h)
        img = ImageGrab.grab(bbox)
        
        if self.zoom_overlay.winfo_exists():
            self.zoom_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        output = io.BytesIO()
        img.convert('RGB').save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()
        
        try:
            self.clipboard_clear()
            self.update()
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
        if self.zoom_overlay.winfo_viewable():
            self.zoom_overlay.place_forget()
        
        self.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        bbox = (x, y, x + w, y + h)
        img = ImageGrab.grab(bbox)
        
        if self.zoom_overlay.winfo_exists():
            self.zoom_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        capturas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas")
        if not os.path.exists(capturas_dir):
            os.makedirs(capturas_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"grafo_{timestamp}.png"
        caminho_arquivo = os.path.join(capturas_dir, nome_arquivo)
        
        try:
            img.save(caminho_arquivo)
            self.history_manager.adicionar_captura({
                'caminho': caminho_arquivo,
                'nome': nome_arquivo
            })
            messagebox.showinfo("Imagem salva", f"Imagem salva com sucesso!\n\nCaminho: {caminho_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar imagem:\n{str(e)}")
    
    def on_pan_start(self, event):
        if self.modo_edicao or not self.graph_manager.existe_grafo():
            return
        cursor = self.zoom_pan_tool.on_pan_start(event)
        self.canvas.config(cursor=cursor)
    
    def on_pan_move(self, event):
        if self.modo_edicao or not self.graph_manager.existe_grafo():
            return
        w, h = self.graph_drawer.obter_dimensoes_canvas()
        if self.zoom_pan_tool.on_pan_move(event, self.graph_manager, w, h):
            self.desenhar_grafo()
    
    def on_pan_end(self, event):
        cursor = self.zoom_pan_tool.on_pan_end()
        self.canvas.config(cursor=cursor)
    
    def on_mousewheel_zoom(self, event):
        if self.modo_edicao or not self.graph_manager.existe_grafo():
            return
        w, h = self.graph_drawer.obter_dimensoes_canvas()
        if self.zoom_pan_tool.on_mousewheel_zoom(event, self.graph_manager, w, h):
            self.atualizar_texto_zoom()
            self.desenhar_grafo()
    
    def zoom_in(self):
        if self.modo_edicao:
            return
        if self.zoom_pan_tool.zoom_in():
            self.atualizar_texto_zoom()
            self.desenhar_grafo()
    
    def zoom_out(self):
        if self.modo_edicao:
            return
        if self.zoom_pan_tool.zoom_out():
            self.atualizar_texto_zoom()
            self.desenhar_grafo()
    
    def zoom_reset(self):
        if self.modo_edicao:
            return
        self.zoom_pan_tool.reset_zoom_pan()
        self.atualizar_texto_zoom()
        self.desenhar_grafo()
    
    def atualizar_texto_zoom(self):
        zoom_percent = int(self.zoom_pan_tool.zoom_level * 100)
        self.btn_zoom_reset.config(text=f"{zoom_percent}%")
    
    def show_tooltip(self, text, x, y):
        canvas_x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        
        is_contextual_tip = (self.modo_edicao and 
                           (text.startswith('Clique para criar') or 
                            text.startswith('Clique para adicionar') or 
                            text.startswith('Clique em um vértice')))
        
        if is_contextual_tip:
            self.tooltip_label.config(
                text=text,
                bg="#ffffcc",
                fg="#000000",
                font=("Segoe UI", 8),
                bd=1,
                relief=tk.SOLID
            )
        else:
            self.tooltip_label.config(
                text=text,
                bg="#2a2b2e",
                fg="#fff",
                font=("Segoe UI", 9),
                bd=0,
                relief=tk.FLAT
            )
        self.tooltip_label.place(x=canvas_x+10, y=canvas_y+10)
    
    def hide_tooltip(self, event=None):
        self.tooltip_label.place_forget()
    
    def atualizar_estado_botoes(self):
        grafo_osm = self.graph_manager.eh_grafo_osm() if self.graph_manager.existe_grafo() else False
        tem_grafo_valido = self.graph_manager.existe_grafo()
        tem_vertices = self.graph_manager.existe_grafo() and len(self.graph_manager.grafo.nodes) > 0
        
        if self.modo_edicao:
            self.btn_apagar_grafo.config(state=tk.NORMAL)
            self.habilitar_botoes_principais(False)
            self.habilitar_botoes_zoom(False)
            self.zoom_overlay.place_forget()
            self.btn_criar_grafo.config(state=tk.DISABLED if grafo_osm else tk.NORMAL)
            self.habilitar_botoes_edicao(not grafo_osm)
        else:
            self.btn_apagar_grafo.config(state=tk.NORMAL if tem_vertices else tk.DISABLED)
            
            if tem_grafo_valido:
                self.habilitar_botoes_principais(True)
                self.habilitar_botoes_zoom(True)
                self.zoom_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
            else:
                self.habilitar_botoes_zoom(False)
                self.zoom_overlay.place_forget()
                self.btn_copiar.config(state=tk.DISABLED)
                self.btn_salvar.config(state=tk.DISABLED)
                self.btn_dist.config(state=tk.DISABLED)
                self.btn_cores.config(state=tk.DISABLED)
                self.btn_limpar.config(state=tk.DISABLED)
                self.btn_rota.config(state=tk.DISABLED)
                self.btn_pontos.config(state=tk.DISABLED)
            
            self.btn_criar_grafo.config(state=tk.DISABLED if grafo_osm else tk.NORMAL)
    
    def habilitar_botoes_principais(self, habilitar=True):
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.btn_importar.config(state=estado)
        self.btn_rota.config(state=estado)
        self.btn_limpar.config(state=estado)
        self.btn_pontos.config(state=estado)
        self.btn_copiar.config(state=estado)
        self.btn_salvar.config(state=estado)
        self.btn_dist.config(state=estado)
        self.btn_cores.config(state=estado)
    
    def habilitar_botoes_zoom(self, habilitar=True):
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.btn_zoom_in.config(state=estado)
        self.btn_zoom_out.config(state=estado)
        self.btn_zoom_reset.config(state=estado)
    
    def habilitar_botoes_edicao(self, habilitar=True):
        estado = tk.NORMAL if habilitar else tk.DISABLED
        self.btn_gerar_vertices.config(state=estado)
        self.btn_gerar_arestas.config(state=estado)
    
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

if __name__ == '__main__':
    app = MapaTkinter()
    app.mainloop()