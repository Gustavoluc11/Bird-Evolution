"""
Gera os sons do Bird Evolution por síntese (sem precisar de arquivos de áudio).

Uso (opcional, os sons já vêm prontos em AV/Sons):
    pip install numpy scipy
    python Ferramentas/gerar_sons.py

Para usar áudios reais, basta colocar arquivos com os MESMOS NOMES em AV/Sons
(Pintinho.wav, Frango.wav, ..., fundir.wav, musica.ogg / musica.wav / musica.mp3).
"""
import subprocess
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
PASTA = Path(__file__).resolve().parent.parent / "AV" / "Sons"
rng = np.random.default_rng(7)


# ----------------------------------------------------------------------
# Ferramentas básicas
# ----------------------------------------------------------------------
def t_(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def passa_baixa(x, corte, sr=SR, ordem=2):
    b, a = butter(ordem, corte / (sr / 2), "low")
    return lfilter(b, a, x)


def passa_alta(x, corte, sr=SR, ordem=2):
    b, a = butter(ordem, corte / (sr / 2), "high")
    return lfilter(b, a, x)


def oscilador(freq, harmonicos, sr=SR):
    """freq: array com a frequência em cada instante (permite deslizar a nota)."""
    fase = 2 * np.pi * np.cumsum(freq) / sr
    sinal = np.zeros_like(freq)
    for n, amp in enumerate(harmonicos, start=1):
        sinal += amp * np.sin(n * fase)
    return sinal


def envelope(n, ataque=0.005, decaimento=6.0, sr=SR):
    t = np.arange(n) / sr
    env = np.exp(-t * decaimento)
    a = max(1, int(ataque * sr))
    env[:a] *= np.linspace(0, 1, a)
    return env


def glide(inicio, fim, n, curva=1.0):
    return inicio + (fim - inicio) * np.linspace(0, 1, n) ** curva


def normalizar(x, pico=0.85):
    return x / (np.max(np.abs(x)) + 1e-9) * pico


def colocar(destino, trecho, inicio_seg, sr=SR):
    i = int(inicio_seg * sr)
    fim = min(len(destino), i + len(trecho))
    destino[i:fim] += trecho[: fim - i]


def salvar_wav(caminho, x, sr=SR):
    dados = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(dados.tobytes())


# ----------------------------------------------------------------------
# Um som para cada ave
# ----------------------------------------------------------------------
def pintinho():
    """'piu piu piu': três pios agudos."""
    s = np.zeros(int(0.55 * SR))
    for i, (f0, f1) in enumerate([(3000, 4100), (3200, 4300), (3400, 4600)]):
        n = int(0.085 * SR)
        f = glide(f0, f1, n, 0.6) * (1 + 0.02 * np.sin(2 * np.pi * 40 * t_(0.085)))
        pio = oscilador(f, [1, 0.25]) * envelope(n, 0.004, 22)
        colocar(s, pio, 0.02 + i * 0.15)
    return normalizar(s)


def frango():
    """'có có có': cacarejo grave e curtinho."""
    s = np.zeros(int(0.7 * SR))
    for i in range(3):
        n = int(0.09 * SR)
        f = glide(520, 260, n, 0.7)
        voz = oscilador(f, [1, 0.7, 0.5, 0.3, 0.2])
        voz = passa_baixa(voz, 1800) * envelope(n, 0.006, 20)
        voz += 0.15 * passa_alta(rng.standard_normal(n), 2000) * envelope(n, 0.002, 60)
        colocar(s, voz, 0.03 + i * 0.17)
    return normalizar(s)


def ganso():
    """'hôonk': buzina anasalada."""
    n = int(0.55 * SR)
    t = t_(0.55)
    f = np.interp(t, [0, 0.08, 0.35, 0.55], [300, 430, 390, 300])
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 7 * t))
    voz = oscilador(f, [1, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25])
    voz *= 1 + 0.35 * np.sin(2 * np.pi * 70 * t)  # aspereza
    voz = passa_baixa(voz, 2600)
    env = np.minimum(1, t / 0.04) * np.exp(-np.maximum(0, t - 0.3) * 7)
    return normalizar(voz * env)


def tucano():
    """Coaxar grave e pulsado, como o tucano de verdade."""
    n = int(0.65 * SR)
    t = t_(0.65)
    f = np.interp(t, [0, 0.15, 0.5, 0.65], [140, 210, 190, 130])
    voz = oscilador(f, [1, 0.9, 0.8, 0.6, 0.5, 0.3, 0.2])
    pulso = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 26 * t)) * np.abs(np.sin(2 * np.pi * 26 * t)) ** 0.5
    voz = passa_baixa(voz * pulso, 1700)
    env = np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - 0.4) * 9)
    return normalizar(voz * env)


def avestruz():
    """'buum buum': estrondo grave."""
    s = np.zeros(int(0.95 * SR))
    for i in range(2):
        n = int(0.38 * SR)
        t = t_(0.38)
        f = glide(125, 95, n, 0.8) * (1 + 0.015 * np.sin(2 * np.pi * 9 * t))
        voz = oscilador(f, [1, 0.6, 0.35, 0.15])
        voz = passa_baixa(voz, 900)
        env = np.minimum(1, t / 0.07) * np.exp(-np.maximum(0, t - 0.1) * 6)
        colocar(s, voz * env, 0.04 + i * 0.42)
    return normalizar(s)


