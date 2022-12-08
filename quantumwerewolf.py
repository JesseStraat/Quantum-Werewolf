from sympy.utilities.iterables import multiset_permutations as mp
from tabulate import tabulate
import numpy as np
import random




names = []              # List of names
rolecount= [2, 1]       # [werewolves, seers]
players = 10            # This variable is to be used if no names are specified



def player(name):       # Adds a player to the game
    # name: the name (or list of names) of the player(s) to add
    
    def addplayer(name: str):   #The actual function that adds the player
        if isinstance(name, str):
            if name in names:
                print("Player {} already exists!".format(name))
            else: names.append(name)
        else: print("Wrong data type: {}, must be either string or list of strings".format(type(name)))
    
    if checkstarted(False):
    # The game can't be ongoing
        if isinstance(name, list):
        # Allows one to add a list of names at once
            for n in name:
                addplayer(n)
        
        elif isinstance(name, str):
            addplayer(name)
        
        else: print("Wrong data type: {}, must be either string or list of strings".format(type(name)))

def deck(roles):        # Lets you set the contents of the deck
    # roles: [werewolves, seers]
    global rolecount
    rolecount = roles

def idfy():             # Identifies the player names with their IDs
    idfy = [[i+1, names[i]] for i in range(len(names))]
    print(tabulate(idfy, headers = ["ID", "Name"]))

def start():            # Starts the game
    if checkstarted(False):
        global nww
        global names
        global players
        global perms
        global roles
        global started
        global killed
        global deaths
        
        # Shuffling the player order
        random.shuffle(names)
        
        if names != []: players = len(names)
        else: names = ["Player " + str(x+1) for x in range(players)]
        
        
        villagers = players - sum(rolecount)
        
        if villagers < 0: print("Too little players, decrease the amount of roles!"); return
        
        # Sets the list of roles
        roles = rolecount[0] * ["w"] + rolecount[1] * ["s"] + villagers * ["v"]
        
        nww = rolecount[0]
        
        # Generates the list of all role permutations
        perms = list(mp(roles))
        
        deaths = []
        for i in range(players):
            deaths += [[0] * players]
        
        # Tell the game master which player corresponds to which ID
        idfy()
        
        started = True
        
        killed = [0] * players
        
        print("Game started.")
        
        # Generate table of probabilities
        results()


def stop():             # Stops the game (duh)
    if checkstarted():
        global started
        
        started = False
        
        print("Game stopped.")


def reset():            # Resets the game (duh)
    global names
    global rolecount
    names = list(dnames)
    rolecount= list(drole)
    if started == True: stop()
    print("Game reset.")

def checkstarted(boolean = True):
    # boolean: set this to false if you want to check if you HAVEN'T started yet
    # The point of this function is to throw an error if the game hasn't started yet
    if started == boolean: return True
    else:
        if boolean: print("Please start the game first with start()."); return False
        else: print("Please stop the game first with stop()."); return False


def num(name):          # Returns the ID corresponding to someone's name
    #name: the name of the player
    return names.index(name) + 1


def role(letter):       # Returns the role corresponding to some letter
    # letter: the letter who's corresponding role you want to know
    roles = ["villager", "werewolf", "seer"]
    letters = ["v", "w", "s"]
    return roles[letters.index(letter)]

def results():          # Gives the table of probabilities
    if checkstarted():
        calcprobs()
        print("There are {} possible permutations left.".format(nperm))
        print()
        print(tabulate(probs, headers = ["Player", "Villagers", "Seer", "Werewolf", "Dead"]))

        
def calcprobs():        # Calculates the probabilities
    if checkstarted():
        global probs
        global nperm
        nperm = len(perms)
        permt = np.array(perms).T.tolist()
        probst = []
        for i in range(players):
            probst.append([i+1, permt[i].count("v")/nperm, permt[i].count("s")/nperm, permt[i].count("w")/nperm, deathp(names[i])])
        probs = probst

def seer(seer, target): # Lets a player commit his seer action
    # seer: name of the seer
    # target: name of the target of the seer
    if checkstarted():
        seer = num(seer)
        target = num(target)
        if probs[seer-1][1] == 0:
        # Someone may only do his seer action if he can possibly be one (to save time)
            print("Error: {}'s seer probability is 0.".format(names[seer-1]))
        elif killed[seer-1] == 1:
        # You can't take an action if you're dead
            print("Error: seer {} is dead.".format(names[seer - 1]))
        else:
        # Player is allowed to commit the action
            print("{} is investigating {} ...".format(names[seer-1], names[target-1]))
            list = []
            for p in perms:
                if p[seer-1] == "s":
                    list.append(p)
            
            # Choose an outcome
            res = random.choice(list)
            
            # Collapse the wave function
            for p in list:
                if p[target-1] != res[target-1]:
                    perms.remove(p)
            
            # Report on results
            print("{} sees that {} is a {}!".format(names[seer-1], names[target-1], role(res[target-1])))
            calcprobs()


def kill(target):       # Forces someone's death (e.g., after a vote). Otherwise used only by script
    # target: the name of the target
    if checkstarted():
        global killed
        global nww
        global perms
        print("{} was killed!".format(target))
        
        # Chooses an outcome
        res = random.choice(perms)
        prole = res[num(target)-1]
        permt = list(perms)
        
        # Collapse the wave function
        for p in permt:
            if p[num(target)-1] != prole: perms.remove(p)
        
        # Report on results
        print("{} was a {}!".format(target, role(prole)))
        
        # Deal with the case that the dead person is a werewolf
        if role(prole) == "w":
            nww -= 1
            for p in perms:
                for i in range(players):
                    p[i+players][num(target)-1] = 0
        
        killed[num(target)-1] = 1
        calcprobs()
        
def deathp(name):       # Shows the probability of death for some player
    # name: name of player
    if checkstarted():
        dead = 0
        if killed[num(name) - 1] == 1:
            dead = 1
        else:
            deathn = 0
            for p in perms:
                for i in range(players):
                    if p[i] == "w" and p[num(name)-1] != "w":
                        deathn += deaths[num(name)-1][i]
            dead = deathn/len(perms)
            if dead >= 1:
                kill(name)
        return dead


def wolf(wolf, target):     # Lets someone commit their wolf action
    # wolf: the name of the wolf
    # target: the name of the wolf's target
    if checkstarted():
        if killed[num(wolf)-1] == 1:
            print("Error: wolf {} is dead".format(wolf))
        else:
            deaths[num(target) - 1][num(wolf) - 1] = 1/nww
            print("{} has mauled {}!".format(wolf, target))

    

dnames = list(names)
drole = list(rolecount)

started = False



#Debugging:

debugnames = ["a", "b", "c", "d", "e", "f"]



def testperms():
    print(perms)

def testdeaths():
    print(deaths)
