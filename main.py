class Player:
    def __init__(self, mineral, vespene):
        """Adding player's characteristics"""

        self.minerals = mineral
        self.gas = vespene
        self.max_supply = 200
        self.busy_supply = 0
        self.current_supply = 10
        self.summary_supply = 10
        self.own_units = []
        self.own_buildings = []
        self.roach_warrens_cnt = 0
        self.spawning_pools_cnt = 0

    def add_supply(self, additional_supply):
        """Adding supply, if it less than max supply"""

        self.current_supply += min(self.max_supply - self.current_supply,
                                   additional_supply)
        self.summary_supply += additional_supply

    def is_enough_gas(self, creature):
        if creature.gas_cost <= self.gas:
            return True
        else:
            print('You need more vespene gas!!!')
            return False

    def is_enough_minerals(self, creature):
        if creature.mineral_cost <= self.minerals:
            return True
        else:
            print('Not enough minerals!!!')
            return False

    def is_enough_supplies(self):
        if self.busy_supply <= self.current_supply:
            return True
        else:
            if self.current_supply < self.max_supply:
                print('Not enough overlords!!!')
            else:
                print('You have reached supply limit')
            return False

    def spend_resources(self, creature):
        self.gas -= creature.gas_cost
        self.minerals -= creature.mineral_cost


class Zergling:
    """Adding zergling's characteristics"""

    def __init__(self, player):
        self.name = 'zergling'
        self.location_space = 'ground'
        self.attack_space = 'ground'
        self.hp = 35
        self.mineral_cost = 50
        self.gas_cost = 0
        self.attack_power = 5
        self.armor = 0
        self.can_move = True
        self.taken_supplies = 0.5
        self.number = len(player.own_units)
        self.owner = player
        player.own_units.append(self)
        player.busy_supply += self.taken_supplies

    def attack(self, unit_hurting):
        if unit_hurting.location_space in self.attack_space:
            unit_hurting.hp -= self.attack_power
        else:
            print('This unit can attack only ', self.attack_space, ' units')

    def death(self):
        self.owner.busy_supply -= self.taken_supplies

        # When we delete self, all following elements numbers reduce by 1
        for creature in self.owner.own_units:
            if creature.number > self.number:
                creature.number -= 1
        del self.owner.own_units[self.number]

    def __lt__(self, compared_unit):
        return compared_unit.hp / self.attack_power > \
               self.hp / compared_unit.attack_power


class Drone(Zergling):
    """Changing drone's characteristics"""

    def __init__(self, player):
        Zergling.__init__(self, player)
        self.name = 'drone'
        self.hp = 45
        self.taken_supplies = 1
        player.busy_supply += self.taken_supplies - 0.5

    def build(self, structure):
        if (self.owner.is_enough_minerals(structure) and
                self.owner.is_enough_gas(structure)):
            self.owner.spend_resources(structure)
            self.death()
            return structure

    def mine_minerals(self):
        self.owner.minerals += 25

    def extracting_gas(self, ):
        self.owner.gas += 8


class Overlord(Zergling):
    """Changing overlord's characteristics"""

    def __init__(self, player):
        Zergling.__init__(self, player)
        self.name = 'overlord'
        self.location_space = 'air'
        self.hp = 200
        self.mineral_cost = 100
        self.attack_power = 0
        self.taken_supplies = 0
        self.owner.add_supply(8)
        player.busy_supply -= 0.5

    def death(self):
        Zergling.death(self)
        if self.owner.summary_supply > self.owner.max_supply:
            self.owner.current_supply = min(self.owner.summary_supply - 8,
                                            self.owner.max_supply)
        else:
            self.owner.current_supply -= 8


class Roach(Zergling):
    """Changing roach's characteristics"""

    def __init__(self, player):
        Zergling.__init__(self, player)
        self.name = 'roach'
        self.attack_space = 'ground and air'
        self.hp = 145
        self.mineral_cost = 75
        self.gas_cost = 25
        self.attack_power = 16
        self.taken_supplies = 2
        self.armor = 1
        player.busy_supply += self.taken_supplies - 0.5


