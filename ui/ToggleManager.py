class ToggleManager:
    def __init__(self, main_app):
        self.main_app = main_app
    
    def toggle_pontos(self):
        """Alterna exibição de pontos"""
        mostrar = self.main_app.selection_manager.toggle_pontos()
        self.main_app.action_panel.configurar_texto_pontos(mostrar)
        self.main_app.view_manager.desenhar_grafo()
    
    def toggle_distancias(self):
        """Alterna exibição de distâncias"""
        self.main_app.mostrar_distancias = not self.main_app.mostrar_distancias
        self.main_app.sidebar.buttons['dist'].config(text="Ocultar Distâncias" if self.main_app.mostrar_distancias else "Exibir Distâncias")
        self.main_app.view_manager.desenhar_grafo()
    
    def toggle_cores_ruas(self):
        """Alterna cores personalizadas"""
        self.main_app.cores_personalizadas = not self.main_app.cores_personalizadas
        self.main_app.view_manager.desenhar_grafo()
    
    def limpar_selecao(self):
        """Limpa seleção atual"""
        self.main_app.selection_manager.limpar_selecao()
        self.main_app.action_panel.configurar_texto_pontos(True)
        self.main_app.view_manager.desenhar_grafo()