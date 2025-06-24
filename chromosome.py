import random
from typing import List, Tuple, Optional

class Chromosome:
    @classmethod
    def set_ascii_character_list(cls, ascii_character_list: List[str]) -> None:
        """
        Setează lista globală de caractere ASCII pentru clasa Chromosome.
        """
        cls.ascii_character_list = ascii_character_list

    @classmethod
    def set_size(cls, size: Tuple[int, int]) -> None:
        """
        Setează dimensiunea globală pentru clasa Chromosome.
        """
        cls.width = size[0]
        cls.height = size[1]

    @classmethod
    def __create_random_ascii_character_list(cls) -> list[list[str]]:
        """
        Creează o listă de caractere ASCII aleatorii de dimensiunea specificată.
        """

        # Construim o matrice de caractere ASCII
        ascii_image = []
        for _ in range(cls.height):
            row = [random.choice(cls.ascii_character_list) for _ in range(cls.width)]
            ascii_image.append(row)

        return ascii_image
        

    def __init__(self, ascii_image: List[List[str]] = None) -> None:
        """
        Initializarea cromozomului cu o listă de caractere ASCII și dimensiuni.
        """
        if ascii_image is None:
            self.ascii_image = self.__create_random_ascii_character_list()
        else:
            self.ascii_image = ascii_image

    def set_fitness(self, fitness: float) -> None:
        """
        Setează valoarea fitness a cromozomului.
        """
        self.fitness = fitness

    def mutate(self, mutation_rate: float) -> None:
        """
        Efectuează o mutație asupra cromozomului cu o rată de mutație specificată.
        """
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < mutation_rate:
                    # Folosim guided mutation
                    if (random.random() < 0.5):
                        if(self.ascii_image[y][x] == self.ascii_character_list[0]):
                            self.ascii_image[y][x] = self.ascii_character_list[-1]
                        else:
                            self.ascii_image[y][x] = self.ascii_character_list[self.ascii_character_list.index(self.ascii_image[y][x]) - 1]
                    else:
                        if(self.ascii_image[y][x] == self.ascii_character_list[-1]):
                            self.ascii_image[y][x] = self.ascii_character_list[0]
                        else:
                            self.ascii_image[y][x] = self.ascii_character_list[self.ascii_character_list.index(self.ascii_image[y][x]) + 1]
                    
    def print(self) -> None:
        """
        Afișează imaginea ASCII generată.
        """
        for y in range(self.height):
            for x in range(self.width):
                print(self.ascii_image[y][x], end="")
            print()