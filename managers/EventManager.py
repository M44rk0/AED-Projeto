from tkinter import simpledialog, messagebox

class EventManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.canvas = main_app.canvas
        self.criar_bindings()
    
    def criar_bindings(self):
        #Configura todos os bindings de eventos do canvas
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
    
    def on_canvas_motion(self, event):
        #Gerencia movimento do mouse no canvas
        if self.main_app.modo_edicao:
            # No modo de edição, sempre mostrar dicas contextuais
            if self.main_app.graph_manager.existe_grafo():
                num_vertices = len(self.main_app.graph_manager.grafo.nodes())
                num_arestas = len(self.main_app.graph_manager.grafo.edges())
                
                closest_node = self.main_app.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
                if closest_node:
                    self.main_app.tooltip_manager.show_tooltip(f'Vértice: {closest_node}', event.x_root, event.y_root)
                    return
                
                if num_vertices == 0:
                    self.main_app.tooltip_manager.show_tooltip('Clique para criar um vértice', event.x_root, event.y_root, True)
                elif num_vertices == 1:
                    self.main_app.tooltip_manager.show_tooltip('Clique para adicionar outro vértice', event.x_root, event.y_root, True)
                elif num_vertices >= 2 and num_arestas == 0:
                    self.main_app.tooltip_manager.show_tooltip('Clique em um vértice, depois em outro para criar uma aresta', event.x_root, event.y_root, True)
                else:
                    self.main_app.tooltip_manager.hide_tooltip()
            else:
                # Se não há grafo no modo de edição, mostrar dica para criar o primeiro vértice
                self.main_app.tooltip_manager.show_tooltip('Clique para criar um vértice', event.x_root, event.y_root, True)
            return
        
        # Quando não está no modo de edição (modo de navegação)
        if self.main_app.graph_manager.existe_grafo():
            closest_node = self.main_app.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
            if closest_node:
                # Se há um vértice próximo, mostrar informações do vértice
                self.main_app.tooltip_manager.show_tooltip(f'Vértice: {closest_node}', event.x_root, event.y_root)
            else:
                # Se não há vértice próximo, mostrar dicas contextuais apenas se ainda não foram mostradas
                if not self.main_app.selection_manager.tooltips_ajuda_mostrados:
                    if not self.main_app.selection_manager.origem:
                        self.main_app.tooltip_manager.show_tooltip('Selecione o vértice de início', event.x_root, event.y_root, True)
                    elif not self.main_app.selection_manager.destino:
                        self.main_app.tooltip_manager.show_tooltip('Selecione o vértice de destino', event.x_root, event.y_root, True)
                    else:
                        # Ambos origem e destino já foram selecionados
                        self.main_app.tooltip_manager.show_tooltip('Clique no botão "Calcular Rota"', event.x_root, event.y_root, True)
                else:
                    self.main_app.tooltip_manager.hide_tooltip()
        else:
            self.main_app.tooltip_manager.hide_tooltip()
    
    def on_canvas_click(self, event):
        #Gerencia cliques no canvas
        if self.main_app.zoom_pan_tool.panning:
            return
            
        if not self.main_app.graph_manager.existe_grafo():
            if self.main_app.modo_edicao:
                self.main_app.graph_manager.criar_grafo_vazio()
                self.main_app.zoom_pan_tool.reset_zoom_pan()
            else:
                return

        if self.main_app.modo_edicao:
            self._processar_clique_edicao(event)
        else:
            self._processar_clique_selecao(event)
    
    def _processar_clique_edicao(self, event):
        #Processa cliques no modo de edição
        closest_node = self.main_app.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
        if event.num == 1:  # Clique esquerdo
            if closest_node:
                if not self.main_app.selection_manager.vertice_selecionado:
                    self.main_app.selection_manager.vertice_selecionado = closest_node
                    self.main_app.selection_manager.criando_aresta = True
                else:
                    if closest_node != self.main_app.selection_manager.vertice_selecionado:
                        # Usar uma abordagem mais robusta para obter o peso
                        peso_valido = False
                        peso = 0.0
                        
                        while not peso_valido:
                            try:
                                peso_input = simpledialog.askstring("Peso da Aresta", 
                                                                  "Digite o peso (distância) da aresta:\n(Deixe vazio para usar 0):")
                                
                                # Se o usuário cancelou, sair do loop
                                if peso_input is None:
                                    break
                                
                                # Se o campo está vazio, usar 0
                                if peso_input.strip() == "":
                                    peso = 0.0
                                    peso_valido = True
                                else:
                                    # Tentar converter para float
                                    peso = float(peso_input)
                                    if peso < 0:
                                        messagebox.showerror("Erro", "O peso deve ser um número não negativo!")
                                        continue
                                    peso_valido = True
                                    
                            except ValueError:
                                messagebox.showerror("Erro", "Por favor, digite um número válido!")
                                continue
                        
                        # Se chegou até aqui, criar a aresta
                        if peso_valido:
                            self.main_app.graph_manager.adicionar_aresta(self.main_app.selection_manager.vertice_selecionado, closest_node, peso)
                    
                    self.main_app.selection_manager.vertice_selecionado = None
                    self.main_app.selection_manager.criando_aresta = False
            else:
                min_x, min_y, max_x, max_y = self.main_app.graph_manager.bbox or (0, 0, 900, 650)
                x_geo = min_x + (event.x / self.canvas.winfo_width()) * (max_x - min_x)
                y_geo = max_y - (event.y / self.canvas.winfo_height()) * (max_y - min_y)
                self.main_app.graph_manager.adicionar_vertice(x_geo, y_geo)
        elif event.num in [2, 3]:  # Clique direito
            if closest_node:
                self.main_app.graph_manager.remover_vertice(closest_node)
            else:
                for u, v, data in self.main_app.graph_manager.grafo.edges(data=True):
                    x0, y0 = self.main_app.graph_drawer.node_canvas_map[u]
                    x1, y1 = self.main_app.graph_drawer.node_canvas_map[v]
                    dist = self.main_app.graph_drawer.distancia_ponto_linha(event.x, event.y, x0, y0, x1, y1)
                    if dist < 5:
                        self.main_app.graph_manager.remover_aresta(u, v)
                        break
        self.main_app.view_manager.desenhar_grafo()
    
    def _processar_clique_selecao(self, event):
        #Processa cliques no modo de seleção
        closest_node = self.main_app.graph_drawer.encontrar_vertice_proximo(event.x, event.y)
        if closest_node:
            self.main_app.selection_manager.alternar_selecao(closest_node)
            self.main_app.view_manager.desenhar_grafo()
    
    def on_pan_start(self, event):
        #Inicia o pan
        if self.main_app.modo_edicao or not self.main_app.graph_manager.existe_grafo():
            return
        cursor = self.main_app.zoom_pan_tool.on_pan_start(event)
        self.canvas.config(cursor=cursor)
    
    def on_pan_move(self, event):
        #Move o pan
        if self.main_app.modo_edicao or not self.main_app.graph_manager.existe_grafo():
            return
        w, h = self.main_app.graph_drawer.obter_dimensoes_canvas()
        if self.main_app.zoom_pan_tool.on_pan_move(event, self.main_app.graph_manager, w, h):
            self.main_app.view_manager.desenhar_grafo_com_zoom_fluido()
    
    def on_pan_end(self, event):
        #Finaliza o pan
        cursor = self.main_app.zoom_pan_tool.on_pan_end()
        self.canvas.config(cursor=cursor)
    
    def on_mousewheel_zoom(self, event):
        #Gerencia zoom com scroll do mouse
        if self.main_app.modo_edicao or not self.main_app.graph_manager.existe_grafo():
            return
        w, h = self.main_app.graph_drawer.obter_dimensoes_canvas()
        if self.main_app.zoom_pan_tool.on_mousewheel_zoom(event, self.main_app.graph_manager, w, h):
            self.main_app.view_manager.atualizar_texto_zoom()
            self.main_app.view_manager.desenhar_grafo_com_zoom_fluido()
    
    def hide_tooltip(self, event=None):
        #Oculta o tooltip
        self.main_app.tooltip_manager.hide_tooltip()