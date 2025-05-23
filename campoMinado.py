import tkinter as tk
from tkinter import messagebox
import random
import time

class CampoMinado:
    def __init__(self, master):
        self.master = master
        master.title("Campo Minado - ADS")

        # Dificuldades: (linhas, colunas, minas)
        self.niveis = {
            "Fácil": (8, 10, 10),
            "Médio": (14, 18, 40),
            "Difícil": (20, 24, 99)
        }
        self.nivel_atual = "Médio"

        # Variáveis do jogo
        self.linhas = 0
        self.colunas = 0
        self.num_minas = 0

        self.minas = []
        self.valores = []
        self.botoes = []
        self.bandeiras_restantes = 0
        self.jogo_iniciado = False
        self.jogo_terminado = False

        self.tempo_inicial = None
        self.tempo_label = None
        self.timer_id = None

        self.create_widgets()
        self.iniciar_jogo(self.nivel_atual)

    def create_widgets(self):
        # Frame topo (menu e infos)
        topo_frame = tk.Frame(self.master)
        topo_frame.pack(pady=5)

        # Menu de seleção de nível
        self.nivel_var = tk.StringVar(value=self.nivel_atual)
        nivel_menu = tk.OptionMenu(topo_frame, self.nivel_var, *self.niveis.keys(), command=self.mudar_nivel)
        nivel_menu.pack(side=tk.LEFT, padx=10)

        # Label bandeiras restantes
        self.bandeiras_label = tk.Label(topo_frame, text="Bandeiras: 0")
        self.bandeiras_label.pack(side=tk.LEFT, padx=10)

        # Label cronômetro
        self.tempo_label = tk.Label(topo_frame, text="Tempo: 0s")
        self.tempo_label.pack(side=tk.LEFT, padx=10)

        # Botão reiniciar
        reiniciar_btn = tk.Button(topo_frame, text="Reiniciar", command=self.reiniciar_jogo)
        reiniciar_btn.pack(side=tk.LEFT, padx=10)

        # Frame do tabuleiro
        self.frame_tabuleiro = tk.Frame(self.master)
        self.frame_tabuleiro.pack()

    def mudar_nivel(self, valor):
        if self.jogo_terminado or not self.jogo_iniciado:
            self.nivel_atual = valor
            self.iniciar_jogo(valor)
        else:
            if messagebox.askyesno("Confirmar", "Jogo em andamento. Deseja reiniciar e mudar o nível?"):
                self.nivel_atual = valor
                self.iniciar_jogo(valor)
            else:
                # voltar menu para nível atual
                self.nivel_var.set(self.nivel_atual)

    def iniciar_jogo(self, nivel):
        self.linhas, self.colunas, self.num_minas = self.niveis[nivel]
        self.bandeiras_restantes = self.num_minas
        self.jogo_iniciado = False
        self.jogo_terminado = False
        self.tempo_inicial = None
        self.tempo_label.config(text="Tempo: 0s")
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        # Limpar frame e listas
        for widget in self.frame_tabuleiro.winfo_children():
            widget.destroy()
        self.minas = [[False]*self.colunas for _ in range(self.linhas)]
        self.valores = [[0]*self.colunas for _ in range(self.linhas)]
        self.botoes = []

        # Criar botões
        for i in range(self.linhas):
            linha_botoes = []
            for j in range(self.colunas):
                botao = tk.Button(self.frame_tabuleiro, text=" ", width=2, height=1,
                                  command=lambda i=i, j=j: self.clicar_celula(i,j))
                botao.bind("<Button-3>", lambda e, i=i, j=j: self.alternar_bandeira(i,j))
                botao.grid(row=i, column=j)
                linha_botoes.append(botao)
            self.botoes.append(linha_botoes)

        self.atualizar_bandeiras_label()

    def colocar_minas(self, primeira_linha, primeira_coluna):
        # Posicoes proibidas: primeira célula clicada + vizinhos
        proibidas = set()
        for x in range(primeira_linha-1, primeira_linha+2):
            for y in range(primeira_coluna-1, primeira_coluna+2):
                if 0 <= x < self.linhas and 0 <= y < self.colunas:
                    proibidas.add((x,y))

        todas_posicoes = [(i,j) for i in range(self.linhas) for j in range(self.colunas)]
        posicoes_possiveis = [p for p in todas_posicoes if p not in proibidas]

        minas_pos = random.sample(posicoes_possiveis, self.num_minas)
        for (x,y) in minas_pos:
            self.minas[x][y] = True

        # Calcular valores de vizinhos
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.minas[i][j]:
                    continue
                cont = 0
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:
                        nx, ny = i+dx, j+dy
                        if 0 <= nx < self.linhas and 0 <= ny < self.colunas:
                            if self.minas[nx][ny]:
                                cont += 1
                self.valores[i][j] = cont

    def clicar_celula(self, linha, coluna):
        if self.jogo_terminado:
            return
        botao = self.botoes[linha][coluna]
        if botao["state"] == "disabled" or botao["text"] == "🚩":
            return

        if not self.jogo_iniciado:
            self.colocar_minas(linha, coluna)
            self.jogo_iniciado = True
            self.iniciar_cronometro()

        if self.minas[linha][coluna]:
            botao.config(text="💣", bg="red", state="disabled")
            self.revelar_todas_minas()
            self.terminar_jogo(False)
        else:
            self.revelar_celulas_vizinhas(linha, coluna)
            if self.verificar_vitoria():
                self.terminar_jogo(True)

    def revelar_celulas_vizinhas(self, linha, coluna):
        if not (0 <= linha < self.linhas and 0 <= coluna < self.colunas):
            return
        botao = self.botoes[linha][coluna]
        if botao["state"] == "disabled" or botao["text"] == "🚩":
            return

        numero = self.valores[linha][coluna]
        botao.config(text=str(numero) if numero > 0 else " ", bg="lightgray", state="disabled")

        if numero == 0:
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    if dx != 0 or dy != 0:
                        self.revelar_celulas_vizinhas(linha+dx, coluna+dy)

    def alternar_bandeira(self, linha, coluna):
        if self.jogo_terminado:
            return
        botao = self.botoes[linha][coluna]
        if botao["state"] == "normal":
            if botao["text"] == "🚩":
                botao.config(text=" ")
                self.bandeiras_restantes += 1
            else:
                if self.bandeiras_restantes > 0:
                    botao.config(text="🚩")
                    self.bandeiras_restantes -= 1
            self.atualizar_bandeiras_label()

    def atualizar_bandeiras_label(self):
        self.bandeiras_label.config(text=f"Bandeiras: {self.bandeiras_restantes}")

    def revelar_todas_minas(self):
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.minas[i][j]:
                    botao = self.botoes[i][j]
                    if botao["text"] != "🚩":
                        botao.config(text="💣", bg="red", state="disabled")

    def verificar_vitoria(self):
        # Vitória: todas as células que não são minas estão reveladas
        for i in range(self.linhas):
            for j in range(self.colunas):
                botao = self.botoes[i][j]
                if not self.minas[i][j] and botao["state"] != "disabled":
                    return False
        return True

    def terminar_jogo(self, venceu):
        self.jogo_terminado = True
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        if venceu:
            messagebox.showinfo("Parabéns!", f"Você venceu em {int(time.time() - self.tempo_inicial)} segundos! 🎉")
        else:
            messagebox.showinfo("Fim de Jogo", "Você clicou em uma mina! 💥")

    def reiniciar_jogo(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None
        self.iniciar_jogo(self.nivel_atual)

    def iniciar_cronometro(self):
        self.tempo_inicial = time.time()
        self.atualizar_cronometro()

    def atualizar_cronometro(self):
        if self.jogo_terminado:
            return
        tempo_passado = int(time.time() - self.tempo_inicial)
        self.tempo_label.config(text=f"Tempo: {tempo_passado}s")
        self.timer_id = self.master.after(1000, self.atualizar_cronometro)

if __name__ == "__main__":
    root = tk.Tk()
    jogo = CampoMinado(root)
    root.mainloop()
