class SelectionManager:
    def __init__(self):
        self.origem = None
        self.destino = None
        self.caminho = None
        self.vertice_selecionado = None
        self.criando_aresta = False
        self.selecionando = 'origem'
        self.mostrar_pontos = True
    
    def limpar_selecao(self):
        """Limpa toda a seleção"""
        self.origem = None
        self.destino = None
        self.caminho = None
        self.vertice_selecionado = None
        self.criando_aresta = False
        self.selecionando = 'origem'
        self.mostrar_pontos = True
    
    def selecionar_origem(self, vertice):
        """Seleciona o vértice de origem"""
        self.origem = vertice
        self.selecionando = 'destino'
        self.caminho = None
    
    def selecionar_destino(self, vertice):
        """Seleciona o vértice de destino"""
        self.destino = vertice
        self.selecionando = 'origem'
        self.caminho = None
    
    def alternar_selecao(self, vertice):
        """Alterna entre origem e destino"""
        if not self.origem:
            self.selecionar_origem(vertice)
        elif not self.destino:
            self.selecionar_destino(vertice)
        else:
            self.selecionar_origem(vertice)
            self.destino = None
    
    def definir_caminho(self, caminho):
        """Define o caminho calculado"""
        self.caminho = caminho
        self.mostrar_pontos = False
    
    def toggle_pontos(self):
        """Alterna a exibição de pontos"""
        self.mostrar_pontos = not self.mostrar_pontos
        return self.mostrar_pontos