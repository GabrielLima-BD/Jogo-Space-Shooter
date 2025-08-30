import os
import sys

# Lista de arquivos obrigatórios para o jogo rodar

REQUIRED_FILES = [
    'src/assets/ships/player.png',
    'src/assets/ships/EnemyEasy.png',
    'src/assets/ships/EnemyMedium.png',
    'src/assets/ships/EnemyHard.png',
]

REQUIRED_SOUNDS = [
    'src/assets/sounds/gunplayer',
    'src/assets/sounds/deadplayer',
    'src/assets/sounds/deadenemy',
    'src/assets/sounds/gamestart',
    'src/assets/sounds/musicgame',
]

missing = [f for f in REQUIRED_FILES if not os.path.exists(f)]
for base in REQUIRED_SOUNDS:
    if not (os.path.exists(base + '.mp3') or os.path.exists(base + '.wav')):
        missing.append(base + '.mp3 ou .wav')

missing = [f for f in REQUIRED_FILES if not os.path.exists(f)]

if missing:
    print('ATENÇÃO: Os seguintes arquivos estão faltando:')
    for f in missing:
        print(' -', f)
    print('\nO jogo não funcionará corretamente sem esses arquivos.')
    sys.exit(1)
else:
    print('Todos os arquivos essenciais estão presentes.')
