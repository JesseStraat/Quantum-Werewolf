from sympy.utilities.iterables import multiset_permutations
from tabulate import tabulate
import numpy as np
import random
import os

class Game:

    def __init__(self):
        self.players = []
        self.role_count= {'werewolf':2, 'seer':1}
        self.player_count = 10
        self.started = False

    # Add players to the game
    def add_players(self, *names):
        # name: the name (or list of names) of the player(s) to add

        # The game can't be ongoing
        if not self.check_started(False):
            return None

        # Add names from input and input lists
        for name in names:
            if isinstance(name, str):
                # Check if name is not already taken
                if name in self.players:
                    print("Player {} already exists!".format(name))
                else: self.players.append(name)
            elif isinstance(name, list):
                # unwrap list and pass to add_players again
                self.add_players(*name)
            else: print("Wrong data type: {}, must be either string or list of strings".format(type(name)))

    # Set the contents of the deck
    def set_role(self, role, amount):
        # roles: [werewolves, seers]
        self.role_count[role] = amount

    # Identify the player names with their IDs
    def identify_players(self):
        self.player_count = len(self.players)
        idfy = [[i+1, self.players[i]] for i in range(self.player_count)]
        print(tabulate(idfy, headers = ["ID", "Name"]))

    # Start the game
    def start(self):
        if self.check_started(False):

            # Shuffling the player order
            # random.shuffle(self.players)

            # Determine playercount or generate players if none are given
            if self.players != []:
                self.player_count = len(self.players)
            else:
                self.players = ["Player " + str(x+1) for x in range(self.player_count)]

            # Determine (valid) amount of villager in the game
            villagers = self.player_count - sum(self.role_count.values())
            if villagers < 0:
                print("Too few players, decrease the amount of roles!")
                return False

            # Sets the list of roles
            roles = self.role_count['werewolf'] * ["w"] + self.role_count['seer'] * ["s"] + villagers * ["v"]
            self.werewolf_count = self.role_count['werewolf']

            # Generates the list of all role permutations
            self.permutations = list(multiset_permutations(roles))

            # Set all players to be fully alive
            self.deaths = []
            for i in range(self.player_count):
                self.deaths += [[0] * self.player_count]
            self.killed = [0] * self.player_count

            # start game
            self.started = True
            print("Game started.")

            self.calculate_probabilities()

            return True

    # Stop the game
    def stop(self):
        if self.check_started():
            self.started = False
            print("Game stopped.")

    # Reset the game
    def reset(self):
        self.players = []
        self.role_count= {'werewolf':2,'seer':1}
        if self.started == True:
            self.stop()
        print("Game reset.")

    # Check if game has(n't) started and throw error otherwise
    def check_started(self, boolean = True):
        # boolean: set this to false if you want to check if you HAVEN'T started yet
        # The point of this function is to throw an error if the game hasn't started yet
        if self.started == boolean:
            return True
        else:
            if boolean:
                print("Please start the game first with start().")
                return False
            else:
                print("Please stop the game first with stop().")
                return False

    # Returns the ID corresponding to someone's name
    def ID(self, player_name):
        #name: the name of the player
        return self.players.index(player_name)

    # Returns the ID corresponding to someone's name
    def name(self, player_id):
        #name: the name of the player
        return self.players[player_id]

    # Return the role corresponding to some letter
    def role(self, letter):
        # letter: the letter who's corresponding role you want to know
        roles = ["villager", "werewolf", "seer"]
        letters = ["v", "w", "s"]
        return roles[letters.index(letter)]

    # Gives the table of probabilities
    def get_probabilities(self):
        if self.check_started():
            self.calculate_probabilities()
            print("There are {} possible permutations left.\n".format(self.nperm))
            print(tabulate(self.probs, headers = ["Player", "Villagers", "Seer", "Werewolf", "Dead"]))


    # Calculates the probabilities
    def calculate_probabilities(self):
        if self.check_started():
            self.nperm = len(self.permutations)
            permt = np.array(self.permutations).T.tolist()
            probst = []
            for i, p in enumerate(self.players):
                P_villager = permt[i].count("v")/self.nperm
                P_seer = permt[i].count("s")/self.nperm
                P_werewolf = permt[i].count("w")/self.nperm
                P_dead = self.death_probability(p)
                probst.append([i+1, P_villager, P_seer, P_werewolf, P_dead])
            self.probs = probst

    # Let a player take his seer action
    def seer(self, seer, target):
        # seer: name of the seer
        # target: name of the target of the seer
        if self.check_started():
            seer_id = self.ID(seer)
            target_id = self.ID(target)

            # Check if player and target are alive and player can be the seer
            assert self.killed[seer_id] != 1, "ERROR: in seer() seer {} is dead.".format(seer)
            assert self.killed[target_id] != 1, "ERROR: in seer() target {} is dead.".format(target)
            assert self.probs[seer_id][2] != 0, "ERROR: {}'s seer probability is 0.".format(seer)

            # Player is allowed to take the action
            print("{} is investigating {} ...".format(seer, target))
            p_list = []
            for p in self.permutations:
                if p[seer_id] == "s":
                    p_list.append(p)

            # Choose an outcome
            assert len(p_list) > 0, "ERROR: seer list is empty"
            observation = random.choice(p_list)[target_id]

            # Collapse the wave function
            for p in p_list:
                if p[target_id] != observation:
                    self.permutations.remove(p)

            # Report on results
            print("{} sees that {} is a {}!".format(seer, target, self.role(observation)))

    # Force someone's death (e.g., after a vote). Otherwise used only by script
    def kill(self, target):
        # target: the name of the target
        target_id = self.ID(target)
        if self.check_started():
            assert self.killed[target_id] != 1, "ERROR:in kill() target {} is already dead.".format(target)

            print("{} was killed!".format(target))

            # Chooses an outcome
            res = random.choice(self.permutations)
            prole = res[target_id]
            permt = list(self.permutations)

            # Collapse the wave function
            for p in permt:
                if p[target_id] != prole:
                    self.permutations.remove(p)

            # Report on results
            print("{} was a {}!".format(target, self.role(prole)))

            # Deal with the case that the dead person is a werewolf
            if self.role(prole) == "w":
                self.werewolf_count -= 1
                for i in range(self.player_count):
                    deaths[i][target_id] = 0

            self.killed[target_id] = 1
            self.calculate_probabilities()

    # Shows the probability of death for a player
    def death_probability(self, name):
        # name: name of player
        name_id = self.ID(name)
        if self.check_started():
            dead = 0
            if self.killed[name_id] == 1:
                dead = 1
            else:
                deathn = 0
                for p in self.permutations:
                    for i in range(self.player_count):
                        if p[i] == "w" and p[name_id] != "w":
                            deathn += self.deaths[name_id][i]
                dead = deathn / len(self.permutations)
                if dead >= 1:
                    self.kill(name)
            return dead

    # Lets someone commit their wolf action
    def wolf(self, wolf, target):
        # wolf: the name of the wolf
        # target: the name of the wolf's target
        wolf_id = self.ID(wolf)
        target_id = self.ID(target)
        if self.check_started():
            assert self.killed[wolf_id] != 1, "ERROR: in wolf() wolf {} is dead".format(wolf)
            assert self.killed[target_id] != 1, "ERROR: in wolf() target {} is dead".format(target)

            self.deaths[target_id][wolf_id] = 1 / self.werewolf_count
            print("{} has mauled {}!".format(wolf, target))

    def check_win(self):
        villager_win = True
        werewolf_win = True
        for perm in self.permutations:
            for ID, role in enumerate(perm):
                if self.killed[ID] == 0:
                    if role == 'w':
                        villager_win = False
                    else:
                        werewolf_win = False
        if villager_win:
            print('The villagers win!')
            return True
        if werewolf_win:
            print('The werewolves win!')
            return True
        return False




