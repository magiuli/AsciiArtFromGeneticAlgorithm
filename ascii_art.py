import os
import logging
from typing import List
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Configurare logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def image_zone_to_character_similarity(image: Image.Image, character_image: Image.Image) -> float:
    """
    Calculeaza similaritatea dintre o portiune din imagine si imaginea unui caracter."""
    if image.size != character_image.size:
        logging.error(
            "Dimensiunile imaginilor nu se potrivesc pentru comparatie.")
        return 0.0

    # Convertim imaginile in array-uri numpy pentru comparatie
    image_array = np.array(image)
    character_array = np.array(character_image)

    # Calculam similaritatea folosind SSIM
    similarity = ssim(image_array, character_array,
                      data_range=image_array.max() - image_array.min())

    return similarity


def finess_function(image: Image.Image, ascii_image: List[List[str]], ascii_characters_images: dict[str, Image.Image], block_size: tuple[int, int]) -> float:
    """
    Evaluează similitudinea dintre imaginea originală și imaginea ASCII generată.
    """
    pass



def render_character(character: str, block_size: tuple[int, int], font: str = "arial.ttf") -> Image.Image:
    """
    Randează un caracter ASCII într-o imagine de dimensiuni specificate.
    """
    width, height = block_size
    # Creăm o imagine goală cu fundal negru
    image = Image.new('L', (width, height), color=0)

    try:
        # Încercăm să încărcăm fontul specificat
        font = ImageFont.truetype(font, size=min(width, height)*1.40)
    except IOError:
        logging.warning(
            f"Fontul '{font}' nu a putut fi gasit. Se va folosi fontul implicit.")
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(image)

    # Obținem “bounding box” al caracterului la poziția 0,0
    # textbbox returnează tuple (left, top, right, bottom)
    bbox = draw.textbbox((0, 0), character, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculăm coordonatele pentru centrare
    x = (width - text_width) // 2 - bbox[0]
    y = (height - text_height) // 2 - bbox[1]

    draw.text((x, y), character, fill=255, font=font)

    return image


def get_ascii_characters(source: str = os.path.join("input", "characters.txt")) -> List[str]:
    """
    Obține caracterele ASCII dintr-un fișier text.
    Fișierul ar trebui să conțină câte un caracter pe fiecare linie.
    """
    try:
        with open(source, 'r', encoding='utf-8') as file:
            # Citim doar prima linie din fișier și extragem caracterele
            # Eliminam duplicatele
            characters = list(dict.fromkeys(file.readline().strip()))
            if not characters:
                logging.warning(
                    "Fisierul de caractere este gol sau nu contine caractere valide.")
                return []

            return characters

    except FileNotFoundError:
        logging.error(f"Fisierul de caractere '{source}' nu a fost gasit.")
        return []
    except Exception as e:
        logging.error(
            f"A aparut o eroare la citirea fisierului de caractere: {e}")
        return []


def preprocess_image(image_path: str, block_size: tuple[int, int]) -> Image.Image | None:
    """
    Procesăm imaginea pentru a putea fi convertită in ASCII art.
    Funcția încarcă imaginea, se asigură că este în format grayscale, iar la nevoie o trunchiază și o redimensionează.
    """
    try:
        with Image.open(image_path) as image:
            # Convertirea imamginii la grayscale
            if image.mode != 'L':
                logging.info("Se converteste imaginea la grayscale...")
                image = image.convert('L')

            # Trunchierea imaginea, astfel incat latimea sa fie un multiplu de block_size[0], iar inaltimea sa fie un multiplu de block_size[1]
            width, height = image.size
            new_width = (width // block_size[0]) * block_size[0]
            new_height = (height // block_size[1]) * block_size[1]

            if new_width != width or new_height != height:
                logging.info(
                    f"Redimensionam imaginea de la ({width}, {height}) la ({new_width}, {new_height}).")
                image = image.resize((new_width, new_height))

            return image

    except FileNotFoundError:
        logging.error(f"Image not found: {image_path}")
        return None
    except UnidentifiedImageError:
        logging.error(
            f"Fisierul de la calea '{image_path}' nu a putut fi identificat ca o imagine valida.")
        return None
    except Exception as e:
        logging.error(f"A aparut o eroare la procesarea imaginii: {e}")
        return None




if __name__ == "__main__":
    # Un caracter va corespunde unei zone de 50x50 pixeli
    block_size = (50, 50)
    font = "arial.ttf"  # Fontul folosit pentru a desena caracterele
    image_name = "pickachu_fundal_alb.jpg"
    image_path = os.path.join("input", "images", image_name)

    image = preprocess_image(image_path, block_size)
    ascii_characters = get_ascii_characters()

    if image:
        # image.show()  # Afișăm imaginea pentru verificare
        if ascii_characters:
            logging.info(
                f"Am obtinut caracterele {ascii_characters} din fisierul de caractere.")

            # ascii_characters_images = [render_character(char, block_size, font) for char in ascii_characters]

            # Cream un dictionar carater imagine
            ascii_characters_images = {char: render_character(
                char, block_size, font) for char in ascii_characters}
