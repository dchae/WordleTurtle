class WordleSolver:
    def __init__(self):
        pass

    def read_wordlist(self, filename):
        wordlist = []
        with open(filename, "r") as f:
            for line in f:
                wordlist.append(line.strip())
        return wordlist

    def get_feedback(self, usrinput, guess, ruled_out, potential, found):
        feedback = [int(x) for x in usrinput]
        for i in range(5):
            if feedback[i] == 0:
                for place in ruled_out:
                    place.add(guess[i])
            elif feedback[i] == 1:
                for place in [x for x in range(5) if x != i]:
                    potential[place].add(guess[i])
                ruled_out[i].add(guess[i])
            elif feedback[i] == 2:
                found[i] = guess[i]

    def score_solutions(self, wordlist_solutions, ruled_out, potential, found):
        best = (None, float("-inf"))
        potential_letters = set([c for place in potential for c in place])
        for word in wordlist_solutions.keys():
            for i in range(5):
                letter = word[i]
                if letter in ruled_out[i]:
                    continue
                if found[i] == letter:
                    wordlist_solutions[word][i] = 2
                elif letter in potential_letters:
                    wordlist_solutions[word][i] = 1
            if sum(wordlist_solutions[word]) > best[1]:
                best = (word, sum(wordlist_solutions[word]))
                print(best)  # for debugging
        return best

    def score_guesses(self, wordlist_guesses, ruled_out, potential, found):
        best = (None, float("-inf"))
        # potential_letters = set([c for place in potential for c in place])
        for word in wordlist_guesses.keys():
            for i in range(5):
                letter = word[i]
                if letter == found[i]:
                    wordlist_guesses[word][i] += -2
                if letter in potential[i]:
                    wordlist_guesses[word][i] += -1
                if letter in ruled_out[i]:
                    wordlist_guesses[word][i] += -10
                wordlist_guesses[word][i] -= word.count(letter) + 1
            if sum(wordlist_guesses[word]) > best[1]:
                best = (word, sum(wordlist_guesses[word]))
                print(best)  # for debugging
        return best

    def bestguess(
        self,
        wordlist_guesses,
        wordlist_solutions,
        ruled_out,
        potential,
        found,
        guesscount,
    ):
        """
        Score each word in wordlist_solutions
        If there is not yet a word that has a perfect score
        Score each word in wordlist_guesses according to the letters it rules out
        Submit highest scoring guess
        """
        best = self.score_solutions(wordlist_solutions, ruled_out, potential, found)
        if guesscount == 5 or best[1] == 10:
            return best[0]
        best = self.score_guesses(wordlist_guesses, ruled_out, potential, found)
        return best[0]

    def help(self):
        print("Commands: help, newgame, exit")
        print("Input SCORE according to letter colour as follows:")
        print("  Grey: 0\n  Yellow: 1\n  Green: 2")

    def execute(self):
        while True:
            print("_" * 50)
            wordlist_guesses = {
                key: list([0, 0, 0, 0, 0])
                for key in self.read_wordlist("wordlist_guesses.txt")
            }
            wordlist_solutions = dict(
                (k, [0, 0, 0, 0, 0])
                for k in self.read_wordlist("wordlist_solutions.txt")
            )

            print("Wordlists initialised")
            print("_" * 50)
            self.help()
            potential = [set() for i in range(5)]
            ruled_out = [set() for i in range(5)]
            found = dict.fromkeys(range(5), "")
            guesscount = 0
            while True:
                if guesscount == 0:
                    guess = "raise"
                else:
                    guess = self.bestguess(
                        wordlist_guesses,
                        wordlist_solutions,
                        ruled_out,
                        potential,
                        found,
                        guesscount,
                    )
                print(f"Guess {guesscount+1}: {guess.upper()}")
                print("Input score per letter or command:")
                print(guess.upper())
                usrinput = input()
                if usrinput.isalpha():
                    command = usrinput.lower()
                    if command == "exit":
                        print("exiting...")
                        return
                    elif command == "help":
                        self.help()
                    elif command == "newgame":
                        break
                else:
                    self.get_feedback(usrinput, guess, ruled_out, potential, found)
                guesscount += 1


wordle_turtle = WordleSolver()
wordle_turtle.execute()
