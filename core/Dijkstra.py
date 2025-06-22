import heapq
import time
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class DijkstraData:
    distancias: Dict[int, float] = field(default_factory=lambda: defaultdict(lambda: float('inf')))
    predecessores: Dict[int, Optional[int]] = field(default_factory=lambda: defaultdict(lambda: None))
    visitados: Set[int] = field(default_factory=set)
    heap: List[Tuple[float, int]] = field(default_factory=list)
    nos_explorados: int = 0
    tempo_inicio: float = 0
    tempo_fim: float = 0

class Dijkstra:
    def __init__(self, grafo: Dict[int, Dict[int, float]]):

        self.grafo = grafo
        
    def encontrar_caminho(self, origem: int, destino: int) -> Tuple[List[int], float]:

        dados = DijkstraData()
        dados.tempo_inicio = time.time()
        
        # Inicialização
        dados.distancias[origem] = 0
        heapq.heappush(dados.heap, (0, origem))
        
        while dados.heap:
            distancia_atual, vertice_atual = heapq.heappop(dados.heap)
            dados.nos_explorados += 1
            
            if vertice_atual == destino:
                break
                
            if vertice_atual in dados.visitados:
                continue
                
            dados.visitados.add(vertice_atual)
            
            # Processa os vizinhos do vértice atual
            for vizinho, peso in self.grafo[vertice_atual].items():
                if vizinho in dados.visitados:
                    continue
                    
                nova_distancia = dados.distancias[vertice_atual] + peso
                
                if nova_distancia < dados.distancias[vizinho]:
                    dados.distancias[vizinho] = nova_distancia
                    dados.predecessores[vizinho] = vertice_atual
                    heapq.heappush(dados.heap, (nova_distancia, vizinho))
                    
        dados.tempo_fim = time.time()
        
        # Reconstruir o caminho
        caminho = []
        vertice_atual = destino
        
        while vertice_atual is not None:
            caminho.append(vertice_atual)
            vertice_atual = dados.predecessores[vertice_atual]
            
        caminho.reverse()
        
        # Salvar os dados para estatísticas
        self.dados = dados
        
        return caminho, dados.distancias[destino]
        
    def get_estatisticas(self) -> Dict[str, float]:

        if not hasattr(self, 'dados'):
            return {
                'tempo': 0,
                'nos_explorados': 0,
                'custo_total': float('inf')
            }
            
        return {
            'tempo': self.dados.tempo_fim - self.dados.tempo_inicio,
            'nos_explorados': self.dados.nos_explorados,
            'custo_total': self.dados.distancias.get(list(self.grafo.keys())[-1], float('inf'))
        } 