def ask_yesno(query, yes, no):
    answer = input(query + ' (yes/no) ')
    if answer == 'yes' or answer == 'y':
        if isinstance(yes, str):
            print(yes)
        else:
            yes()
    elif answer == 'no' or answer == 'n':
        if isinstance(no, str):
            print(no)
        else:
            no()
    else:
        print('invalid answer')
        ask_yesno(query, yes, no)

def ask_player(query):
    answer = input(query + ' Name: ')
    if answer in g.players and g.killed[g.ID(answer)] == 0:
        return answer
    else:
        print('  "{}" is not a living player'.format(answer))
        print('  Players alive are:')
        for i, p in enumerate(g.players):
            if g.killed[i] == 0:
                print("    {}".format(p))

        return ask_player(query)

if __name__ == "__main__":
    g = Game()

    os.system('clear')

    print("Enter player name(s) separated by spaces.")
    print("Enter no name to continue.")

    # Get player names
    new_player = True
    while new_player:
        names = input("  Name(s): ")
        if names != '':
            g.add_players(names.split())
        else:
            new_player = False

    os.system('clear')

    print("Current Players:")
    for i, p in enumerate(g.players):
        print(" {}: {}".format(i+1,p))

    # Set the deck
    print("\nPlay with following roles?")
    for (role, count) in g.role_count.items():
        if count == 1:
            suffix = ''
        else:
            suffix = 's'
        print(" {} {}{}".format(count, role, suffix))

    def set_role(role, amount):
        def set_seer_value():
            g.set_role(role, amount)
        return set_seer_value

    def ask_roles():
        # ask for new roles
        g.role_count['werewolf'] = int(input('\nNumber of werewolves: '))
        ask_yesno('Include seer?', set_role('seer',1), set_role('seer',0))

    ask_yesno('', "roles confirmed!",  ask_roles)

    os.system('clear')

    # Start game
    g.start()

    # loop turns for every player
    turn_counter = 0
    while g.started == True:
        turn_counter += 1
        # night
        os.system('clear')
        print('Night falls and all players take their actions in turns privately\n')

        start_probabilities = g.probs

        for i, p in enumerate(g.players):
            if g.killed[i] == 1:
                continue

            input("{}'s turn (press ENTER to continue)".format(p))
            os.system('clear')
            print("{}'s turn".format(p))

            # display game and player info (role superposition)
            player_probabilities = start_probabilities[i]
            print('\n  Your role:')
            print("    Villager: {:3.0f}%".format(100*player_probabilities[1]))
            print("    Seer:     {:3.0f}%".format(100*player_probabilities[2]))
            print("    werewolf: {:3.0f}%\n".format(100*player_probabilities[3]))

            # seer
            if player_probabilities[2] != 0:
                target = ask_player('  SEER: Whose role do you inspect?\n   ')
                g.seer(p,target)

            # wolf
            if player_probabilities[3] != 0:
                target = ask_player('  WOLF: Who do you attack?\n   ')
                g.wolf(p,target)

            input("\n(press ENTER to continue)")

            os.system('clear')

        # day
        input('all player have had their turn (press ENTER to continue)')
        os.system('clear')
        print('The day begins')

        g.get_probabilities()

        # vote
        target = ask_player('\nWHOLE VILLAGE: Who do you lynch?\n   ')
        g.kill(target)

        input('(press ENTER to continue)')

        # check win
        if g.check_win():
            print("Game over")
            break