class Larva(Zergling):
    """Changing larva's characteristics"""

    def __init__(self, player):
        Zergling.__init__(self, player)
        self.name = 'larva'
        self.hp = 25
        self.mineral_cost = 0
        self.attack_power = 0
        self.taken_supplies = 0
        self.armor = 10
        player.busy_supply -= 0.5

    def evolve(self, evolving_unit):
        if (self.owner.is_enough_minerals(evolving_unit) and
                self.owner.is_enough_gas(evolving_unit) and
                self.owner.is_enough_supplies()):

            if evolving_unit.name == 'zergling':

                # 2 zerglings spawn from 1 larva if player has spawning pool
                if self.owner.spawning_pools_cnt > 0:
                    self.owner.spend_resources(evolving_unit)
                    self.death()
                    return Zergling(self.owner), evolving_unit

                else:
                    print('You need spawning pool to evolve')
                    evolving_unit.death()
                    return self

            else:

                # Roach spawns if player has spawning pool
                if evolving_unit.name == 'roach':
                    if self.owner.roach_warrens_cnt > 0:
                        self.owner.spend_resources(evolving_unit)
                        self.death()
                        return evolving_unit

                    else:
                        print('You need roach warren to evolve')
                        evolving_unit.death()
                        return self

                else:
                    self.owner.spend_resources(evolving_unit)
                    self.death()
                    return evolving_unit
        else:
            evolving_unit.death()
            return self


class Spawning_Pool:
    """Changing spawning pool's characteristics"""

    def __init__(self, player):
        self.name = 'spawning pool'
        self.location_space = 'ground'
        self.hp = 750
        self.mineral_cost = 200
        self.gas_cost = 0
        self.armor = 1
        self.can_move = False
        self.number = len(player.own_buildings)
        self.owner = player
        player.own_buildings.append(self)
        player.spawning_pools_cnt += 1

    def death(self):
        self.owner.spawning_pools_cnt -= 1

        # When we delete self, all following elements numbers reduce by 1
        for creature in self.owner.own_buildings:
            if creature.number > self.number:
                creature.number -= 1
        del self.owner.own_buildings[self.number]


class Roach_Warren(Spawning_Pool):
    """Changing roach warren's characteristics"""

    def __init__(self, player):
        Spawning_Pool.__init__(self, player)
        self.name = 'roach warren'
        self.hp = 850
        self.mineral_cost = 150
        player.spawning_pools_cnt -= 1
        player.roach_warrens_cnt += 1

    def death(self):
        Spawning_Pool.death(self)
        self.owner.spawning_pools_cnt += 1
        self.owner.roach_warrens_cnt -= 1


class Hatchery(Spawning_Pool):
    """Changing hatchery's characteristics"""

    def __init__(self, player):
        Spawning_Pool.__init__(self, player)
        self.name = 'hatchery'
        self.hp = 1250
        self.mineral_cost = 300
        player.spawning_pools_cnt -= 1
        player.add_supply(2)

    def death(self):
        Spawning_Pool.death(self)
        self.owner.spawning_pools_cnt += 1
        if self.owner.summary_supply > self.owner.max_supply:
            self.owner.current_supply = min(self.owner.summary_supply - 2,
                                            self.owner.max_supply)
        else:
            self.owner.current_supply -= 2

    def create_larva(self):
        return Larva(self.owner)


# /Comment/ To show class let's play a little game

# CoolJoker = Player(150, 0)
# cooljokers_hatchery = Hatchery(CoolJoker)

# Part 1: We play by CoolJoker

# cool_larva = cooljokers_hatchery.create_larva()
# cool_larva.evolve(Drone(CoolJoker))

# Part 2: Now CoolJoker has hatchery, drone and 100 minerals
# Let's spawn 2 more drones and mine some minerals to build spawning pool

# cooljokers_hatchery.create_larva()
# cooljokers_hatchery.create_larva()
# CoolJoker.own_units[2].evolve(Drone(CoolJoker))
# CoolJoker.own_units[1].evolve(Drone(CoolJoker))

# Part 3: Then we will mine a lot of minerals by 3 our drones

