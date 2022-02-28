import string
import collections
from letter_frequency_analyser import LetterFrequency


class WordleSolver:
    def __init__(self):
        freq = LetterFrequency()
        self.freq_weights = freq.freq_weights()
        self.wordlist_guesses = {}
        self.wordlist_solutions = {}

    def initialise_wordlists(self):
        print("_" * 50)
        self.wordlist_guesses = {
            key: list([0, 0, 0, 0, 0])
            for key in self.read_wordlist("wordlist_guesses.txt")
        }
        self.wordlist_solutions = dict(
            (k, [0, 0, 0, 0, 0]) for k in self.read_wordlist("wordlist_solutions.txt")
        )

        print("Wordlists initialised")
        print("_" * 50)

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
                # if the guess and the answer both contain more than one instance of the letter
                if sum([feedback[j] for j in range(5) if guess[j] == guess[i]]) > 1:
                    # add letter to every unfound place besides current one
                    for place in range(5):
                        if not (place == i or found[place]):
                            potential[place].add(guess[i])
                # add letter to every unfound place besides current one if letter found yet
                elif guess[i] not in found.values():
                    for place in range(5):
                        if not (place == i or found[place]):
                            potential[place].add(guess[i])
                ruled_out[i].add(guess[i])
            elif feedback[i] == 2:
                for place in range(5):
                    if guess[i] in potential[place]:
                        potential[place].remove(guess[i])
                potential[i].clear()
                found[i] = guess[i]

    def score_solutions(self, wordlist_solutions, ruled_out, potential, found):
        best = (None, float("-inf"), 0)
        bestlist_solutions = []
        potential_letters = set([c for place in potential for c in place])
        for word in wordlist_solutions.keys():
            if word in ["erode", "drove"]:
                debugscore = wordlist_solutions[word]
            for i in range(5):
                letter = word[i]
                if letter in ruled_out[i]:
                    wordlist_solutions[word][i] = -5
                if found[i] == letter:
                    wordlist_solutions[word][i] = 2
                elif letter in potential_letters:
                    wordlist_solutions[word][i] = 1
                # reduce score by 1 for number of repeated letters
                # wordlist_solutions[word][i] -= (word.count(letter) - 1) * 0.25
                # weight word according to letter frequency in english
                # freq_weight = self.freq_weights[letter]
                # wordlist_solutions[word][i] += freq_weight / 2
            score = sum(wordlist_solutions[word])
            if score > best[1]:
                bestlist_solutions.clear()
            if score >= best[1]:
                best = (word, score, score - best[1])
                bestlist_solutions.append(best)
                print(
                    f"Best solution: {best[0]}, Score: {best[1]}, Lead: {best[2]}"
                )  # for debugging
        print("Best List:", bestlist_solutions)
        return bestlist_solutions

    def score_guesses(self, wordlist_guesses, ruled_out, potential, found):
        best = (None, float("-inf"))
        for word in wordlist_guesses.keys():
            if word in ["forth", "nerol"]:
                debugscore = wordlist_guesses[word]
            for i in range(5):
                letter = word[i]
                wordlist_guesses[word][i] = 0  # reset score every guess
                if letter == found[i]:
                    wordlist_guesses[word][i] += -3
                elif letter in found.values():
                    wordlist_guesses[word][i] = -1
                if letter in potential[i]:
                    if letter != found[i]:
                        wordlist_guesses[word][i] += 2
                if letter in ruled_out[i]:
                    wordlist_guesses[word][i] += -10
                wordlist_guesses[word][i] -= word.count(letter) - 1
                # weight word according to letter frequency in english
                freq_weight = self.freq_weights[letter]
                wordlist_guesses[word][i] += freq_weight / 2
            if sum(wordlist_guesses[word]) >= best[1]:
                best = (word, sum(wordlist_guesses[word]))
                print(f"Best guess: {best[0]}, Score: {best[1]}")  # for debugging
        return best

    def score_guesses_narrow(
        self, wordlist_guesses, ruled_out, potential, found, bestlist_solutions
    ):
        best = (None, float("-inf"))
        ruled_out_letters = set([c for place in ruled_out for c in place])
        ruled_out_letters.update(set(found.values()))
        bestlist_solutions_letters = [
            letter
            for word in bestlist_solutions
            for letter in word[0]
            if letter not in ruled_out_letters
        ]
        narrowpool = set(
            [
                letter
                for letter in bestlist_solutions_letters
                if bestlist_solutions_letters.count(letter) < 3
            ]
        )
        for word in wordlist_guesses.keys():
            for i in range(5):
                letter = word[i]
                wordlist_guesses[word][i] = 0  # reset score every guess
                if letter == found[i]:
                    wordlist_guesses[word][i] += -1
                elif letter in found.values():
                    wordlist_guesses[word][i] += -3
                if letter in potential[i]:
                    if letter != found[i]:
                        wordlist_guesses[word][i] += 2
                if letter in narrowpool:
                    wordlist_guesses[word][i] += 4 / word.count(letter)
                if letter in ruled_out[i]:
                    wordlist_guesses[word][i] += -10
                wordlist_guesses[word][i] -= word.count(letter) - 1
                # weight word according to letter frequency in english
                freq_weight = self.freq_weights[letter]
                wordlist_guesses[word][i] += freq_weight / 2
            if sum(wordlist_guesses[word]) >= best[1]:
                best = (word, sum(wordlist_guesses[word]))
                print(
                    f"Best narrow guess: {best[0]}, Score: {best[1]}"
                )  # for debugging
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
        bestlist_solutions = self.score_solutions(
            wordlist_solutions, ruled_out, potential, found
        )
        best = bestlist_solutions[0]
        if guesscount == 5 or (
            best[1] >= 4 and best[2] >= 2 and len(bestlist_solutions) == 1
        ):
            # best[1] represents how sure the algorithm is that a solution is correct on scale 0-10
            return best[0]
        elif best[1] >= 5 and 1 < len(bestlist_solutions) < 6:
            best = self.score_guesses_narrow(
                wordlist_guesses, ruled_out, potential, found, bestlist_solutions
            )
            print("Narrow Guess:")
            return best[0]
        else:
            best = self.score_guesses(wordlist_guesses, ruled_out, potential, found)
            return best[0]

    def help(self):
        print("Commands: help, newgame, win, exit")
        print("Input SCORE according to letter colour as follows:")
        print("  Grey: 0\n  Yellow: 1\n  Green: 2")

    def execute(self,):
        current_game = True
        while current_game:
            self.initialise_wordlists()
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
                        self.wordlist_guesses,
                        self.wordlist_solutions,
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

    def logger(self):
        version = input("Version: ")
        description = input("Description: ")
        score = self.score()
        with open("Scores.txt", "a") as f:
            f.write(f"Version: {version}\nDescription: {description}\n")
            f.write(f"Average guesses to answer: {score}")

    def test(self):
        test = wordle_turtle.WordleSolver()
        for word in self.read_wordlist("wordlist_solutions.txt"):
            answer = word


if __name__ == "__main__":
    wordle_turtle = WordleSolver()
    wordle_turtle.execute()
