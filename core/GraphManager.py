import osmnx as ox
import networkx as nx
import random
from math import radians, sin, cos, sqrt, atan2
from core.Dijkstra import Dijkstra

class GraphManager:
    def __init__(self):
        self.grafo = None
        self.bbox = None
        self.contador_vertices = 0
        self.reset_contador()
    
    def reset_contador(self):
        """Reseta o contador de vértices para 1"""
        self.contador_vertices = 1
    
    def importar_osm(self, caminho):
        """Importa um arquivo OSM e cria o grafo"""
        try:
            self.grafo = ox.graph_from_xml(caminho)
            return True
        except Exception as e:
            return str(e)
    
    def criar_grafo_vazio(self):
        """Cria um grafo vazio para modo de edição"""
        self.grafo = nx.Graph()
        self.bbox = (0, 0, 900, 650)
        return True
    
    def existe_grafo(self):
        """Verifica se existe um grafo carregado"""
        return self.grafo is not None and len(self.grafo.nodes) > 0
    
    def eh_grafo_osm(self):
        """Detecta se o grafo foi importado do OSM"""
        if not self.existe_grafo():
            return False
            
        # Verificar se algum nó tem o atributo 'osmid' ou se há arestas com atributos OSM
        for _, data in self.grafo.nodes(data=True):
            if 'osmid' in data:
                return True
        # Se não encontrou nos nós, verificar nas arestas
        if len(self.grafo.edges()) > 0:
            for _, _, data in self.grafo.edges(data=True):
                if 'highway' in data or 'osmid' in data or 'geometry' in data:
                    return True
        return False
    
    def obter_proximo_id_vertice(self):
        """Obtém o próximo ID disponível para um vértice"""
        if not self.grafo or not self.grafo.nodes():
            return 1  # Começar do ID 1 em vez de 0
        
        # Encontrar o menor ID não utilizado
        ids_utilizados = set(self.grafo.nodes())
        proximo_id = 1  # Começar do ID 1
        while proximo_id in ids_utilizados:
            proximo_id += 1
        return proximo_id
    
    def recalcular_contador(self):
        """Recalcula o contador de vértices baseado nos IDs existentes"""
        if self.grafo and self.grafo.nodes():
            self.contador_vertices = max(self.grafo.nodes()) + 1
        else:
            self.contador_vertices = 1
    
    def adicionar_vertice(self, x, y):
        """Adiciona um vértice ao grafo"""
        novo_id = self.obter_proximo_id_vertice()
        self.grafo.add_node(novo_id, x=x, y=y)
        return novo_id
    
    def adicionar_aresta(self, u, v, peso):
        """Adiciona uma aresta ao grafo"""
        self.grafo.add_edge(u, v, weight=peso)
        return True
    
    def remover_vertice(self, node):
        """Remove um vértice do grafo"""
        self.grafo.remove_node(node)
        self.recalcular_contador()
        return True
    
    def remover_aresta(self, u, v):
        """Remove uma aresta do grafo"""
        self.grafo.remove_edge(u, v)
        return True
    
    def gerar_vertices_aleatorios(self, quantidade):
        """Gera vértices aleatórios no grafo"""
        if not self.existe_grafo():
            self.criar_grafo_vazio()
            
        for _ in range(quantidade):
            x = random.uniform(50, 850)  # Margem de 50px das bordas
            y = random.uniform(50, 600)  # Margem de 50px das bordas
            novo_id = self.obter_proximo_id_vertice()
            self.grafo.add_node(novo_id, x=x, y=y)
        return True
    
    def gerar_arestas_aleatorias(self):
        """Gera arestas aleatórias entre os vértices existentes"""
        if not self.existe_grafo() or len(self.grafo.nodes()) < 2:
            return False
            
        # Remover todas as arestas existentes
        self.grafo.remove_edges_from(list(self.grafo.edges()))
        
        # Pegar lista de vértices
        vertices = list(self.grafo.nodes())
        
        # Garantir que todos os vértices estejam conectados (árvore geradora)
        vertices_conectados = {vertices[0]}
        vertices_restantes = set(vertices[1:])
        
        while vertices_restantes:
            v1 = random.choice(list(vertices_conectados))
            v2 = random.choice(list(vertices_restantes))
            peso = random.randint(10, 100)  # Peso entre 10 e 100
            self.grafo.add_edge(v1, v2, weight=peso)
            vertices_conectados.add(v2)
            vertices_restantes.remove(v2)
        
        # Adicionar arestas extras aleatoriamente
        num_arestas_extras = len(vertices) * 2  # Ajuste este número para mais ou menos densidade
        for _ in range(num_arestas_extras):
            v1 = random.choice(vertices)
            v2 = random.choice(vertices)
            if v1 != v2 and not self.grafo.has_edge(v1, v2):
                peso = random.randint(10, 100)
                self.grafo.add_edge(v1, v2, weight=peso)
        return True
    
    def calcular_distancia(self, lat1, lon1, lat2, lon2):
        """Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine"""
        R = 6371000  # Raio da Terra em metros
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    def calcular_rota(self, origem, destino):
        """Calcula a rota mais curta entre origem e destino usando Dijkstra"""
        if not self.existe_grafo():
            return None, "Grafo não existe!"
            
        # Verificar se os vértices origem e destino existem no grafo
        if origem not in self.grafo.nodes() or destino not in self.grafo.nodes():
            return None, "Vértices de origem ou destino não existem no grafo!"
            
        # Verificar se há arestas no grafo
        if len(self.grafo.edges()) == 0:
            return None, "Não há arestas no grafo! Adicione arestas para calcular rotas."
            
        # Converter o grafo do NetworkX para nosso formato
        grafo_dijkstra = {}
        for u, v, data in self.grafo.edges(data=True):
            if u not in grafo_dijkstra:
                grafo_dijkstra[u] = {}
            if v not in grafo_dijkstra:
                grafo_dijkstra[v] = {}
            
            # Usar o peso da aresta se existir, senão calcular a distância
            peso = data.get('weight', None)
            if peso is None:
                peso = self.calcular_distancia(
                    self.grafo.nodes[u]['y'], self.grafo.nodes[u]['x'],
                    self.grafo.nodes[v]['y'], self.grafo.nodes[v]['x']
                )
            
            # Adicionar aresta em ambas as direções (grafo não direcionado)
            grafo_dijkstra[u][v] = peso
            grafo_dijkstra[v][u] = peso
        
        # Verificar se os vértices origem e destino estão conectados no grafo
        if origem not in grafo_dijkstra or destino not in grafo_dijkstra:
            return None, "Vértices de origem ou destino não estão conectados no grafo!"
            
        try:
            # Criar instância do Dijkstra e calcular caminho
            dijkstra = Dijkstra(grafo_dijkstra)
            caminho, dist = dijkstra.encontrar_caminho(origem, destino)
            
            # Verificar se existe caminho
            if dist == float('inf') or not caminho or len(caminho) == 1:
                return None, "Não existe caminho entre os pontos selecionados!"
                
            stats = dijkstra.get_estatisticas()
            return {
                'caminho': caminho,
                'distancia': dist,
                'tempo': stats['tempo'],
                'nos_explorados': stats['nos_explorados']
            }
        except KeyError as e:
            return None, f"Erro ao calcular rota: vértice {e} não encontrado no grafo!"
        except Exception as e:
            return None, f"Erro inesperado ao calcular rota: {str(e)}"
    
    def limpar_grafo(self):
        """Limpa o grafo e reseta todas as variáveis relacionadas"""
        self.grafo = None
        self.bbox = None
        self.reset_contador()
    
    def obter_bbox_osm(self):
        """Obtém o bbox para grafos OSM"""
        if not self.existe_grafo():
            return None
            
        nodes = list(self.grafo.nodes(data=True))
        xs = [data['x'] for _, data in nodes]
        ys = [data['y'] for _, data in nodes]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return min_x, min_y, max_x, max_y

    def obter_bbox_manual(self):
        """Obtém o bbox para grafos manuais"""
        if not self.bbox:
            self.bbox = (0, 0, 900, 650)
        return self.bbox