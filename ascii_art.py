import os
import logging
from typing import List
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError
from skimage.metrics import structural_similarity as ssim
import numpy as np
from chromosome import Chromosome
import random
import matplotlib.pyplot as plt

# Configurare logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

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
    # similarity = ssim(image_array, character_array)/1

    # Calculăm similaritatea folosind L1
    similarity = np.sum(character_array - image_array) / (image_array.size * 255.0)

    # print(similarity)

    return similarity

def finess_function(image: Image.Image,
                    ascii_image: List[List[str]],
                    ascii_characters_images: dict[str, Image.Image],
                    block_size: tuple[int, int],
                    ascii_art_size: tuple[int, int] = (0, 0),
                    maximum_similarity = 1
                    ) -> float:
    """
    Evaluează similitudinea dintre imaginea originală și imaginea ASCII generată.
    """
    fitness = 0.0
    width, height = image.size
    block_width, block_height = block_size
    ascii_width, ascii_height = ascii_art_size

    for y in range(ascii_height):
        for x in range(ascii_width):
            # Obținem caracterul ASCII corespunzător
            character = ascii_image[y][x]
            if character not in ascii_characters_images:
                logging.warning(f"Caracterul '{character}' nu are o imagine asociata.")
                continue

            character_image = ascii_characters_images[character]

            # Calculăm coordonatele zonei din imaginea originală
            left = x * block_width
            top = y * block_height
            right = left + block_width
            bottom = top + block_height

            # Extragem zona din imaginea originală
            image_zone = image.crop((left, top, right, bottom))

            # Calculăm similaritatea dintre zona din imagine și imaginea caracterului
            similarity = image_zone_to_character_similarity(image_zone, character_image)
            
            fitness += similarity

    return (fitness / (ascii_width * ascii_height)) if ascii_width * ascii_height > 0 else 0.0

def generate_population(size : int) -> List[Chromosome]:
    """
    Generează o populație de cromozomi pentru algoritmul genetic.
    """
    population = []
    for _ in range(size):
        chromosome = Chromosome()
        population.append(chromosome)
    
    return population

def evaluate_individuals(population: List[Chromosome],
                        image: Image.Image,
                        ascii_characters_images: dict[str, Image.Image],
                        block_size: tuple[int, int],
                        ascii_art_size: tuple[int, int] = (0, 0),
                        maximum_similarity = 1
                        ) -> List[Chromosome]:
    """
    Evaluează populația de cromozomi și le setează fitness-ul.
    """
    for chromosome in population:
        fitness = finess_function(image, chromosome.ascii_image,ascii_characters_images, block_size, ascii_art_size, maximum_similarity)
        chromosome.set_fitness(fitness)

def evaluate_population(population: List[Chromosome]) -> float:
    """
    Calculeaza meadia fitness-ului.
    """
    population_size = len(population)
    total_fitness = sum(chromosome.fitness for chromosome in population)
    return total_fitness / population_size if population_size > 0 else 0.0

def select_parents(population: List[Chromosome], 
                   population_size: int,
                   tournament_size = 5,
                   elitism = 3
                   ) -> List[Chromosome]:
    """
    Selectează părinți din populație pe baza fitness-ului.
    Functia utilizează metoda turneului combinata cu elitism.
    """
    selected_parents = sorted(population, key=lambda c: c.fitness, reverse=True)[:elitism]
    
    for _ in range(population_size - elitism):
        tournament = random.sample(population, tournament_size)
        best_parent = max(tournament, key=lambda c: c.fitness)
        selected_parents.append(best_parent)

    return selected_parents

def crossover(parent1: Chromosome, parent2: Chromosome) -> Chromosome:
    """
    Efectuează crossover între doi părinți pentru a crea un nou cromozom.
    Functia utilizeaza crossover uniform.
    """
    new_ascii_image = []
    for y in range(Chromosome.height):
        new_row = []
        for x in range(Chromosome.width):
            # Alege aleatoriu un caracter de la unul dintre părinți
            if random.random() < 0.5:
                new_row.append(parent1.ascii_image[y][x])
            else:
                new_row.append(parent2.ascii_image[y][x])
        new_ascii_image.append(new_row)

    return Chromosome(new_ascii_image)    

def mutate_population(population: List[Chromosome], mutation_rate: float) -> None:
    """
    Efectuează mutații asupra unui cromozom cu o rată specificată.
    """
    for chromosome in population:
        chromosome.mutate(mutation_rate)  

def generate_next_generation(parents: List[Chromosome], 
                            population_size: int, 
                            ) -> List[Chromosome]:
    """
    Generează următoarea generație de cromozomi prin crossover.
    """
    next_generation = []
    
    while len(next_generation) < population_size:
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        
        # Efectuăm crossover
        child = crossover(parent1, parent2)
        
        next_generation.append(child)

    return next_generation


def generate_ascii_art(image: Image.Image, 
                        ascii_characters_images: dict[str, Image.Image], 
                        block_size: tuple[int, int], 
                        ascii_art_size: tuple[int, int]) :
    """
    Generează ASCII art din imaginea dată selectand cel mai potrivit caracter pentru fiecare bloc.
    """
    ascii_art = []
    width, height = image.size
    block_width, block_height = block_size
    ascii_width, ascii_height = ascii_art_size

    for y in range(ascii_height):
        row = []
        for x in range(ascii_width):
            # Calculăm coordonatele zonei din imaginea originală
            left = x * block_width
            top = y * block_height
            right = left + block_width
            bottom = top + block_height

            # Extragem zona din imaginea originală
            image_zone = image.crop((left, top, right, bottom))

            # Găsim cel mai potrivit caracter pentru această zonă
            best_character = None
            best_similarity = -1.0

            for character, char_image in ascii_characters_images.items():
                similarity = image_zone_to_character_similarity(image_zone, char_image)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_character = character

            row.append(best_character)

        ascii_art.append(''.join(row))
    return ascii_art

