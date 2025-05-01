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
