from tkinter import filedialog, messagebox, simpledialog

class GraphOperations:
    def __init__(self, main_app):
        self.main_app = main_app
    
    def importar_osm(self):
        #Importa arquivo OSM
        caminho = filedialog.askopenfilename(filetypes=[("OSM files", "*.osm"), ("Todos arquivos", "*.*")])
        if caminho:
            resultado = self.main_app.graph_manager.importar_osm(caminho)
            if resultado is True:
                self.main_app.selection_manager.limpar_selecao()
                self.main_app.selection_manager.resetar_tooltips_ajuda()
                self.main_app.zoom_pan_tool.reset_zoom_pan()
                self.main_app.ui_manager.ocultar_botoes_centrais()
                self.main_app.ui_manager.atualizar_estado_botoes()
                self.main_app.view_manager.desenhar_grafo()
            else:
                messagebox.showerror("Erro", resultado)
    
    def toggle_modo_edicao(self):
        #Alterna modo de edição
        self.main_app.modo_edicao = not self.main_app.modo_edicao
        if self.main_app.modo_edicao:
            self.main_app.sidebar.configurar_botao_edicao(True)
            self.main_app.sidebar.mostrar_frame_edicao()
            self.main_app.zoom_pan_tool.reset_zoom_pan()
            if not self.main_app.graph_manager.existe_grafo():
                self.main_app.graph_manager.criar_grafo_vazio()
            self.main_app.selection_manager.limpar_selecao()
            self.main_app.ui_manager.ocultar_botoes_centrais()
            # Alterar highlightbackground do canvas para a cor do botão ativo
            self.main_app.canvas.config(highlightbackground="#00ffcc")
        else:
            self.main_app.sidebar.configurar_botao_edicao(False)
            self.main_app.sidebar.ocultar_frame_edicao()
            self.main_app.selection_manager.vertice_selecionado = None
            self.main_app.selection_manager.criando_aresta = False
            if not self.main_app.graph_manager.existe_grafo():
                self.main_app.graph_manager.limpar_grafo()
                self.main_app.zoom_pan_tool.reset_zoom_pan()
            # Restaurar highlightbackground do canvas para a cor padrão
            self.main_app.canvas.config(highlightbackground="#3a3b3e")
        self.main_app.ui_manager.atualizar_estado_botoes()
        self.main_app.view_manager.desenhar_grafo()
    
    def gerar_vertices_aleatorios(self):
        #Gera vértices aleatórios
        quantidade = simpledialog.askinteger("Gerar Vértices", 
                                           "Quantos vértices deseja gerar?",
                                           minvalue=1, maxvalue=10000, initialvalue=10)
        if quantidade:
            self.main_app.graph_manager.gerar_vertices_aleatorios(quantidade)
            self.main_app.ui_manager.ocultar_botoes_centrais()
            self.main_app.view_manager.desenhar_grafo()
            self.main_app.ui_manager.atualizar_estado_botoes()
    
    def gerar_arestas_aleatorias(self):
        #Gera arestas aleatórias
        if self.main_app.graph_manager.gerar_arestas_aleatorias():
            self.main_app.view_manager.desenhar_grafo()
        else:
            messagebox.showwarning("Aviso", "É necessário ter pelo menos 2 vértices para gerar arestas!")
    
    def apagar_grafo(self):
        #Apaga o grafo atual
        self.main_app.graph_manager.limpar_grafo()
        self.main_app.selection_manager.limpar_selecao()
        self.main_app.zoom_pan_tool.reset_zoom_pan()
        self.main_app.history_manager.historico_rotas.clear()
        self.main_app.history_manager.historico_capturas.clear()
        self.main_app.history_manager.atualizar_historico()
        self.main_app.view_manager.desenhar_grafo()
        self.main_app.ui_manager.atualizar_estado_botoes()
    
    def calcular_rota(self):
        #Calcula rota entre origem e destino
        if not self.main_app.graph_manager.existe_grafo() or not self.main_app.selection_manager.origem or not self.main_app.selection_manager.destino:
            messagebox.showwarning("Aviso", "Selecione origem e destino!")
            return
            
        resultado = self.main_app.graph_manager.calcular_rota(self.main_app.selection_manager.origem, self.main_app.selection_manager.destino)
        if resultado and isinstance(resultado, dict):
            self.main_app.selection_manager.definir_caminho(resultado['caminho'])
            self.main_app.action_panel.configurar_texto_pontos(False)
            self.main_app.view_manager.desenhar_grafo()
            
            # Marcar que os tooltips de ajuda já foram mostrados
            self.main_app.selection_manager.marcar_tooltips_mostrados()
            
            info_rota = {
                'origem': self.main_app.selection_manager.origem,
                'destino': self.main_app.selection_manager.destino,
                'distancia': resultado['distancia'],
                'tempo': resultado['tempo'],
                'nos_explorados': resultado['nos_explorados'],
                'caminho': self.main_app.selection_manager.caminho.copy()
            }
            self.main_app.history_manager.adicionar_rota(info_rota)
        else:
            messagebox.showwarning("Sem caminho", "Não existe caminho entre os pontos selecionados!")