def harpia():
    """Grito agudo de rapina, descendo."""
    n = int(0.9 * SR)
    t = t_(0.9)
    f = np.interp(t, [0, 0.05, 0.35, 0.9], [1900, 2700, 2300, 1300])
    f = f * (1 + 0.025 * np.sin(2 * np.pi * 14 * t))
    voz = oscilador(f, [1, 0.5, 0.35, 0.2, 0.1])
    ruido = passa_alta(rng.standard_normal(n), 1500) * 0.12
    voz = (voz + ruido) * (1 + 0.25 * np.sin(2 * np.pi * 55 * t))
    env = np.minimum(1, t / 0.015) * np.exp(-np.maximum(0, t - 0.25) * 4.5)
    return normalizar(voz * env)


def fundir():
    """Brilhinho ascendente para a fusão."""
    s = np.zeros(int(0.5 * SR))
    for i, nota in enumerate([523.25, 659.25, 783.99, 1046.5]):
        n = int(0.28 * SR)
        f = np.full(n, nota)
        som = oscilador(f, [1, 0.3, 0.1]) * envelope(n, 0.004, 9)
        colocar(s, som, i * 0.055)
    return normalizar(s, 0.6)


# ----------------------------------------------------------------------
# Música: loop alegre de "fazenda" (Dó maior)
# ----------------------------------------------------------------------
def freq_nota(nome):
    notas = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    oitava = int(nome[-1])
    semitons = notas[nome[0]] + (1 if "#" in nome else 0)
    return 440.0 * 2 ** ((semitons - 9 + 12 * (oitava - 4)) / 12)


def pluck(freq, dur, sr, decaimento=5.5, brilho=0.35):
    t = np.arange(int(dur * sr)) / sr
    f = np.full(len(t), freq)
    s = oscilador(f, [1, brilho, brilho * 0.4], sr)
    return s * envelope(len(t), 0.004, decaimento, sr)


def musica(sr=22050, bpm=112):
    colcheia = 60 / bpm / 2
    compassos_total = 16
    n_loop = int(compassos_total * 8 * colcheia * sr)
    cauda = int(2.0 * sr)
    buf = np.zeros(n_loop + cauda)

    acordes = {
        "C": (["C3"], ["C4", "E4", "G4"]),
        "Am": (["A2"], ["A3", "C4", "E4"]),
        "F": (["F2"], ["F3", "A3", "C4"]),
        "G": (["G2"], ["G3", "B3", "D4"]),
    }
    progressao = ["C", "Am", "F", "G"] * 4

    # melodia: (nota, duração em colcheias); None = pausa
    A = [
        [("E5", 2), ("G5", 1), ("E5", 1), ("C5", 2), ("E5", 2)],
        [("C5", 2), ("E5", 2), ("A4", 2), ("C5", 2)],
        [("A4", 2), ("C5", 2), ("F5", 2), ("E5", 2)],
        [("D5", 2), ("B4", 2), ("D5", 2), (None, 2)],
    ]
    B = [
        [("E5", 2), ("G5", 2), ("C6", 2), ("G5", 2)],
        [("E5", 2), ("A5", 2), ("G5", 2), ("E5", 2)],
        [("F5", 2), ("A5", 2), ("G5", 2), ("F5", 2)],
        [("E5", 1), ("D5", 1), ("D5", 2), ("G4", 4)],
    ]
    melodia = A + B + A + B

    for c, (compasso, acorde) in enumerate(zip(melodia, progressao)):
        base = c * 8 * colcheia
        baixo, acorde_notas = acordes[acorde]

        # baixo nos tempos 1 e 3
        for tempo in (0, 4):
            som = pluck(freq_nota(baixo[0]), 0.5, sr, 4.5, 0.2) * 0.55
            colocar(buf, som, base + tempo * colcheia, sr)

        # acorde nos tempos 2 e 4 ("pum-tchá")
        for tempo in (2, 6):
            for nota in acorde_notas:
                som = pluck(freq_nota(nota), 0.35, sr, 8, 0.15) * 0.17
                colocar(buf, som, base + tempo * colcheia, sr)

        # chocalho suave nas contratempos
        for tempo in (1, 3, 5, 7):
            n = int(0.04 * sr)
            tss = passa_alta(rng.standard_normal(n), 5000, sr) * envelope(n, 0.001, 70, sr) * 0.05
            colocar(buf, tss, base + tempo * colcheia, sr)

        # melodia
        pos = 0
        for nota, dur in compasso:
            if nota:
                # a segunda volta (compassos 8 a 15) soa um pouco mais brilhante
                brilho = 0.5 if c >= 8 else 0.3
                som = pluck(freq_nota(nota), dur * colcheia + 0.5, sr, 4.2, brilho) * 0.45
                colocar(buf, som, base + pos * colcheia, sr)
            pos += dur

    # une a "cauda" com o começo para o loop não ter corte
    buf[: cauda] += buf[n_loop: n_loop + cauda]
    loop = buf[:n_loop]
    return normalizar(loop, 0.7), sr


# ----------------------------------------------------------------------
def main():
    PASTA.mkdir(parents=True, exist_ok=True)

    efeitos = {
        "Pintinho": pintinho,
        "Frango": frango,
        "Ganso": ganso,
        "Tucano": tucano,
        "Avestruz": avestruz,
        "Harpia": harpia,
        "fundir": fundir,
    }
    for nome, fn in efeitos.items():
        salvar_wav(PASTA / f"{nome}.wav", fn())
        print("ok", nome)

    loop, sr = musica()
    wav = PASTA / "musica.wav"
    salvar_wav(wav, loop, sr)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
             "-c:a", "libvorbis", "-q:a", "4", str(PASTA / "musica.ogg")],
            check=True,
        )
        wav.unlink()
        print("ok musica.ogg")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ok musica.wav (sem ffmpeg para converter em .ogg)")


if __name__ == "__main__":
    main()
