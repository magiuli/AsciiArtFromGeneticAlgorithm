from PIL import Image, ImageDraw, ImageFont
import numpy as np

def get_luminance(char: str, font: ImageFont.FreeTypeFont, size: tuple[int, int]) -> float:
    image = Image.new('L', size, color=0)
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), char, font=font)
    x = (size[0] - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = (size[1] - (bbox[3] - bbox[1])) // 2 - bbox[1]
    draw.text((x, y), char, fill=255, font=font)
    arr = np.array(image, dtype=np.uint8)
    return arr.mean()

# Set de caractere (poți schimba dacă vrei)
characters = list(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""")

# Parametri imagine
block_size = (16, 16)

# Încarcă fontul (poți schimba cu calea completă dacă nu merge implicit)
try:
    font = ImageFont.truetype("DejaVuSansMono.ttf", size=16)
except:
    font = ImageFont.load_default()

# Calculează luminozitatea pentru fiecare caracter
char_luminance = [(char, get_luminance(char, font, block_size)) for char in characters]

# Sortează după luminozitate crescătoare (întunecat ➜ luminos)
sorted_chars = sorted(char_luminance, key=lambda x: x[1])

# Afișează rezultatul
sorted_string = ''.join(char for char, lum in sorted_chars)
print("Caractere ordonate dupa luminozitate:")
print(sorted_string)
