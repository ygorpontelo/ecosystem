from pygame import surface

class World:
    def __init__(self, size):
        self.creatures = {}
        self.background = surface.Surface(size).convert()
        self.background.fill((0, 0, 0))
        self.creatures_to_add = []
        self.creatures_to_remove = []   
        self.width = size[0]
        self.height = size[1]    

    def add_creture(self, creature):
        if creature.get_type in self.creatures:
            self.creatures[creature.get_type].append(creature)
        else:
            self.creatures[creature.get_type] = [creature]

    def remove_creature(self, creature):
        try:
            self.creatures[creature.get_type].remove(creature)
        except Exception:
            pass

    def process(self, time_elapsed):
        for creature_type in self.creatures:
            for creature in self.creatures[creature_type]:
                creature.process(time_elapsed)

        for creature in self.creatures_to_add:
            self.add_creture(creature)

        for creature in self.creatures_to_remove:
            self.remove_creature(creature)

        self.creatures_to_add.clear()
        self.creatures_to_remove.clear()

    def render(self, surface):
        surface.blit(self.background, (0, 0))
        for creature_type in self.creatures:
            for creature in self.creatures[creature_type]:
                creature.render(surface)