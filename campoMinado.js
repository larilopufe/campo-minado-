const tamanho = 5;
const totalMinas = 5;
let tabuleiro = [];
let jogoEncerrado = false;
let bandeirasUsadas = 0;

// Efeitos sonoros
const somClique = new Audio('./mp3/click.mp3');
const somBandeira = new Audio('./mp3/flag.mp3');
const somExplosao = new Audio('./mp3/explosion.mp3');
const somDerrota = new Audio('./mp3/gameover.mp3');
const somVitoria = new Audio('./mp3/win.mp3');

function tocarSom(som) {
  som.currentTime = 0;
  som.play().catch(() => {});
}

// Referências
const telaMenu     = document.getElementById('tela-menu');
const telaJogo     = document.getElementById('tela-jogo');
const telaDerrota  = document.getElementById('tela-derrota');
const telaVitoria  = document.getElementById('tela-vitoria');
const gradeEl      = document.getElementById('tabuleiro');
const contadorEl   = document.getElementById('contador-bandeiras');

function mostrarTela(tela) {
  [telaMenu, telaJogo, telaDerrota, telaVitoria].forEach(t => t.classList.remove('ativa'));
  tela.classList.add('ativa');
}

function iniciarJogo() {
  mostrarTela(telaJogo);
  criarTabuleiro();
  atualizarContador();
}

function voltarMenu() {
  mostrarTela(telaMenu);
}

function sairJogo() {
  window.close();
}

function criarTabuleiro() {
  tabuleiro = [];
  jogoEncerrado = false;
  bandeirasUsadas = 0;
  gradeEl.innerHTML = '';

  const posicoes = [];

  while (posicoes.length < totalMinas) {
    const r = Math.floor(Math.random() * tamanho);
    const c = Math.floor(Math.random() * tamanho);
    if (!posicoes.some(p => p[0] === r && p[1] === c)) {
      posicoes.push([r, c]);
    }
  }

  for (let l = 0; l < tamanho; l++) {
    tabuleiro[l] = [];
    for (let c = 0; c < tamanho; c++) {
      const celula = {
        revelada: false,
        temMina: false,
        bandeira: false,
        elemento: document.createElement('div')
      };

      celula.elemento.className = 'celula';
      celula.elemento.addEventListener('click', () => clicarCelula(l, c));
      celula.elemento.addEventListener('contextmenu', e => {
        e.preventDefault();
        toggleBandeira(l, c);
      });

      gradeEl.appendChild(celula.elemento);
      tabuleiro[l][c] = celula;
    }
  }

  posicoes.forEach(([l, c]) => {
    tabuleiro[l][c].temMina = true;
    tabuleiro[l][c].elemento.classList.add('mina-suave');
  });
}

function atualizarContador() {
  const restantes = totalMinas - bandeirasUsadas;
  contadorEl.textContent = restantes.toString().padStart(2, '0');
}

function toggleBandeira(l, c) {
  const cel = tabuleiro[l][c];
  if (jogoEncerrado || cel.revelada) return;

  if (!cel.bandeira && bandeirasUsadas < totalMinas) {
    cel.bandeira = true;
    cel.elemento.classList.add('bandeira');
    bandeirasUsadas++;
  } else if (cel.bandeira) {
    cel.bandeira = false;
    cel.elemento.classList.remove('bandeira');
    bandeirasUsadas--;
  }

  tocarSom(somBandeira);
  atualizarContador();
}

function clicarCelula(l, c) {
  const cel = tabuleiro[l][c];
  if (jogoEncerrado || cel.revelada || cel.bandeira) return;

  cel.revelada = true;
  cel.elemento.classList.add('revelada');

  if (cel.temMina) {
    cel.elemento.textContent = '💣';
    cel.elemento.classList.add('explodida');
    tocarSom(somExplosao);
    setTimeout(() => {
      explodirBombasSequencialmente(() => encerrarJogo(false));
    }, 100);
  } else {
    const n = contarMinasVizinhas(l, c);
    if (n > 0) {
      cel.elemento.textContent = n;
    } else {
      revelarVizinhos(l, c);
    }
    tocarSom(somClique);
    verificarVitoria();
  }
}

function contarMinasVizinhas(l, c) {
  let cont = 0;
  for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
      const nl = l + i, nc = c + j;
      if (nl >= 0 && nl < tamanho && nc >= 0 && nc < tamanho && tabuleiro[nl][nc].temMina) {
        cont++;
      }
    }
  }
  return cont;
}

function revelarVizinhos(l, c) {
  for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
      const nl = l + i, nc = c + j;
      if (nl >= 0 && nl < tamanho && nc >= 0 && nc < tamanho && !tabuleiro[nl][nc].revelada) {
        clicarCelula(nl, nc);
      }
    }
  }
}

function explodirBombasSequencialmente(callback) {
  const minas = [];
  for (let i = 0; i < tamanho; i++) {
    for (let j = 0; j < tamanho; j++) {
      if (tabuleiro[i][j].temMina) minas.push(tabuleiro[i][j]);
    }
  }

  let idx = 0;
  function explodirProxima() {
    if (idx >= minas.length) {
      callback();
      return;
    }
    const cel = minas[idx];
    cel.elemento.textContent = '💣';
    cel.elemento.classList.add('explodida');
    idx++;
    setTimeout(explodirProxima, 150);
  }
  explodirProxima();
}

function encerrarJogo(venceu) {
  jogoEncerrado = true;
  if (venceu) {
    tocarSom(somVitoria);
    mostrarTela(telaVitoria);
  } else {
    tocarSom(somDerrota);
    mostrarTela(telaDerrota);
    for (let i = 0; i < tamanho; i++) {
      for (let j = 0; j < tamanho; j++) {
        const cel = tabuleiro[i][j];
        if (cel.temMina) {
          cel.elemento.classList.remove('bandeira');
        }
      }
    }
  }
}

function verificarVitoria() {
  let seguras = 0;
  for (let i = 0; i < tamanho; i++) {
    for (let j = 0; j < tamanho; j++) {
      const cel = tabuleiro[i][j];
      if (!cel.temMina && cel.revelada) seguras++;
    }
  }
  if (seguras === tamanho * tamanho - totalMinas) {
    encerrarJogo(true);
  }
}

mostrarTela(telaMenu);
