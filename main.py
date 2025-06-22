import sys
import os

# Adicionar o diretório atual ao path para permitir imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def instalar_dependencias():
    #Instala as dependências do requirements.txt usando pip.
    print("Instalando dependências do requirements.txt...")
    try:
        os.system(f'"{sys.executable}" -m pip install -r requirements.txt')
        print("\nDependências instaladas com sucesso!\n")
    except Exception as e:
        print(f"Erro ao instalar dependências: {e}")
        sys.exit(1)

def rodar_app():
    from ui.MapaTkinter import MapaTkinter
    app = MapaTkinter()
    app.history_manager.refazer_rota_callback = app.refazer_rota
    app.mainloop()

def main():
    #Tenta rodar a aplicação normalmente. Se faltar dependências, oferece instalar automaticamente.
    try:
        rodar_app()
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
        print("Alguma dependência não está instalada.")
        escolha = input("Deseja que o programa instale as dependências automaticamente? (s/n): ").strip().lower()
        if escolha == 's':
            instalar_dependencias()
            try:
                rodar_app()
            except Exception as e2:
                print(f"Erro inesperado após instalar dependências: {e2}")
                sys.exit(1)
        else:
            print("Instale manualmente com: pip install -r requirements.txt")
            sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 