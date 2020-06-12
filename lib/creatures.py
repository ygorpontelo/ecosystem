from pygame import draw, Vector2
from random import randint, random
from abc import abstractmethod, ABC

class BaseCreature(ABC):
    def __init__(self, world, color, coord=None, radius=None):
        self.world = world
        self.color = color
        self.energy = 3000
        self._maxenergy = 3000
        self.alive = True
        self.qtd_breed = 0
        self.qtd_alive = 0

        if coord: 
            self.coord = coord

            # Avoid rendering outside the screen
            width, height = self.world.width, self.world.height
            if self.coord.x > width: self.coord.x = width
            elif self.coord.x < 0: self.coord.x = 0
            
            if self.coord.y > height: self.coord.y = height
            elif self.coord.y < 0: self.coord.y = 0

        else: self.coord = Vector2((randint(0, world.width), randint(0, world.height)))

        if radius: self.radius = radius
        else: self.radius = (random()*10)%8 + 2

    def die(self):
        self.world.creatures_to_remove.append(self)    
        self.alive = False

    @abstractmethod
    def breed(self):
        self.qtd_breed += 1

    @abstractmethod
    def check_necessities(self):
        pass

    @abstractmethod
    def process(self, time_elapsed):
        if self.alive:
            self.qtd_alive += time_elapsed
    
    def render(self, screen):
        draw.circle(screen, self.color, (round(self.coord.x), round(self.coord.y)), round(self.radius))

    @property
    def get_type(self):
        return '{}'.format(type(self).__name__)

    @property
    def get_consumed_energy(self):
        return self._maxenergy/2 * self.radius

class Plant(BaseCreature):
    def __init__(self, world, color=(0, randint(0, 155)+100, 0), coord=None, radius=None):
        super().__init__(world, color, coord=coord, radius=radius)

    def breed(self):
        super().breed()

        if (random()*100000+1) <= self.radius:
            self.world.creatures_to_add.append(Plant(self.world, self.color, self.coord + Vector2((randint(-50,50), randint(-50,50))), self.radius))
            self.energy -= 1 + self.radius * (1.1 - self.color[1]/255)
    
    def check_necessities(self):
        if self.energy <= 0:
            self.die()
 
    def process(self, time_elapsed):
        super().process(time_elapsed)

        if self.alive:     
            self.check_necessities()
            self.breed()
            self.energy -= time_elapsed * self.radius * (1.05 - self.color[1]/255)

class Animal(BaseCreature, ABC):
    def __init__(self, world, color, gender=bool(randint(0,1)), coord=None, radius=None, vision=None, velocity=None):
        super().__init__(world, color, coord=coord, radius=radius)

        self.danger = False
        self.hungry = False
        self.horny = False
        self.gender = gender
        self.destiny = Vector2((randint(0, self.world.width), randint(0, self.world.height)))

        if vision: self.vision = vision
        else: self.vision = (random()*100)%200 + 20

        if velocity: self.velocity = velocity
        else: self.velocity = (random()*10) + 15

    def check_necessities(self):
        if self.energy <= 0:
            self.die()
        else:

            if randint(1, 1000) == 1: 
                if self.energy > 10 + self.energy-self.radius:
                    self.horny = True
                else:
                    self.horny = False

            if self.energy < self._maxenergy/2:
                self.hungry = True
            else:
                self.hungry = False

    def process(self, time_elapsed):
        super().process(time_elapsed)

        if self.alive:    
            self.check_necessities()

            d = 0
            if self.danger:
                d = self.run(time_elapsed)
            elif self.hungry:
                d = self.hunt(time_elapsed)
            elif self.horny:
                d = self.search_mate(time_elapsed)
            else:
                d = self.move(time_elapsed)

            self.energy -= d * (1 + self.radius) + time_elapsed * self.radius

    def move(self, time_elapsed, factor=1):
        if self.coord.distance_to(self.destiny) > 5:
            heading = self.destiny - self.coord
            heading = heading.normalize()
            dist = self.velocity * factor * time_elapsed
            dist = heading * dist
            d = self.coord.distance_to(self.coord + dist)
            self.coord += dist
            if self.coord[0] > self.world.width or self.coord[1] > self.world.height or self.coord[0] < 0 or self.coord[1] < 0:
                self.coord -= dist
                self.destiny = Vector2((randint(0,self.world.width), randint(0,self.world.height)))
                return self.move(time_elapsed, factor)
            return d
        else:
            self.destiny = Vector2((randint(0, self.world.width), randint(0, self.world.height)))
            return self.move(time_elapsed, factor)

    def run(self, time_elapsed):
        return self.move(time_elapsed, factor=2)

    @abstractmethod
    def search_mate(self):
        pass
    
    @abstractmethod
    def hunt(self):
        pass

