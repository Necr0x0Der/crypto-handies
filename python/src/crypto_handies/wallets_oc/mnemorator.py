#
#Copyright (c) 2025 Necr0x0Der
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from mnemonic import Mnemonic
from random import shuffle, randint

def _to_word_list(words):
    return words.split(' ') if isinstance(words, str) else words


class Mnemorator:
    '''
    Wrapper over Mnemonic for executing different stategies
    for generating mnemonic phrases
    '''

    def __init__(self, language = "english"):
        self.mnemo = Mnemonic(language)

    def gen_prefer(self, words_top, words_other, min_count=8, strength=128, max_tries=10**6):
        '''
        Generate random mnemonic phrases and count the number of
        preferred words in them (words_top are taken with weight 2).
        
        This is quite a simple strategy, but it can be a good start to
        explore various mnemonics.

        There can be too many or too few accepted results, which can be
        control by the number of preferred words and min_count.

        For example, 20 words_top and 120 words_other words with min_count=8
        give several results in 10**6 attempts. If fewer words are used,
        min_count should also be decreased.
        '''
        for _ in range(max_tries):
            words = self.mnemo.generate(strength=strength)
            splt = words.split(' ')
            cnt = 0
            for w in splt:
                if w in words_other:
                    cnt += 1
                if w in words_top:
                    cnt += 2
            if cnt > min_count:
                yield (words, cnt)

    def _fill_rec(self, words, ws):
        if len(ws) == 0:
            if self.mnemo.check(words):
                yield words
            return
        if ws[0] != '?':
            if len(words) == 0:
                yield from self._fill_rec(ws[0], ws[1:])
            else:
                yield from self._fill_rec(words + ' ' + ws[0], ws[1:])
            return
        for w in self.mnemo.wordlist:
            if len(words) == 0:
                yield from self._fill_rec(w, ws[1:])
            else:
                yield from self._fill_rec(words + ' ' + w, ws[1:])

    def fill_words(self, words, max_count=200):
        '''
        Accept a seed phrase with some words replaced with ?
        and systematically enumerate possible substitutions
        for '?'s from Mnemonic.wordlist checking if the mnemonic
        is correct. Yield all the result up to max_count.

        max_count=-1 will generate all possibilities

        It can useful for different scenarios:
        - You remember the phrase, but not precisely, so
          you replace the words you are not sure in with ?
        - You wrote a poetic mnemonic phrase, but it is
          invalid, so you replace one word with ? and
          choose the most suitable correct phrase
        
        More than one word can be replaced with ?, but
        there can be too many valid alternatives, so
        additional filtering can be needed in this case
        '''
        words = _to_word_list(words)
        for mnem in self._fill_rec('', words):
            yield mnem
            if max_count == 0:
                break
            max_count -= 1

    def shuffle_words(self, words, phrase_length=12, max_out=20, max_shuffle=1000):
        '''
        Try to find valid mnemonic by shuffling words from the provided list.
        Can be useful if you don't remember the order in your mnemonic phrase,
        or just want to generate a phrase made up of specific words.

        The number of words can be 
        - equal to phrase_length - exactly these words will appear in all phrases
        - greater than phrase_length - different words but only from this list
          will be in all phrases
        - lesser than phrase_length - missing words will be found by fill_words;
          however, if more than one word is missing, all (except last) missing
          words will be taken from the beginning of the alphabet
        '''
        words = _to_word_list(words)
        cnt_fill = phrase_length - len(words)
        if cnt_fill > 0:
            words += '?' * cnt_fill
        for _ in range(max_shuffle):
            if max_out == 0:
                break
            # It is ok to call fill_words without ? - it will return
            # input words if they constitute correct mnemonic phrase,
            # otherwise it will return nothing
            _words = words.copy()
            shuffle(_words)
            phrases = self.fill_words(_words[:phrase_length])
            phrases = [] if phrases is None else list(phrases)
            if len(phrases) > 0:
                yield phrases[randint(0, len(phrases)-1)]
                max_out -= 1
