from tkinter import messagebox
from PIL import ImageGrab
import io
import os
from datetime import datetime

class ImageManager:
    def __init__(self, main_app):
        self.main_app = main_app
        self.capturas_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas")
        self.zoom_overlay = None
    
    def set_zoom_overlay(self, zoom_overlay):
        #Define a referência para o overlay de zoom
        self.zoom_overlay = zoom_overlay
    
    def capturar_canvas(self):
        #Captura a imagem do canvas
        # Ocultar botões de zoom temporariamente
        zoom_visivel = self.zoom_overlay.winfo_viewable() if self.zoom_overlay else False
        if zoom_visivel:
            self.zoom_overlay.place_forget()
        
        # Capturar imagem
        self.main_app.update()
        x = self.main_app.canvas.winfo_rootx()
        y = self.main_app.canvas.winfo_rooty()
        w = self.main_app.canvas.winfo_width()
        h = self.main_app.canvas.winfo_height()
        bbox = (x, y, x + w, y + h)
        img = ImageGrab.grab(bbox)
        
        # Restaurar botões de zoom
        if zoom_visivel and self.zoom_overlay:
            self.zoom_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
        
        return img
    
    def copiar_imagem(self):
        #Copia a imagem do canvas para a área de transferência
        try:
            img = self.capturar_canvas()
            
            # Converter para formato BMP
            output = io.BytesIO()
            img.convert('RGB').save(output, 'BMP')
            data = output.getvalue()[14:]
            output.close()
            
            # Limpar clipboard
            try:
                self.main_app.clipboard_clear()
                self.main_app.update()
            except Exception:
                pass
            
            # Copiar para clipboard (Windows)
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                messagebox.showinfo("Imagem copiada", "A imagem do grafo foi copiada para a área de transferência!")
            except Exception as e:
                messagebox.showerror("Erro ao copiar imagem", f"Erro ao copiar imagem para a área de transferência.\n{e}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao capturar imagem:\n{str(e)}")
    
    def salvar_imagem(self):
        #Salva a imagem do canvas em arquivo
        try:
            # Criar diretório de capturas se não existir
            if not os.path.exists(self.capturas_dir):
                os.makedirs(self.capturas_dir)
            
            # Capturar imagem
            img = self.capturar_canvas()
            
            # Gerar nome do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"grafo_{timestamp}.png"
            caminho_arquivo = os.path.join(self.capturas_dir, nome_arquivo)
            
            # Salvar imagem
            img.save(caminho_arquivo)
            
            # Retornar informações da captura
            return {
                'caminho': caminho_arquivo,
                'nome': nome_arquivo
            }
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar imagem:\n{str(e)}")
            return None