# while CoolJoker.minerals < 10000:
    # for creation in CoolJoker.own_units:
        # if creation.name == 'drone':
            # creation.mine_minerals()

# Part 4: I think that's enough. Let's build spawning pool and spawn 6 zerglings

# CoolJoker.own_units[2].build(Spawning_Pool(CoolJoker))
# cnt = 0
# while cnt < 3:
    # cool_larva = cooljokers_hatchery.create_larva()
    # cool_larva.evolve(Zergling(CoolJoker))
    # cnt += 1

# Part 5: 2 player Jamazex want to destroy our hatchery, we should defend it,
# but zerglings are too weak. Let's build roach warren, get some vespene and
# evolve larva's in roaches

# while CoolJoker.gas < 1500:
    # for creation in CoolJoker.own_units:
        # if creation.name == 'drone':
            # creation.extracting_gas()
# CoolJoker.own_units[1].build(Roach_Warren(CoolJoker))
# cool_larva = cooljokers_hatchery.create_larva()
# cool_larva.evolve(Roach(CoolJoker))

# Part 6: Let's check objects that we have

# for unit in CoolJoker.own_units:
    # print(unit.name, 'U')
# for building in CoolJoker.own_buildings:
    # print(building.name, 'B')

# Part 7.1: Now we are starting roach evolving

# cnt = 0
# while cnt < 4:
    # cool_larva = cooljokers_hatchery.create_larva()
    # cool_larva.evolve(Roach(CoolJoker))
    # cnt += 1
# /Comment/ Oh, we forgot about overlords, we need to produce 1
# print('*Overlord produced*')
# cool_larva = cooljokers_hatchery.create_larva()
# cool_larva.evolve(Overlord(CoolJoker))
# cool_larva = cooljokers_hatchery.create_larva()
# cool_larva.evolve(Roach(CoolJoker))

# Part 8: Is zergling weaker than roach?

# print(CoolJoker.own_units[1] <
      # CoolJoker.own_units[len(CoolJoker.own_units) - 1])

# Part 9: This our enemy

# Jamazex = Player(0, 0)
# jamazex_lings = []
# cnt = 14
# while cnt > 0:
    # jamazex_lings.append(Zergling(Jamazex))
    # cnt -= 1

# Part 10: We need to beat his zerglings, to avoid losing our hatchery

# end_fight = 0
# while not end_fight:

    # /Comment/ CoolJoker's units attack
    # for cool_unit in CoolJoker.own_units:
        # enemy_number = 0
        # if len(Jamazex.own_units) == 0:
            # end_fight = 1
            # print("All enemies has been killed")
            # break

        # /Comment/ Finding alive enemy, if all of them dead, end fight
        # while Jamazex.own_units[enemy_number].hp <= 0:
            # enemy_number += 1
            # if enemy_number == len(Jamazex.own_units):
                # end_fight = 1
                # print("All enemies has been killed")
                # break

        # if end_fight:
            # break

        # cool_unit.attack(Jamazex.own_units[enemy_number])

    # /Comment/ Jamazex's units attack
    # for not_cool_unit in Jamazex.own_units:
        # jamazex_enemy_number = 0

        # /Comment/ Finding alive enemy, if all of them dead, end fight
        # while CoolJoker.own_units[jamazex_enemy_number].hp < 0:
            # jamazex_enemy_number += 1
            # if jamazex_enemy_number == len(Jamazex.own_units):
                # end_fight = 1
                # print("All our units has been killed")
                # break

        # if end_fight:
            # break

        # not_cool_unit.attack(CoolJoker.own_units[jamazex_enemy_number])

    # /Comment/ Getting rid of the living dead
    # while len(CoolJoker.own_units) > 0 and CoolJoker.own_units[0].hp <= 0:
        # CoolJoker.own_units[0].death()
    # while len(Jamazex.own_units) > 0 and Jamazex.own_units[0].hp <= 0:
        # Jamazex.own_units[0].death()

# Part 11: Great, we won, let's BM him a little
# if len(Jamazex.own_units):
    # print('Ha-ha, weak platinum rating player')
# /Comment/ Don't BM people in the real matches
