# GUIA DO GRUPO - SISTEMA MAPAAED

## VISÃO GERAL DO SISTEMA

O MapaAED é uma aplicação de visualização e manipulação de grafos que permite trabalhar com dois tipos principais de dados:
1. **Grafos Manuais**: Criados pelo usuário através da interface
2. **Grafos OSM**: Importados de arquivos OpenStreetMap (.osm)

## ARQUITETURA DO SISTEMA

### Estrutura de Pastas
- **core/**: Algoritmos fundamentais (Dijkstra, operações de grafo)
- **managers/**: Gerenciadores de funcionalidades específicas
- **ui/**: Interface gráfica e componentes visuais
- **assets/**: Recursos como capturas de tela

### Padrões de Design Utilizados
- **Manager Pattern**: Cada funcionalidade tem seu próprio gerenciador
- **Observer Pattern**: Sistema de eventos para detectar mudanças
- **State Pattern**: Controle de estados dos botões baseado no contexto

## FUNCIONALIDADES PRINCIPAIS

### 1. CRIAÇÃO E EDIÇÃO DE GRAFOS

#### Grafos Manuais
- **Criação de Vértices**: Clique no canvas para adicionar vértices
- **Geração de Arestas**: Conecta automaticamente todos os vértices
- **Pesos das Arestas**: Calculados automaticamente baseados na distância euclidiana
- **Edição**: Possibilidade de adicionar/remover vértices e arestas

#### Grafos OSM
- **Importação**: Carrega dados de arquivos .osm
- **Conversão Automática**: Intersecções viram vértices, ruas viram arestas
- **Preservação de Dados**: Mantém informações originais do OSM
- **Cálculo de Distâncias**: Usa fórmula de Haversine para distâncias geográficas

### 2. ALGORITMO DE DIJKSTRA

#### Preparação dos Dados
- Converte o grafo para formato adequado ao algoritmo
- Identifica vértices de origem e destino
- Prepara estruturas de dados para o processamento

#### Execução do Algoritmo
- Encontra o caminho mais curto entre dois pontos
- Considera os pesos das arestas (distâncias)
- Mantém registro dos caminhos intermediários

#### Reconstrução do Caminho
- Reconstrói o caminho completo a partir dos dados do algoritmo
- Calcula a distância total do percurso
- Exibe o resultado visualmente no grafo

### 3. SISTEMA DE CONTROLE INTELIGENTE

#### Detecção de Tipo de Grafo
O sistema automaticamente detecta se está trabalhando com:
- **Grafo Manual**: Sem atributos OSM
- **Grafo OSM**: Com atributos específicos do OpenStreetMap

#### Controle Contextual de Botões
- **Botão de Distâncias**: Habilitado apenas para grafos manuais
- **Botão de Gerar Arestas**: Habilitado apenas quando há pelo menos 2 vértices
- **Botões de Edição**: Habilitados apenas no modo de edição
- **Botões de Navegação**: Sempre disponíveis quando há grafo

### 4. SISTEMA DE CAPTURAS

#### Funcionalidade
- Salva capturas de tela do estado atual do grafo
- Numeração automática: "Captura 1.", "Captura 2.", etc.
- Armazenamento em pasta específica com timestamp
- Histórico visual na interface

#### Organização
- Arquivos salvos em `managers/capturas/`
- Nomenclatura: `grafo_YYYYMMDD_HHMMSS.png`
- Integração com painel de histórico

## CÁLCULOS E ALGORITMOS

### 1. Cálculo de Distâncias

#### Para Grafos Manuais
- **Fórmula**: Distância euclidiana entre coordenadas
- **Unidade**: Pixels (convertidos para metros)
- **Armazenamento**: Peso salvo diretamente na aresta

#### Para Grafos OSM
- **Fórmula**: Haversine (considera curvatura da Terra)
- **Parâmetros**: 
  - Raio da Terra: 6.371.000 metros
  - Coordenadas em latitude/longitude
- **Cálculo Dinâmico**: Realizado a cada consulta

### 2. Algoritmo de Dijkstra

#### Estrutura de Dados
- **Fila de Prioridade**: Para selecionar vértice com menor distância
- **Dicionário de Distâncias**: Armazena distâncias mínimas
- **Dicionário de Predecessores**: Para reconstruir o caminho

#### Processo de Execução
1. Inicialização com distância infinita para todos os vértices
2. Distância zero para o vértice de origem
3. Iteração até visitar o vértice de destino
4. Atualização de distâncias através de relaxamento de arestas

### 3. Conversão OSM para Grafo

#### Processo de Importação
1. **Leitura do XML**: Parse do arquivo .osm
2. **Identificação de Nós**: Pontos de intersecção viram vértices
3. **Criação de Arestas**: Segmentos de rua conectam os vértices
4. **Preservação de Metadados**: Mantém informações originais

## REGRAS E RESTRIÇÕES

### 1. Validações de Interface
- **Mínimo de Vértices**: 2 vértices necessários para gerar arestas
- **Tipo de Grafo**: Controle específico baseado na origem dos dados
- **Modo de Edição**: Botões habilitados apenas quando apropriado

### 2. Restrições de Funcionalidades
- **Distâncias OSM**: Não exibidas (cálculo complexo)
- **Edição de Grafos OSM**: Limitada para preservar integridade
- **Geração de Arestas**: Apenas quando há vértices suficientes

### 3. Controle de Estados
- **Detecção Automática**: Sistema identifica contexto atual
- **Atualização Dinâmica**: Estados mudam conforme ações do usuário
- **Consistência**: Interface sempre reflete estado válido

## FLUXO DE TRABALHO

### 1. Criação de Grafo Manual
1. Usuário ativa modo de edição
2. Clica no canvas para adicionar vértices
3. Usa botão "Gerar Arestas" (quando há 2+ vértices)
4. Pode exibir distâncias das arestas
5. Pode calcular menor rota entre pontos

### 2. Importação de Grafo OSM
1. Usuário seleciona arquivo .osm
2. Sistema converte automaticamente
3. Botão de distâncias fica desabilitado
4. Funcionalidades de rota permanecem disponíveis
5. Distâncias calculadas dinamicamente

### 3. Cálculo de Menor Rota
1. Usuário seleciona vértice de origem
2. Seleciona vértice de destino
3. Sistema executa algoritmo de Dijkstra
4. Caminho é destacado visualmente
5. Distância total é exibida

## PONTOS IMPORTANTES PARA O GRUPO

### 1. Separação de Responsabilidades
- Cada gerenciador tem função específica
- Interface separada da lógica de negócio
- Algoritmos isolados em módulos próprios

### 2. Extensibilidade
- Fácil adição de novos algoritmos
- Sistema modular permite expansões
- Padrões consistentes facilitam manutenção

### 3. Robustez
- Validações em múltiplos níveis
- Tratamento de casos especiais
- Interface adaptativa ao contexto

### 4. Performance
- Cálculos otimizados para grafos grandes
- Lazy loading de funcionalidades
- Cache de resultados quando apropriado

## CONSIDERAÇÕES TÉCNICAS

### 1. Bibliotecas Utilizadas
- **NetworkX**: Manipulação de grafos
- **OSMnx**: Importação de dados OSM
- **Tkinter**: Interface gráfica
- **PIL**: Processamento de imagens

### 2. Estruturas de Dados
- **Grafo**: Representação NetworkX
- **Nós**: Dicionários com coordenadas e metadados
- **Arestas**: Dicionários com pesos e atributos

### 3. Sistema de Coordenadas
- **Grafos Manuais**: Sistema de coordenadas do canvas
- **Grafos OSM**: Latitude/longitude (WGS84)
- **Conversões**: Automáticas quando necessário

## 🎨 Visualização e Interface

### Sistema de Renderização
O aplicativo utiliza um sistema de renderização otimizado que se adapta ao nível de zoom e quantidade de dados:

**Renderização Inteligente:**
- **Zoom Ativo**: Quando o usuário faz zoom ou pan, o sistema usa renderização otimizada com supersample reduzido para melhor performance
- **Zoom Normal**: Renderização completa com alta qualidade para visualização detalhada
- **Adaptação Automática**: O sistema detecta automaticamente quando usar cada tipo de renderização

**Limite de Distâncias:**
- **150 Vértices**: Para manter a performance e legibilidade, as distâncias das arestas só são exibidas em grafos com até 150 vértices
- **Controle Automático**: O botão "Exibir Distâncias" é automaticamente desabilitado quando o limite é excedido
- **Aplicação**: Este limite se aplica tanto ao modo de edição quanto ao modo de visualização
- **Justificativa**: Grafos com muitos vértices ficariam poluídos visualmente com muitas informações de distância

### Cores e Estilos

**Sistema de Cores das Ruas:**
- **Azul (#2196f3)**: Ruas de mão única (oneway)
- **Laranja (#ff9800)**: Ruas de mão dupla
- **Vermelho (#ff3333)**: Rota calculada pelo algoritmo de Dijkstra
- **Cinza (#77787C)**: Cor padrão quando cores personalizadas estão desabilitadas

**Legenda Automática:**
- **Posição**: Canto inferior direito do canvas
- **Ativação**: Aparece automaticamente quando o botão "Identificar Vias" está ativo
- **Conteúdo**: Mostra as cores e seus significados
- **Visibilidade**: Apenas para grafos OSM (não aparece em grafos manuais)
- **Design**: Fundo semi-transparente com bordas para melhor legibilidade

Este documento serve como referência para entender o funcionamento interno do sistema, facilitando a manutenção e expansão futuras do projeto. 