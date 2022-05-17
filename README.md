Quantum Werewolf is a game I created in Python a long time ago, which I uploaded to GitHub to share with friends.
I might one day upload a new version with better code and more roles.

Now, on to the actual game...

--- What is Quantum Werewolf? ---

Quantum Werewolf is a game based on the party game "The Werewolves of Millers Hollow" (known as "Weerwolven van Wakkerdam" to Dutch audiences) with a quantum mechanical twist.


--- What is "The Werewolves of Millers Hollow"? ---

The Werewolves of Millers Hollow is a classical party game where each player (save the game master) gets a secret role card assigned to them. There are two teams: the werewolves
and the village (consisting of all roles except the werewolves). At night, each player secretly takes an action corresponding to their role -- the seer gets to see another player's card,
Cupid can make two players fall in love, and the werewolves vote on who they will eat that night. During the day, all players vote on another player to be lynched.
The village's goal is to kill all werewolves, and the werewolves' goal is to kill all non-werewolves. When only one faction is left, they win.

--- What is the quantum twist? ---

The quantum twist introduced in Quantum Werewolf is a superposition of rolems. This means that every player is every role at once, and gets to take actions corresponding to all roles at night.
Of course, the superposition can be collapsed by measurements. Currently, there are two ways of measuring the superposition:
1. A player uses his Seer action to look at someone else's role, partially collapsing the superposition (and introducing entanglement!);
2. A player dies, which reveals his role to all players, collapsing the superposition quite a bit.

Since there is no way of knowing the final gamestate (in fact, your actions influence what the final measurement will be), it is important to players to "crack" the permutations
and try to make the superposition collapse in their favour. The game is very complex, and honestly isn't much fun to play with your grandma. However, it can be used as an
education tool for superpositions, or as a way to pit physicists against each other in cracking the code.

--- What are the rules? ---

The game can support any number of players, one of which must be the game master (or GM). The GM does not actively compete with the other players, but runs the game behind
the screens.
P: (Python script) players are added using the "player" command.
FE: (for example) Let us say that our game has 4 players, Alice, Bob, Craig and David, and one GM, Zack. In the Python script, Zack runs
"player(['Alice', 'Bob', 'Craig', 'David'])".

At the beginning of the game, all players (except the GM) are assigned a random ID number. Only the GM and the player can know someone's secret ID.
FE: Randomly, Alice is assigned to be player 1, Bob is player 2, Craig is player 3 and David is player 4. Only Alice and Zack can know that Alice is player 1 at this stage,
but the other players might figure out later on...

Using the deck of cards chosen by the GM (by default, 2 werewolves and 1 seer), all permutations of possible game states are generated.
FE: At the start of the game, the 12 possible permutations are (let w represent werewolf, s represent seer and v represent villager)

[s, w, w, v], [s, w, v, w], [s, v, w, w], [w, s, w, v], [w, s, v, w], [v, s, w, w], [w, w, s, v], [w, v, s, w], [v, w, s, w], [w, w, v, s], [w, v, w, s], [v, w, w, s].

The players are given how many possible permutations there are, and a table of probabilities on which roles they might have.
FE: Zack will show the players the following information:
There are 12 possible permutations left.

  Player    Villagers    Seer    Werewolf    Dead
__________________________________________________
       1         0.25    0.25         0.5       0
       2         0.25    0.25         0.5       0
       3         0.25    0.25         0.5       0
       4         0.25    0.25         0.5       0
P: The above few steps are automatically taken upon running "start()". You can set the deck using "deck".

Now the game can officially begin. It starts with a night phase

At night:
   Actions are taken in order of ID, although only the GM knows everyone's ID, so he may only commit the actions once everyone has submitted their targets.
   
 - Each player with a non-zero probability of being a seer can look at another player's role. All permutations where the acting player is a seer and the target is not
   the role seen by the seer are eliminated.
   
   P: this is realised using the "seer" command.
   
   FE: Alice looks at Bob's role, so Zack runs "seer('Alice', 'Bob')" and tells Alice she sees he is a werewolf. Permutation [s, v, w, w] gets removed from the superposition, since it is impossible.
   
 - Each player with a non-zero probability of being a werewolf can attempt to kill another player. All alive wolves in all permutations must do this at any point during the game in order for someone to be killed by wolves.
   
   P: this is realised using the "wolf" command.
   
   FE: Alice decides to kill Craig, so Zack runs "wolf('Alice', 'Craig')". This makes Craig 1/2 dead in all permutations in which Alice is a werewolf.
   
   N.B.: If the second wolf would die while Alice is still alive, it would not make Craig fully dead in the permutations in which Alice is the werewolf, and it stays at 1/2. If, however, Alice decides to attack Craig again, it would make him fully dead in those permutations.
   
 - After everyone had their actions, it becomes day.

At day:
   
 - The GM reveals whether anyone died during the night, and if they did, they will reveal the dead person's role. All permutations where he wasn't that role are removed.
   
   N.B.: A player can only die at night if he is fully dead in all permutations.
   
   P: This is realised automatically when probabilities are calculated via calcprobs().
   
 - The GM once again shows all players the table of probabilities, and the number of permutations left.
   
   FE: If nobody else took an action during the first night (which is impossible), the table would look like so:
   
   There are 11 possible permutations left.
   
     Player    Villagers      Seer    Werewolf      Dead
   ______________________________________________________
          1     0.272727  0.181818    0.545455  0
          2     0.181818  0.272727    0.545455  0
          3     0.272727  0.272727    0.454545  0.181818
          4     0.272727  0.272727    0.454545  0
   
    P: This is realised through running "results()".
    
  - All players who are still alive get to vote to lynch a player. That player instantly dies in all permutations, and his role is revealed.
    
    P: You may use the "kill" command for these purposes.
    
    FE: The town vote to lynch David. Zack runs "kill('David')", which reveals that he was a werewolf! All permutations in which David isn't a werewolf are eliminated.
    
  - It becomes night.
 
 
The game ends when in all permutations, only the werewolves are alive, only the village is alive or everyone has died. In the event of the game ending, all players who
are in the winning team (in all permutations) win. The superposition doesn't necessarily have to collapse fully for the game to end in a village win.

FE: if on the second day, Bob is lynched and revealed to be a werewolf, there are still the permutations [s, w, v, w] and [v, w, s, w] left!
Nonetheless, the town, consisting of Alice and Craig, wins!



I hope this explanation was clear. Feel free to contact me if you have any questions!
