class ToggleManager:
    def __init__(self, main_app):
        self.main_app = main_app
    
    def toggle_pontos(self):
        #Alterna exibição de pontos
        mostrar = self.main_app.selection_manager.toggle_pontos()
        self.main_app.action_panel.configurar_texto_pontos(mostrar)
        self.main_app.view_manager.desenhar_grafo()
    
    def toggle_distancias(self):
        #Alterna exibição de distâncias
        # Verificar se há mais de 150 vértices
        if self.main_app.graph_manager.existe_grafo():
            num_vertices = len(self.main_app.graph_manager.grafo.nodes())
            if num_vertices > 150:
                # Desabilitar o botão e mostrar mensagem
                self.main_app.sidebar.buttons['dist'].config(state='disabled', text="Exibir Distâncias")
                self.main_app.mostrar_distancias = False
                self.main_app.view_manager.desenhar_grafo()
                return
        
        self.main_app.mostrar_distancias = not self.main_app.mostrar_distancias
        self.main_app.sidebar.buttons['dist'].config(text="Ocultar Distâncias" if self.main_app.mostrar_distancias else "Exibir Distâncias")
        self.main_app.view_manager.desenhar_grafo()
    
    def toggle_cores_ruas(self):
        #Alterna cores personalizadas
        self.main_app.cores_personalizadas = not self.main_app.cores_personalizadas
        
        # Alterar cor do botão baseado no estado
        if self.main_app.cores_personalizadas:
            # Usar a mesma cor do botão ativo (Criar Grafo)
            self.main_app.sidebar.buttons['cores'].configure(**self.main_app.sidebar.btn_style_ativo)
        else:
            # Voltar para a cor normal
            self.main_app.sidebar.buttons['cores'].configure(**self.main_app.sidebar.btn_style_normal)
        
        self.main_app.view_manager.desenhar_grafo()
    
    def limpar_selecao(self):
        #Limpa seleção atual
        self.main_app.selection_manager.limpar_selecao()
        self.main_app.action_panel.configurar_texto_pontos(True)
        self.main_app.view_manager.desenhar_grafo()