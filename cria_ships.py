from PIL import Image, ImageDraw
import os

ships = [
    ("player.png", (50, 50), (80, 220, 100)),
    ("EnemyEasy.png", (40, 40), (220, 80, 80)),
    ("EnemyMedium.png", (55, 55), (220, 180, 80)),
    ("EnemyHard.png", (75, 75), (120, 80, 220)),
]

os.makedirs("src/assets/ships", exist_ok=True)

for name, size, color in ships:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Desenha um triângulo simples para cada nave
    w, h = size
    draw.polygon([(w//2, 5), (w-5, h-5), (5, h-5)], fill=color)
    img.save(f"src/assets/ships/{name}")
print("Imagens de nave criadas!")
