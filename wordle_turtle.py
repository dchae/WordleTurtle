import string
from letter_frequency_analyser import LetterFrequency


class WordleSolver:
    def __init__(self):
        freq = LetterFrequency()
        self.freq_weights = freq.freq_weights()

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
                for place in range(5):
                    if not (place == i or found[place]):
                        potential[place].add(guess[i])
                ruled_out[i].add(guess[i])
            elif feedback[i] == 2:
                potential[i].clear()
                ruled_out[i].update(
                    set(
                        letter
                        for letter in string.ascii_lowercase
                        if letter != guess[i]
                    )
                )
                found[i] = guess[i]

    def score_solutions(self, wordlist_solutions, ruled_out, potential, found):
        best = (None, float("-inf"))
        potential_letters = set([c for place in potential for c in place])
        for word in wordlist_solutions.keys():
            for i in range(5):
                letter = word[i]
                if letter in ruled_out[i]:
                    wordlist_solutions[word][i] = -1
                if found[i] == letter:
                    wordlist_solutions[word][i] = 2
                elif letter in potential_letters:
                    wordlist_solutions[word][i] = 1
                # weight word according to letter frequency in english
                # freq_weight = self.freq_weights[letter]
                # wordlist_solutions[word][i] += freq_weight / 2
            if sum(wordlist_solutions[word]) >= best[1]:
                best = (word, sum(wordlist_solutions[word]))
                print(f"Best solution: {best[0]}, Score: {best[1]}")  # for debugging
        return best

    def score_guesses(self, wordlist_guesses, ruled_out, potential, found):
        best = (None, float("-inf"))
        for word in wordlist_guesses.keys():
            for i in range(5):
                letter = word[i]
                if letter == found[i]:
                    wordlist_guesses[word][i] += -3
                elif letter in found.values():
                    wordlist_guesses[word][i] += -1.25
                if letter in potential[i]:
                    wordlist_guesses[word][i] += 2
                if letter in ruled_out[i]:
                    wordlist_guesses[word][i] += -10
                wordlist_guesses[word][i] -= word.count(letter) - 1
                # weight word according to letter frequency in english
                freq_weight = self.freq_weights[letter]
                wordlist_guesses[word][i] += freq_weight
            if sum(wordlist_guesses[word]) >= best[1]:
                best = (word, sum(wordlist_guesses[word]))
                print(f"Best guess: {best[0]}, Score: {best[1]}")  # for debugging
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
        if guesscount == 5 or best[1] > 5:
            # best[1] represents how sure the algorithm is that a solution is correct on scale 0-10
            return best[0]
        best = self.score_guesses(wordlist_guesses, ruled_out, potential, found)
        return best[0]

    def help(self):
        print("Commands: help, newgame, win, exit")
        print("Input SCORE according to letter colour as follows:")
        print("  Grey: 0\n  Yellow: 1\n  Green: 2")

    def execute(self):
        current_game = True
        while current_game:
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
                if guesscount > 5:
                    print("Loading new game...")
                    print("...\n" * 3)
                    break
                elif guesscount == 0:
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

                taking_input = True
                while taking_input:
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
                        elif command in ["newgame", "win"]:
                            current_game = False
                            break
                        else:
                            print("Not a valid command. Try 'help'.")
                            continue
                    else:
                        self.get_feedback(usrinput, guess, ruled_out, potential, found)
                        taking_input = False
                if current_game == False:
                    break
                guesscount += 1
            current_game = True


if __name__ == "__main__":
    wordle_turtle = WordleSolver()
    wordle_turtle.execute()
