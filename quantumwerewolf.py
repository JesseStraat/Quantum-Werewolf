from sympy.utilities.iterables import multiset_permutations
from tabulate import tabulate
import numpy as np
import random

class Game:

    def __init__(self):
        self.players = []               # List of player names
        self.role_count= [2, 1]         # [werewolves, seers]
        self.player_count = 10          # This variable is to be used if no names are specified
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
    def set_deck(self, roles):
        # roles: [werewolves, seers]
        self.role_count = roles

    # Identify the player names with their IDs
    def identify_players(self):
        idfy = [[i+1, self.players[i]] for i in range(len(self.players))]
        print(tabulate(idfy, headers = ["ID", "Name"]))

    # Start the game
    def start(self):
        if self.check_started(False):

            # Shuffling the player order
            random.shuffle(self.players)

            # Determine playercount or generate players if none are given
            if self.players != []:
                self.player_count = len(self.players)
            else:
                self.players = ["Player " + str(x+1) for x in range(self.player_count)]

            # Determine (valid) amount of villager in the game
            villagers = self.player_count - sum(self.role_count)
            if villagers < 0:
                print("Too few players, decrease the amount of roles!")
                return

            # Sets the list of roles
            roles = self.role_count[0] * ["w"] + self.role_count[1] * ["s"] + villagers * ["v"]
            self.werewolf_count = self.role_count[0]

            # Generates the list of all role permutations
            self.perms = list(multiset_permutations(roles))

            # Set all players to be fully alive
            self.deaths = []
            for i in range(self.player_count):
                self.deaths += [[0] * self.player_count]
            self.killed = [0] * self.player_count

            # Tell the game master which player corresponds to which ID
            self.identify_players()

            # start game
            self.started = True
            print("Game started.")

            # Generate table of probabilities
            self.get_probabilities()

    # Stop the game
    def stop(self):
        if self.check_started():
            self.started = False
            print("Game stopped.")

    # Reset the game
    def reset(self):
        self.players = []
        self.role_count= [2,1]
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
        return self.players.index(player_name) + 1

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
            print("There are {} possible permutations left.".format(self.nperm))
            print()
            print(tabulate(self.probs, headers = ["Player", "Villagers", "Seer", "Werewolf", "Dead"]))


    # Calculates the probabilities
    def calculate_probabilities(self):
        if self.check_started():
            self.nperm = len(self.perms)
            permt = np.array(self.perms).T.tolist()
            probst = []
            for i in range(self.player_count):
                probst.append([i+1, permt[i].count("v")/self.nperm, permt[i].count("s")/self.nperm, permt[i].count("w")/self.nperm, self.death_probability(self.players[i])])
            self.probs = probst

    # Let a player commit his seer action
    def seer(self, seer, target):
        # seer: name of the seer
        # target: name of the target of the seer
        if self.check_started():
            seer = self.ID(seer)
            target = self.ID(target)
            if self.probs[seer-1][1] == 0:
                # Someone may only do his seer action if he can possibly be one (to save time)
                print("Error: {}'s seer probability is 0.".format(self.players[seer-1]))
            elif self.killed[seer-1] == 1:
                # You can't take an action if you're dead
                print("Error: seer {} is dead.".format(self.players[seer - 1]))
            else:
                # Player is allowed to commit the action
                print("{} is investigating {} ...".format(self.players[seer-1], self.players[target-1]))
                list = []
                for p in self.perms:
                    if p[seer-1] == "s":
                        list.append(p)

                # Choose an outcome
                res = random.choice(list)

                # Collapse the wave function
                for p in list:
                    if p[target-1] != res[target-1]:
                        self.perms.remove(p)

                # Report on results
                print("{} sees that {} is a {}!".format(self.players[seer-1], self.players[target-1], self.role(res[target-1])))
                self.calculate_probabilities()

    # Force someone's death (e.g., after a vote). Otherwise used only by script
    def kill(self, target):
        # target: the name of the target
        if self.check_started():
            print("{} was killed!".format(target))

            # Chooses an outcome
            res = random.choice(self.perms)
            prole = res[self.ID(target)-1]
            permt = list(self.perms)

            # Collapse the wave function
            for p in permt:
                if p[self.ID(target)-1] != prole:
                    self.perms.remove(p)

            # Report on results
            print("{} was a {}!".format(target, self.role(prole)))

            # Deal with the case that the dead person is a werewolf
            if self.role(prole) == "w":
                self.werewolf_count -= 1
                for p in self.perms:
                    for i in range(self.player_count):
                        p[i+self.player_count][self.ID(target)-1] = 0

            self.killed[self.ID(target)-1] = 1
            self.calculate_probabilities()

    # Shows the probability of death for some player
    def death_probability(self, name):
        # name: name of player
        if self.check_started():
            dead = 0
            if self.killed[self.ID(name) - 1] == 1:
                dead = 1
            else:
                deathn = 0
                for p in self.perms:
                    for i in range(self.player_count):
                        if p[i] == "w" and p[self.ID(name)-1] != "w":
                            deathn += self.deaths[self.ID(name)-1][i]
                dead = deathn/len(self.perms)
                if dead >= 1:
                    self.kill(name)
            return dead

    # Lets someone commit their wolf action
    def wolf(self, wolf, target):
        # wolf: the name of the wolf
        # target: the name of the wolf's target
        if self.check_started():
            if self.killed[self.ID(wolf)-1] == 1:
                print("Error: wolf {} is dead".format(wolf))
            else:
                self.deaths[self.ID(target) - 1][self.ID(wolf) - 1] = 1/self.werewolf_count
                print("{} has mauled {}!".format(wolf, target))


if __name__ == "__main__":
    g = Game()