def introduce_new_chromosomes(population: List[Chromosome],
                            population_size: int,
                            new_chromosomes_percentage: float) -> List[Chromosome]:
    """
    Introduce un anumit procent de cromozomi noi în populație.
    """
    new_chromosomes_count = int(population_size * new_chromosomes_percentage)

    for _ in range(new_chromosomes_count):
        chromosome = Chromosome()
        population[random.randint(0, population_size - 1)] = chromosome

    return population

if __name__ == "__main__":
    font = "DejaVuSansMono.ttf"  # Fontul folosit pentru a desena caracterele
    image_name = "pickachu_fundal_colorat.jpg"
    block_size = (8, 16)

    # Parametri pentru populatie
    population_size = 200
    tournament_size = 7
    generation_count = 400
    mutation_rate = 0.1
    base_mutation_rate = 0.06
    max_mutation_rate = 0.2
    elitism = 5
    epsilon = 0.0001
    past_generation_count = 10
    introduce_new_chromosomes_interval = 25
    new_chromosomes_percentage = 0.25

    average_fitness_history = []
    best_fitness_history = []

    image_path = os.path.join("input", "images", image_name)
    image = preprocess_image(image_path, block_size)
    
    if image is None:
        logging.error("Imaginea nu a putut fi procesată. Asigurați-vă că calea este corectă și imaginea este validă.")
    else:
        ascii_art_size = (image.size[0] // block_size[0],image.size[1] // block_size[1])  # Dimensiunea imaginii ASCII art

    ascii_characters = get_ascii_characters()

    if ascii_characters:
            # Cream un dictionar carater imagine
        ascii_characters_images = {char: render_character(char, block_size, font) for char in ascii_characters}

        # Generam cel mai bun ASCII art conform functiei de fitness
        best_ascii_art = generate_ascii_art(image, ascii_characters_images, block_size, ascii_art_size)
        for line in best_ascii_art:
            print(line)
        # evaluam imaginea ASCII generată
        maximum_fitness = finess_function(image, best_ascii_art, ascii_characters_images, block_size, ascii_art_size)
        logging.info(f"Fitness-ul imaginii ASCII generate: {maximum_fitness:.4f}")

        # Setăm parametrii pentru cromozomi
        Chromosome.set_ascii_character_list(ascii_characters)
        Chromosome.set_size(ascii_art_size)

        # Generăm populația
        population = generate_population(population_size)
        # Evaluăm populația
        evaluate_individuals(population, image, ascii_characters_images, block_size, ascii_art_size)
        average_fitness_history.append(evaluate_population(population))
        # Selectăm părinți
        parents = select_parents(population, population_size, tournament_size, elitism)

        # Generăm următoarea generație
        for generation in range(generation_count):
            print(f"Generatia {generation + 1}/{generation_count}")
            next_generation = generate_next_generation(parents, population_size)
            # Efectuăm mutații
            mutate_population(next_generation, mutation_rate)
            evaluate_individuals(next_generation, image, ascii_characters_images, block_size, ascii_art_size)
            average_fitness = evaluate_population(next_generation)
            average_fitness_history.append(average_fitness)
            print(f"Fitness-ul mediu al generatiei: {average_fitness:.4f}")
            print(f"Rata de mutatie curenta: {mutation_rate}")
            # Pregătim pentru următoarea iterație
            population = next_generation
            parents = select_parents(population, population_size, tournament_size, elitism)

            # Afisam imaginea ASCII generată de cel mai bun cromozom pentru fiecare generatie
            best_chromosome = max(population, key=lambda c: c.fitness)
            best_fitness_history.append(best_chromosome.fitness)
            print("Imaginea ASCII generata de cel mai bun cromozom:")
            best_chromosome.print()

            if generation > past_generation_count and abs(average_fitness_history[-1] - average_fitness_history[-past_generation_count]) <= epsilon:
                mutation_rate = min(mutation_rate + 0.02, max_mutation_rate)
            else:
                mutation_rate = max(mutation_rate - 0.005, base_mutation_rate)
                
            if(generation % introduce_new_chromosomes_interval == 0):
                population = introduce_new_chromosomes(population, population_size, new_chromosomes_percentage)
        # Salvam imaginea ascii generata de cel mai bun cromozom intr-un fisier text din output si plotam evolutia fitness-ului pe care o salvam tot in fisier
        best_chromosome = max(population, key=lambda c: c.fitness)
        with open(os.path.join("output", "best_ascii_art.txt"), "w") as f:
            for line in best_chromosome.ascii_image:
                f.write("".join(line) + "\n")
        
        plt.plot(average_fitness_history, label="Fitness mediu")
        plt.plot(best_fitness_history, label="Fitness cel mai bun")
        plt.xlabel("Generatia")
        plt.ylabel("Fitness")
        plt.title("Evolutia fitness-ului")
        plt.legend()
        plt.savefig(os.path.join("output", "fitness_evolution.png"))
        plt.show()