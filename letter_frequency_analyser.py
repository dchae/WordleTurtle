import collections


class LetterFrequency:
    def read_wordlist(self, filename):
        letterlist = []
        with open(filename, "r") as f:
            for line in f:
                letterlist.extend(line.strip())
        return letterlist

    def frequency(self, letterlist):
        freq = collections.Counter(letterlist)
        return freq

    def freq_weights(self):
        letterlist = self.read_wordlist("wordlist_solutions.txt")
        freq = self.frequency(letterlist)
        ordered = [x[0] for x in freq.most_common()]
        weights = [(c, (25 - i) / 25) for i, c in enumerate(ordered)]
        return dict(weights)


if __name__ == "__main__":
    test = LetterFrequency()
    print(test.freq_weights())

