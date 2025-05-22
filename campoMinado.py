import tkinter as tk
from tkinter import messagebox
import random

LINHAS = 5
COLUNAS = 5
NUM_MINAS = 5

botoes = []
minas = []
valores = []

def gerar_minas():
    global minas, valores
    minas = [[False for _ in range(COLUNAS)] for _ in range(LINHAS)]
    valores = [[0 for _ in range(COLUNAS)] for _ in range(LINHAS)]
    
    # Sortear posições das minas
    posicoes = random.sample(range(LINHAS * COLUNAS), NUM_MINAS)
    for pos in posicoes:
        linha = pos // COLUNAS
        coluna = pos % COLUNAS
        minas[linha][coluna] = True

    # Calcular número de minas ao redor de cada célula
    for i in range(LINHAS):
        for j in range(COLUNAS):
            if minas[i][j]:
                continue
            cont = 0
            for x in range(i-1, i+2):
                for y in range(j-1, j+2):
                    if 0 <= x < LINHAS and 0 <= y < COLUNAS:
                        if minas[x][y]:
                            cont += 1
            valores[i][j] = cont

def clicar_celula(linha, coluna):
    botao = botoes[linha][coluna]
    if minas[linha][coluna]:
        botao.config(text="💣", bg="red", state="disabled")
        revelar_todas_minas()
        messagebox.showinfo("Fim de Jogo", "Você clicou em uma mina! 💥")
    else:
        numero = valores[linha][coluna]
        botao.config(text=str(numero), bg="lightgray", state="disabled")

def revelar_todas_minas():
    for i in range(LINHAS):
        for j in range(COLUNAS):
            if minas[i][j]:
                botoes[i][j].config(text="💣", bg="red", state="disabled")

def reiniciar_jogo():
    for i in range(LINHAS):
        for j in range(COLUNAS):
            botoes[i][j].config(text=" ", bg="SystemButtonFace", state="normal")
    gerar_minas()

# Criar janela principal
janela = tk.Tk()
janela.title("Campo Minado - ADS")

# Criar frame do tabuleiro
frame = tk.Frame(janela)
frame.pack(padx=10, pady=10)

# Criar matriz de botões
for i in range(LINHAS):
    linha_botoes = []
    for j in range(COLUNAS):
        botao = tk.Button(frame, text=" ", width=4, height=2,
                          command=lambda i=i, j=j: clicar_celula(i, j))
        botao.grid(row=i, column=j)
        linha_botoes.append(botao)
    botoes.append(linha_botoes)

# Botão de reiniciar
btn_reiniciar = tk.Button(janela, text="🔁 Reiniciar", command=reiniciar_jogo)
btn_reiniciar.pack(pady=5)

# Inicializar minas
gerar_minas()

# Rodar a janela
janela.mainloop()
