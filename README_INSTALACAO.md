# 🚀 GUIA DE INSTALAÇÃO E EXECUÇÃO
## Navegador OSM - Visualizador de Grafos

Este guia fornece instruções detalhadas para instalar e executar o Navegador OSM em diferentes sistemas operacionais.

---

## 📋 PRÉ-REQUISITOS

### 🔧 Requisitos Mínimos
- **Python**: 3.7 ou superior
- **Sistema Operacional**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Memória RAM**: 4GB mínimo
- **Espaço em Disco**: 100MB livres
- **Conexão com Internet**: Para download de dependências

### 🎯 Requisitos Recomendados
- **Python**: 3.9 ou superior
- **Sistema Operacional**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Memória RAM**: 8GB ou mais
- **Espaço em Disco**: 500MB livres
- **Resolução de Tela**: 1920x1080 ou superior

---

## 🛠️ INSTALAÇÃO

### 📥 Opção 1: Instalação Automática (Recomendada)

#### Windows
1. **Baixe o instalador:**
   - Execute o arquivo `install.bat` como administrador
   - Ou use o script Python: `python install.py`

2. **Siga as instruções na tela:**
   - Escolha o diretório de instalação
   - Aguarde o download das dependências
   - Confirme a instalação

#### Linux/macOS
1. **Execute o script de instalação:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **Ou use o script Python:**
   ```bash
   python3 install.py
   ```

### 📥 Opção 2: Instalação Manual

#### Passo 1: Preparar o Ambiente
```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/CursorAED.git
cd CursorAED

# 2. Criar ambiente virtual (recomendado)
python -m venv venv

# 3. Ativar o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

#### Passo 2: Instalar Dependências
```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação
python -c "import osmnx, networkx, PIL; print('Dependências instaladas com sucesso!')"
```

#### Passo 3: Verificar Instalação
```bash
# Testar se tudo está funcionando
python main.py
```

---

## 🚀 EXECUÇÃO

### 🎮 Primeira Execução

1. **Abra o terminal/prompt de comando**
2. **Navegue até o diretório do projeto:**
   ```bash
   cd CursorAED
   ```

3. **Ative o ambiente virtual (se usado):**
   ```bash
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

4. **Execute o aplicativo:**
   ```bash
   python main.py
   ```

### 🖥️ Interface Inicial

Após a execução, você verá:
- **Janela principal** com área de visualização
- **Painel lateral** com controles
- **Barra de status** na parte inferior

### 🎯 Primeiros Passos

1. **Importar um mapa OSM:**
   - Clique em "📂 Importar OSM"
   - Selecione um arquivo .osm
   - Aguarde o carregamento

2. **Navegar no mapa:**
   - **Zoom**: Scroll do mouse
   - **Pan**: Ctrl + clique e arraste
   - **Reset**: Clique no botão "🔍"

3. **Calcular uma rota:**
   - Clique em dois pontos do mapa
   - Clique em "🛣️ Calcular Rota"

---

## 📁 ESTRUTURA DE ARQUIVOS

```
CursorAED/
├── main.py                    # 🚀 Ponto de entrada
├── install.py                 # 🔧 Script de instalação
├── install.bat                # 🔧 Instalador Windows
├── install.sh                 # 🔧 Instalador Linux/macOS
├── requirements.txt           # 📦 Dependências
├── README.md                  # 📚 Documentação geral
├── DOCUMENTACAO_TECNICA.md    # 📋 Documentação técnica
├── README_INSTALACAO.md       # 📖 Este arquivo
├── core/                      # 🧠 Lógica principal
├── ui/                        # 🖥️ Interface gráfica
├── managers/                  # 📋 Gerenciadores
└── assets/                    # 🖼️ Recursos
    └── capturas/             # 📸 Imagens salvas
```

---

## 🔧 CONFIGURAÇÃO

### ⚙️ Configurações Básicas

O aplicativo funciona com configurações padrão, mas você pode personalizar:

#### Configurações de Performance
```python
# No arquivo config.py (criar se necessário)
MAX_NODES = 1000          # Máximo de nós no grafo
CACHE_SIZE = 100          # Tamanho do cache em MB
AUTO_SAVE = True          # Salvamento automático
```

#### Configurações de Interface
```python
DEFAULT_ZOOM = 1.0        # Zoom inicial
GRID_ENABLED = True       # Mostrar grade
SHOW_DISTANCES = False    # Mostrar distâncias
```

### 🎨 Personalização Visual

#### Cores do Grafo
- **Vértices**: Azul padrão
- **Arestas**: Cinza padrão
- **Caminho**: Verde
- **Seleção**: Vermelho

#### Tamanhos
- **Vértices**: 6px padrão
- **Arestas**: 2px padrão
- **Fonte**: 10pt padrão

---

## 🐛 SOLUÇÃO DE PROBLEMAS

### ❌ Erros Comuns

