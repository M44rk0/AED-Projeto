import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import osmnx as ox
from math import radians, sin, cos, sqrt, atan2
from core.Dijkstra import Dijkstra
from PIL import ImageGrab, Image, ImageDraw, ImageTk, ImageFont
import io
import networkx as nx
import os
from datetime import datetime
import random
import platform
import subprocess

# Imports dos módulos separados
from core.GraphManager import GraphManager
from core.GraphDrawer import GraphDrawer
from managers.HistoryManager import HistoryManager
from ui.ZoomPanTool import ZoomPanTool
from ui.Sidebar import Sidebar
from ui.ActionPanel import ActionPanel
from ui.ZoomPanel import ZoomPanel
from ui.HistoryPanel import HistoryPanel
from ui.TooltipManager import TooltipManager
from core.SelectionManager import SelectionManager
from managers.ImageManager import ImageManager
from ui.EventManager import EventManager
from core.GraphOperations import GraphOperations
from ui.ViewManager import ViewManager
from ui.ToggleManager import ToggleManager
from ui.UIManager import UIManager

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
        self.zoom_pan_tool = ZoomPanTool()
        self.selection_manager = SelectionManager()
        
        # Variáveis de estado
        self.cores_personalizadas = False
        self.mostrar_distancias = False
        self.modo_edicao = False
        
        # Configurar interface
        self.criar_widgets()
        
        # Inicializar gerenciadores modulares
        self.event_manager = EventManager(self)
        self.graph_operations = GraphOperations(self)
        self.view_manager = ViewManager(self)
        self.toggle_manager = ToggleManager(self)
        self.ui_manager = UIManager(self)
        
        # Configurar estado inicial
        self.ui_manager.atualizar_estado_botoes()
        
        # Desenhar grafo inicial (grid)
        self.view_manager.desenhar_grafo()
    
    def criar_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self, bg="#1a1b1e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de conteúdo
        content_frame = tk.Frame(main_frame, bg="#1a1b1e")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar painéis modulares na ordem correta
        self.sidebar = Sidebar(content_frame, self)
        
        # Frame central
        center_panel = tk.Frame(content_frame, bg="#1a1b1e")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas principal
        self.canvas = tk.Canvas(center_panel, bg="#2a2b2e", 
                              highlightthickness=3, highlightbackground="#3a3b3e",
                              bd=0, relief='flat')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Criar os outros painéis modulares
        self.action_panel = ActionPanel(center_panel, self)
        self.zoom_panel = ZoomPanel(self.canvas, self)
        self.history_panel = HistoryPanel(content_frame, self)
        self.tooltip_manager = TooltipManager(self.canvas)
        self.image_manager = ImageManager(self)
        
        # Configurar referências cruzadas
        self.image_manager.set_zoom_overlay(self.zoom_panel.overlay)
        self.history_manager = HistoryManager(self.history_panel.canvas, self.history_panel.cards_frame)
        
        # Inicializar GraphDrawer
        self.graph_drawer = GraphDrawer(self.canvas, self.graph_manager)
    

    # === ViewManager ===
    def desenhar_grafo(self):
        self.view_manager.desenhar_grafo()
    
    def desenhar_grafo_com_zoom_fluido(self):
        self.view_manager.desenhar_grafo_com_zoom_fluido()
    
    def zoom_in(self):
        self.view_manager.zoom_in()
    
    def zoom_out(self):
        self.view_manager.zoom_out()
    
    def zoom_reset(self):
        self.view_manager.zoom_reset()
    
    def atualizar_texto_zoom(self):
        self.view_manager.atualizar_texto_zoom()
    
    # === GraphOperations ===
    def importar_osm(self):
        self.graph_operations.importar_osm()
    
    def toggle_modo_edicao(self):
        self.graph_operations.toggle_modo_edicao()
    
    def gerar_vertices_aleatorios(self):
        self.graph_operations.gerar_vertices_aleatorios()
    
    def gerar_arestas_aleatorias(self):
        self.graph_operations.gerar_arestas_aleatorias()
    
    def apagar_grafo(self):
        self.graph_operations.apagar_grafo()
    
    def calcular_rota(self):
        self.graph_operations.calcular_rota()
    
    # === ToggleManager ===
    def limpar_selecao(self):
        self.toggle_manager.limpar_selecao()
    
    def toggle_pontos(self):
        self.toggle_manager.toggle_pontos()
    
    def toggle_distancias(self):
        self.toggle_manager.toggle_distancias()
    
    def toggle_cores_ruas(self):
        self.toggle_manager.toggle_cores_ruas()
    
    # === UIManager ===
    def mostrar_botoes_centrais(self):
        self.ui_manager.mostrar_botoes_centrais()
    
    def ocultar_botoes_centrais(self):
        self.ui_manager.ocultar_botoes_centrais()
    
    def atualizar_estado_botoes(self):
        self.ui_manager.atualizar_estado_botoes()
    
    # === ImageManager ===
    def copiar_imagem_canvas(self):
        self.image_manager.copiar_imagem()
    
    def salvar_imagem_canvas(self):
        resultado = self.image_manager.salvar_imagem()
        if resultado:
            self.history_manager.adicionar_captura(resultado)
            messagebox.showinfo("Imagem salva", f"Imagem salva com sucesso!\n\nCaminho: {resultado['caminho']}")
    
    # === HistoryManager ===
    def refazer_rota(self, info):
        caminho_salvo = info.get('caminho', None)
        if not caminho_salvo or not all(n in self.graph_manager.grafo.nodes for n in caminho_salvo):
            messagebox.showwarning("Aviso", "Não é possível redesenhar esta rota: o grafo foi alterado ou nós não existem mais.")
            return
        self.selection_manager.origem = info['origem']
        self.selection_manager.destino = info['destino']
        self.selection_manager.caminho = caminho_salvo.copy()
        self.selection_manager.mostrar_pontos = False
        self.action_panel.configurar_texto_pontos(False)
        self.view_manager.desenhar_grafo()

if __name__ == '__main__':
    app = MapaTkinter()
    app.history_manager.refazer_rota_callback = app.refazer_rota
    app.mainloop()

