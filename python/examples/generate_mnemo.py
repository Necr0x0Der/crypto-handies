from crypto_handies import Mnemorator

m = Mnemorator()

# We take 20 words as words_top and 120 as words_other
# from Mnemonics.wordlist just for demonstration purposes.
# Use you own word lists to get results you'll like.
for (w, c) in m.gen_prefer(
        words_top=m.mnemo.wordlist[:20],
        words_other=m.mnemo.wordlist[20:140]):
    print(f"{c} : {w}")
