import os
import logging
from typing import List
from PIL import Image, UnidentifiedImageError

# Configurare logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_ascii_characters(source : str = os.path.join("input", "characters.txt")) -> List[str]:
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
                logging.warning("Fisierul de caractere este gol sau nu contine caractere valide.")
                return []
            
            return characters
        
    except FileNotFoundError:
        logging.error(f"Fisierul de caractere '{source}' nu a fost gasit.")
        return []
    except Exception as e:
        logging.error(f"A aparut o eroare la citirea fisierului de caractere: {e}")
        return []


def preprocess_image(image_path: str) -> Image.Image | None:
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

            return image
        
    except FileNotFoundError:
        logging.error(f"Image not found: {image_path}")
        return None
    except UnidentifiedImageError:
        logging.error(f"Fisierul de la calea '{image_path}' nu a putut fi identificat ca o imagine valida.")
        return None
    except Exception as e:
        logging.error(f"A aparut o eroare la procesarea imaginii: {e}")
        return None
    

if __name__ == "__main__":
    image_name = "pickachu_fundal_alb.jpg"
    image_path = os.path.join("input", "images", image_name)

    image = preprocess_image(image_path)
    ascii_characters = get_ascii_characters()

    if ascii_characters:
        logging.info(f"Am obtinut caracterele {ascii_characters} din fisierul de caractere.")

    if image:
        image.show()  # Afișăm imaginea pentru verificare