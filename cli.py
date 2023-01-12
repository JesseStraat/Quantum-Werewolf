from os import system
from quantumwerewolf import Game

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

    system('clear')

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

    system('clear')

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

    system('clear')

    # Start game
    g.start()

    # loop turns for every player
    turn_counter = 0
    while g.started == True:
        turn_counter += 1
        # night
        system('clear')
        print('Night falls and all players take their actions in turns privately\n')

        start_probabilities = g.probs

        for i, p in enumerate(g.players):
            if g.killed[i] == 1:
                continue

            input("{}'s turn (press ENTER to continue)".format(p))
            system('clear')
            print("{}'s turn".format(p))

            # display game and player info (role superposition)
            player_probabilities = start_probabilities[i]
            print('\n  Your role:')
            print("    Villager: {:3.0f}%".format(100*player_probabilities['villager']))
            print("    Seer:     {:3.0f}%".format(100*player_probabilities['seer']))
            print("    werewolf: {:3.0f}%\n".format(100*player_probabilities['werewolf']))

            # seer
            if player_probabilities['seer'] != 0:
                target = ask_player('  SEER: Whose role do you inspect?\n   ')
                g.seer(p,target)

            # werewolf
            if player_probabilities['werewolf'] != 0:
                target = ask_player('  WEREWOLF: Who do you attack?\n   ')
                g.werewolf(p,target)

            input("\n(press ENTER to continue)")

            system('clear')

        # day
        input('All player have had their turn (press ENTER to continue)')
        system('clear')
        print('The day begins')

        g.print_probabilities()

        # vote
        target = ask_player('\nWHOLE VILLAGE: Who do you lynch?\n   ')
        g.kill(target)

        input('(press ENTER to continue)')

        # check win
        if g.check_win():
            print("Game over")
            break