#### Erro: "ModuleNotFoundError: No module named 'osmnx'"
**Solução:**
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install osmnx==1.8.1
```

#### Erro: "Tkinter not found"
**Solução:**
```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS:
brew install python-tk
```

#### Erro: "Permission denied" no Linux/macOS
**Solução:**
```bash
# Dar permissão de execução
chmod +x install.sh
chmod +x main.py
```

#### Erro: "Python not found"
**Solução:**
1. **Verificar instalação do Python:**
   ```bash
   python --version
   python3 --version
   ```

2. **Adicionar Python ao PATH (Windows):**
   - Instalar Python com "Add to PATH" marcado
   - Ou adicionar manualmente nas variáveis de ambiente

### 🔍 Verificação de Instalação

Execute este script para verificar se tudo está funcionando:

```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import tkinter
    print('✓ Tkinter: OK')
except ImportError:
    print('✗ Tkinter: FALHOU')

try:
    import osmnx
    print(f'✓ OSMNX: {osmnx.__version__}')
except ImportError:
    print('✗ OSMNX: FALHOU')

try:
    import networkx
    print(f'✓ NetworkX: {networkx.__version__}')
except ImportError:
    print('✗ NetworkX: FALHOU')

try:
    import PIL
    print(f'✓ Pillow: {PIL.__version__}')
except ImportError:
    print('✗ Pillow: FALHOU')

print('\\nVerificação concluída!')
"
```

### 📞 Suporte

Se você encontrar problemas:

1. **Verifique os logs:**
   - Windows: `%APPDATA%\CursorAED\logs\`
   - Linux/macOS: `~/.local/share/CursorAED/logs/`

2. **Consulte a documentação:**
   - `README.md` - Documentação geral
   - `DOCUMENTACAO_TECNICA.md` - Documentação técnica

3. **Abra uma issue no GitHub:**
   - Inclua detalhes do erro
   - Anexe logs se disponível
   - Especifique seu sistema operacional

---

## 🔄 ATUALIZAÇÃO

### 📦 Atualização Automática

```bash
# 1. Fazer backup (opcional)
cp -r CursorAED CursorAED_backup

# 2. Atualizar código
git pull origin main

# 3. Atualizar dependências
pip install -r requirements.txt --upgrade

# 4. Testar
python main.py
```

### 🔧 Atualização Manual

1. **Baixar nova versão**
2. **Fazer backup da versão atual**
3. **Substituir arquivos**
4. **Reinstalar dependências**
5. **Testar funcionamento**

---

## 🗂️ ARQUIVOS DE EXEMPLO

### 📁 Dados OSM de Teste

O projeto inclui arquivos de exemplo para teste:

```
assets/
├── exemplos/
│   ├── pequeno.osm          # Grafo pequeno (10 nós)
│   ├── medio.osm            # Grafo médio (50 nós)
│   └── grande.osm           # Grafo grande (200 nós)
└── capturas/                # Imagens salvas
```

### 🧪 Testes Rápidos

```bash
# Teste básico
python main.py

# Teste com arquivo específico
python main.py --file assets/exemplos/pequeno.osm

# Teste em modo debug
python main.py --debug
```

---

## 📊 DESEMPENHO

### ⚡ Otimizações Recomendadas

#### Para Grafos Grandes (>500 nós)
- **Memória**: 8GB+ RAM
- **Processador**: 4+ cores
- **Disco**: SSD recomendado

#### Configurações de Performance
```python
# Ajustar para melhor performance
MAX_CACHE_SIZE = 200        # MB
RENDER_QUALITY = 'fast'     # 'fast' ou 'quality'
AUTO_SAVE_INTERVAL = 300    # segundos
```

### 📈 Métricas Esperadas

| Tamanho do Grafo | Carregamento | Dijkstra | Memória |
|------------------|--------------|----------|---------|
| 100 nós          | < 1s         | < 0.1s   | < 50MB  |
| 500 nós          | < 2s         | < 0.5s   | < 200MB |
| 1000 nós         | < 5s         | < 1s     | < 500MB |

---

## 🎯 PRÓXIMOS PASSOS

Após a instalação bem-sucedida:

1. **📚 Leia a documentação:**
   - `README.md` - Guia de uso
   - `DOCUMENTACAO_TECNICA.md` - Detalhes técnicos

2. **🧪 Faça testes:**
   - Importe diferentes arquivos OSM
   - Teste o algoritmo de Dijkstra
   - Experimente as funcionalidades de zoom/pan

3. **🎨 Personalize:**
   - Ajuste cores e tamanhos
   - Configure atalhos de teclado
   - Modifique configurações de performance

4. **📈 Explore recursos avançados:**
   - Histórico de rotas
   - Captura de imagens
   - Modo de edição

---

## 📝 NOTAS IMPORTANTES

### ⚠️ Limitações Conhecidas
- **Tamanho máximo**: 1000 nós por grafo
- **Formatos suportados**: Apenas arquivos .osm
- **Sistemas**: Testado em Windows, macOS e Ubuntu

### 🔒 Segurança
- O aplicativo não requer privilégios de administrador
- Não coleta dados pessoais
- Arquivos são processados localmente

### 📄 Licença
Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

**🎉 Parabéns! Você instalou com sucesso o Navegador OSM!**

Para começar a usar, execute `python main.py` e divirta-se explorando grafos e calculando rotas!

---

**📞 Precisa de ajuda?**
- 📧 Email: suporte@cursoraed.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: Documentação completa no repositório

**🔄 Última atualização**: Dezembro 2024  
**Versão**: 1.0.0 