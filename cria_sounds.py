import wave
import struct
import os

def make_beep(filename, freq=440, duration_ms=200, volume=0.5):
    framerate = 44100
    nframes = int(duration_ms * framerate / 1000)
    amp = int(volume * 32767)
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for i in range(nframes):
            value = int(amp * (i % (framerate // freq) < (framerate // freq) // 2))
            data = struct.pack('<h', value)
            wf.writeframesraw(data)

os.makedirs('src/assets/sounds', exist_ok=True)

# Sons simples para cada evento
eventos = [
    ("gunplayer.wav", 880, 80),
    ("deadplayer.wav", 220, 300),
    ("deadenemy.wav", 440, 120),
    ("gamestart.wav", 660, 200),
    ("musicgame.wav", 330, 1000),
]

for nome, freq, dur in eventos:
    make_beep(f"src/assets/sounds/{nome}", freq, dur)
print("Sons de placeholder criados!")
