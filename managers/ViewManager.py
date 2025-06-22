class ViewManager:
    def __init__(self, main_app):
        self.main_app = main_app
    
    def desenhar_grafo(self):
        #Desenha o grafo principal
        self.main_app.imgtk = self.main_app.graph_drawer.desenhar_canvas_vazio()
        
        if not self.main_app.graph_manager.existe_grafo():
            self.main_app.ui_manager.mostrar_botoes_centrais()
            return
            
        if self.main_app.zoom_pan_tool.tem_zoom_ativo(self.main_app.zoom_pan_tool.zoom_level, self.main_app.zoom_pan_tool.pan_x, self.main_app.zoom_pan_tool.pan_y):
            self.main_app.imgtk = self.main_app.graph_drawer.desenhar_grafo_otimizado(
                zoom_level=self.main_app.zoom_pan_tool.zoom_level,
                pan_x=self.main_app.zoom_pan_tool.pan_x,
                pan_y=self.main_app.zoom_pan_tool.pan_y,
                mostrar_distancias=self.main_app.mostrar_distancias,
                cores_personalizadas=self.main_app.cores_personalizadas,
                caminho=self.main_app.selection_manager.caminho,
                origem=self.main_app.selection_manager.origem,
                destino=self.main_app.selection_manager.destino,
                mostrar_pontos=self.main_app.selection_manager.mostrar_pontos,
                modo_edicao=self.main_app.modo_edicao,
                vertice_selecionado=self.main_app.selection_manager.vertice_selecionado
            )
        else:
            self.main_app.imgtk = self.main_app.graph_drawer.desenhar_grafo(
                zoom_level=self.main_app.zoom_pan_tool.zoom_level,
                pan_x=self.main_app.zoom_pan_tool.pan_x,
                pan_y=self.main_app.zoom_pan_tool.pan_y,
                mostrar_distancias=self.main_app.mostrar_distancias,
                cores_personalizadas=self.main_app.cores_personalizadas,
                caminho=self.main_app.selection_manager.caminho,
                origem=self.main_app.selection_manager.origem,
                destino=self.main_app.selection_manager.destino,
                mostrar_pontos=self.main_app.selection_manager.mostrar_pontos,
                modo_edicao=self.main_app.modo_edicao,
                vertice_selecionado=self.main_app.selection_manager.vertice_selecionado
            )
    
    def desenhar_grafo_com_zoom_fluido(self):
        #Desenha o grafo usando a versão otimizada quando há zoom/pan ativo
        self.main_app.imgtk = self.main_app.graph_drawer.desenhar_grafo_otimizado(
            zoom_level=self.main_app.zoom_pan_tool.zoom_level,
            pan_x=self.main_app.zoom_pan_tool.pan_x,
            pan_y=self.main_app.zoom_pan_tool.pan_y,
            mostrar_distancias=self.main_app.mostrar_distancias,
            cores_personalizadas=self.main_app.cores_personalizadas,
            caminho=self.main_app.selection_manager.caminho,
            origem=self.main_app.selection_manager.origem,
            destino=self.main_app.selection_manager.destino,
            mostrar_pontos=self.main_app.selection_manager.mostrar_pontos,
            modo_edicao=self.main_app.modo_edicao,
            vertice_selecionado=self.main_app.selection_manager.vertice_selecionado
        )
    
    def zoom_in(self):
        #Aumenta o zoom
        if self.main_app.modo_edicao:
            return
        if self.main_app.zoom_pan_tool.zoom_in():
            self.atualizar_texto_zoom()
            self.desenhar_grafo_com_zoom_fluido()
    
    def zoom_out(self):
        #Diminui o zoom
        if self.main_app.modo_edicao:
            return
        if self.main_app.zoom_pan_tool.zoom_out():
            self.atualizar_texto_zoom()
            self.desenhar_grafo_com_zoom_fluido()
    
    def zoom_reset(self):
        #Reseta o zoom
        if self.main_app.modo_edicao:
            return
        self.main_app.zoom_pan_tool.reset_zoom_pan()
        self.atualizar_texto_zoom()
        self.desenhar_grafo()
    
    def atualizar_texto_zoom(self):
        #Atualiza o texto do zoom
        zoom_percent = int(self.main_app.zoom_pan_tool.zoom_level * 100)
        self.main_app.zoom_panel.atualizar_texto_zoom(zoom_percent)