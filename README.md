<h1 align="center">🐥 Bird Evolution</h1>

<p align="center">
  <b>Junte aves iguais, evolua de Pintinho até a poderosa Harpia e monte o seu bosque!</b>
</p>

<p align="center">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="pygame-ce" src="https://img.shields.io/badge/pygame--ce-2.5-2E8B57">
  <img alt="Versão demo" src="https://img.shields.io/badge/vers%C3%A3o-demo-F28C28">
</p>

<p align="center">
  <img src="docs/menu.png" alt="Menu principal do Bird Evolution" width="48%">
  <img src="docs/jogo.png" alt="Campo de jogo com várias aves" width="48%">
</p>

---

## 🎮 Sobre o jogo

**Bird Evolution** é um jogo de fusão (*merge*) inspirado em *Cow Evolution*: você junta **duas aves do mesmo nível** e elas se transformam em **uma ave mais evoluída**. Cada ave rende moedas com o tempo, e as moedas servem para comprar mais Pintinhos e continuar a cadeia de evolução.

> 🚧 Esta é a **versão demo**: a mecânica principal já está completa e jogável, e novos recursos virão nas próximas versões.

## 🐣 A cadeia de evolução

<p align="center">
  <img src="docs/evolucao.png" alt="Pintinho, Frango, Ganso, Tucano, Avestruz e Harpia" width="100%">
</p>

| Nível | Ave | Moedas por ciclo* |
|:-----:|-----|:-----------------:|
| 1 | Pintinho | 1 |
| 2 | Frango | 3 |
| 3 | Ganso | 8 |
| 4 | Tucano | 20 |
| 5 | Avestruz | 50 |
| 6 | Harpia | 120 |

\* Cada ave paga suas moedas a cada 4 segundos. A **Harpia é o nível máximo** e não se funde com outras.

## 🕹️ Como jogar

1. Clique em **Começar jogo**. Você já começa com 2 Pintinhos e 30 moedas.
2. **Arraste** uma ave com o mouse e solte em cima de outra **do mesmo nível**. Quando elas puderem se fundir, ficam com um brilho amarelo.
3. As duas viram **uma ave do próximo nível**, com direito a efeito de brilho e o som da ave nova.
4. Use as moedas para **comprar mais Pintinhos**. O preço sobe 9% a cada compra.
5. O campo comporta até **14 aves** ao mesmo tempo. Junte as aves para abrir espaço!

## ⌨️ Controles

| Ação | Controle |
|------|----------|
| Pegar e arrastar uma ave | Botão esquerdo do mouse |
| Comprar um Pintinho | Botão verde ou tecla `Espaço` |
| Abrir o menu / voltar | `ESC` |
| Tela cheia | `F11` |
| Ligar/desligar a música | `M` |

Dica: no menu principal, clique nas aves lá embaixo para ouvir o som de cada uma. 🔊

## ⚙️ Configurações

Na tela de **Configurações** você ajusta o volume da música e dos efeitos e liga a tela cheia. Tudo fica salvo em um arquivo `config.json`, criado automaticamente na primeira vez que você mexe nas opções.

<p align="center">
  <img src="docs/configuracoes.png" alt="Tela de configurações" width="48%">
</p>

## 🚀 Como rodar

Você precisa do **Python 3.10 ou superior** e do **Git** instalados.

**Windows (PowerShell):**

```powershell
git clone https://github.com/Gustavoluc11/Bird-Evolution.git
cd Bird-Evolution
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

**Linux / macOS:**

```bash
git clone https://github.com/Gustavoluc11/Bird-Evolution.git
cd Bird-Evolution
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Nas próximas vezes, só o último comando é necessário (dentro da pasta do projeto).

## 📁 Estrutura do projeto

```
Bird-Evolution/
├── main.py                 # Ponto de entrada: controla as telas (menu, jogo, configurações)
├── requirements.txt        # Dependências (pygame-ce)
├── AV/
│   ├── Fundos/             # Cenário do jogo
│   ├── Passaros/           # Aves em PNG com fundo transparente
│   ├── Originais/          # Imagens originais (antes do recorte)
│   └── Sons/               # Efeito de cada ave, som de fusão e música
├── Codigo/
│   ├── jogo.py             # Regras: comprar, arrastar, fundir, moedas e HUD
│   ├── passaro.py          # Classe Passaro (nível, animações, colisão)
│   ├── menu.py             # Menu principal e tela de configurações
│   ├── audio.py            # Música de fundo e efeitos sonoros
│   ├── config.py           # Leitura e gravação do config.json
│   ├── ui.py               # Botões, painéis e placa de madeira
│   └── cursor.py           # Cursor de mãozinha
├── Ferramentas/
│   └── gerar_sons.py       # Gera os sons e a música por síntese
└── docs/                   # Imagens usadas neste README
```

## 🛠️ Personalizando

- **Equilíbrio do jogo:** em `Codigo/jogo.py` ficam `MOEDAS_INICIAIS`, `CUSTO_BASE`, `CRESCIMENTO_CUSTO` e `MAX_AVES`. Em `Codigo/passaro.py` ficam `RENDA`, `TEMPO_RENDA` e `ALTURAS`.
- **Trocar os sons:** coloque arquivos `.wav`, `.ogg` ou `.mp3` em `AV/Sons/` com o **mesmo nome** dos atuais (`Pintinho`, `Frango`, `Ganso`, `Tucano`, `Avestruz`, `Harpia`, `fundir` e `musica`). Nenhuma mudança no código é necessária.
- **Regerar os sons sintetizados:** `pip install numpy scipy` e depois `python Ferramentas/gerar_sons.py`.

## 🗺️ Próximos passos

- [x] Fusão de aves em 6 níveis
- [x] Economia com moedas e compra de Pintinhos
- [x] Música e som para cada ave
- [x] Menu principal, configurações e tela cheia
- [ ] Salvar o progresso do jogo
- [ ] Vender aves para liberar espaço
- [ ] Upgrades (mais espaço, mais renda, compras mais baratas)
- [ ] Ovos que chocam em vez de compra direta
- [ ] Novos níveis depois da Harpia
- [ ] Loja e Coleção (versão completa)

## 👤 Créditos

Criado por **Gustavo Gomes** ([@Gustavoluc11](https://github.com/Gustavoluc11)).

Os efeitos sonoros e a música foram sintetizados por código (veja `Ferramentas/gerar_sons.py`).