class Herbivore(Animal):
    def __init__(self, world, color=(0, 0, randint(0, 155)+100), gender=bool(randint(0,1)), coord=None, radius=None, vision = None, velocity = None,):
        super().__init__(world, color, gender, coord=coord, radius=radius, vision=vision, velocity=velocity)

    def check_necessities(self):
        super().check_necessities()

        if self.alive:
            predators = [p for p in self.world.creatures['Carnivore'] if self.coord.distance_to(p.coord) <= self.vision]

            if len(predators) > 0:
                self.danger = True
                predators.sort(key=lambda x: self.coord.distance_to(x.coord))
                self.destiny = -predators[0].coord
            else:
                self.danger = False

    def breed(self, creature):
        if self.gender:
            self.world.creatures_to_add.append(Herbivore(self.world, 
                color = ((self.color[0]+creature.color[0])/2, (self.color[1]+creature.color[1])/2, (self.color[2]+creature.color[2])/2),
                coord = self.coord + Vector2((randint(-10, 10), randint(-10, 10))), 
                velocity = (self.velocity+creature.velocity)/2, 
                vision = (self.vision+creature.vision)/2, 
                radius =(self.radius+creature.radius)/2))
            self.energy -= self.radius
            self.horny = False

    def search_mate(self, time_elapsed):
        mates = [m for m in self.world.creatures['Herbivore'] if m.gender != self.gender and self.coord.distance_to(m.coord) <= self.vision]
        
        if len(mates) > 0:
            mates.sort(key= lambda x: self.coord.distance_to(x.coord))
            self.destiny = mates[0].coord

            if self.coord.distance_to(self.destiny) <= 10:
                self.breed(mates[0])
            return self.run(time_elapsed)
        else:
            return self.move(time_elapsed)

    def hunt(self, time_elapsed):
        preys = [p for p in self.world.creatures['Plant'] if self.coord.distance_to(p.coord) <= self.vision]

        if len(preys) > 0:
            preys.sort(key= lambda plant: self.coord.distance_to(plant.coord) - plant.color[1] * (1+plant.radius) )
            self.destiny = preys[0].coord

            if self.coord.distance_to(self.destiny) <= 10:
                preys[0].die()
                self.energy += preys[0].get_consumed_energy
            return self.run(time_elapsed)
        else:
            return self.move(time_elapsed)

class Carnivore(Animal):
    def __init__(self, world, color=(randint(0, 155)+100, 0, 0), gender=bool(randint(0,1)), coord=None, radius=None, vision = None, velocity = None,):
        super().__init__(world, color, gender, coord=coord, radius=radius, vision=vision, velocity=velocity)

    def breed(self, creature):
        if self.gender:
            self.world.creatures_to_add.append(Carnivore(self.world, 
                    color = ((self.color[0]+creature.color[0])/2, (self.color[1]+creature.color[1])/2, (self.color[2]+creature.color[2])/2),  
                    coord = self.coord + Vector2((randint(-10, 10), randint(-10, 10))), 
                    velocity = (self.velocity+creature.velocity)/2, 
                    vision = (self.vision+creature.vision)/2, 
                    radius =(self.radius+creature.radius)/2))
            self.energy -= self.radius
            self.horny = False

    def search_mate(self, time_elapsed):
        mates = [m for m in self.world.creatures['Carnivore'] if m.gender != self.gender and self.coord.distance_to(m.coord) <= self.vision and m.horny]
        
        if len(mates) > 0:
            mates.sort(key= lambda x: self.coord.distance_to(x.coord))
            self.destiny = mates[0].coord

            if self.coord.distance_to(self.destiny) <= 10:
                self.breed(mates[0])
            return self.run(time_elapsed)
        else:
            return self.move(time_elapsed)

    def hunt(self, time_elapsed):
        preys = [p for p in self.world.creatures['Herbivore'] if self.coord.distance_to(p.coord) <= self.vision and self.radius >= p.radius]
        
        if len(preys) > 0:
            preys.sort(key= lambda herb: self.coord.distance_to(herb.coord))
            self.destiny = preys[0].coord

            if self.coord.distance_to(self.destiny) <= 10:
                preys[0].die()
                self.energy += preys[0].get_consumed_energy
            return self.run(time_elapsed)
        else:
            return self.move(time_elapsed)