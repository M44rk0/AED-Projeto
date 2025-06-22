import sys
import os

# Adicionar o diretório atual ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Função principal que inicia a aplicação."""
    try:
        # Importar a classe principal
        from ui.MapaTkinter import MapaTkinter
        
        # Criar e executar a aplicação
        app = MapaTkinter()
        app.history_manager.refazer_rota_callback = app.refazer_rota
        app.mainloop()
        
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
        print("Certifique-se de que todas as dependências estão instaladas.")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 