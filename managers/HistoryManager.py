import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

class HistoryManager:
    def __init__(self, canvas, cards_frame, refazer_rota_callback=None):
        self.historico_canvas = canvas
        self.cards_frame = cards_frame
        self.historico_rotas = []
        self.historico_capturas = []
        self.refazer_rota_callback = refazer_rota_callback
    
    def adicionar_rota(self, info_rota):
        info_rota['datahora'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.historico_rotas.append(info_rota)
        self.atualizar_historico()
    
    def adicionar_captura(self, info_captura):
        info_captura['datahora'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.historico_capturas.append(info_captura)
        self.atualizar_historico()
    
    def atualizar_historico(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        historico_completo = []
        for info in self.historico_rotas:
            info['tipo'] = 'rota'
            historico_completo.append(info)
        for info in self.historico_capturas:
            info['tipo'] = 'captura'
            historico_completo.append(info)
        historico_completo.sort(key=lambda x: datetime.strptime(x['datahora'], '%d/%m/%Y %H:%M:%S'), reverse=True)
        for i, info in enumerate(historico_completo, 1):
            card = tk.Frame(self.cards_frame, bg="#262a2f", bd=0, highlightthickness=0)
            card.pack(fill=tk.X, pady=12, padx=0)
            inner = tk.Frame(card, bg="#262a2f")
            inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            if info['tipo'] == 'rota':
                tk.Label(inner, text=f"{len(historico_completo)-i+1}.", bg="#262a2f", fg="#00ffcc", 
                       font=("Segoe UI", 11, "bold"), anchor="w", pady=2).pack(fill=tk.X, padx=0, pady=(0,6))
                info_textos = [
                    ("Origem:", info['origem']),
                    ("Destino:", info['destino']),
                    ("Distância:", f"{info['distancia']:.2f} m"),
                    ("Tempo:", f"{info['tempo']*1000:.2f} ms"),
                    ("Nós explorados:", info['nos_explorados'])
                ]
                for label, valor in info_textos:
                    linha = tk.Frame(inner, bg="#262a2f")
                    linha.pack(fill=tk.X, padx=0, pady=2)
                    tk.Label(linha, text=label, bg="#262a2f", fg="#bbbbbb", 
                           font=("Segoe UI", 9, "bold"), anchor="w").pack(side=tk.LEFT)
                    tk.Label(linha, text=valor, bg="#262a2f", fg="#ffffff", 
                           font=("Segoe UI", 10), anchor="w").pack(side=tk.LEFT, padx=6)
                btn_refazer = tk.Button(inner, text="🔄", bg="#232428", fg="#00ffcc", 
                                     font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2",
                                     command=lambda info=info: self.refazer_rota_callback(info) if self.refazer_rota_callback else None)
                btn_refazer.place(relx=1.0, rely=1.0, anchor='se', x=0, y=-8)
            elif info['tipo'] == 'captura':
                tk.Label(inner, text=f"Captura {len(historico_completo)-i+1}.", 
                       bg="#262a2f", fg="#00ffcc", font=("Segoe UI", 11, "bold"), anchor="w").pack(fill=tk.X, padx=0, pady=(0,6))
                btn_abrir = tk.Button(inner, text="📂", bg="#232428", fg="#00ffcc", 
                                    font=("Segoe UI", 13), bd=0, relief=tk.FLAT, cursor="hand2",
                                    command=lambda info=info: self.abrir_imagem(info))
                btn_abrir.pack(side=tk.RIGHT, pady=4)
        self.historico_canvas.update_idletasks()
        self.historico_canvas.configure(scrollregion=self.historico_canvas.bbox("all"))
    
    def abrir_imagem(self, info):
        import subprocess
        import platform
        try:
            if platform.system() == "Windows":
                os.startfile(info['caminho'])
            elif platform.system() == "Darwin":
                subprocess.run(["open", info['caminho']])
            else:
                subprocess.run(["xdg-open", info['caminho']])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir imagem:\n{str(e)}") 