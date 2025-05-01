from crypto_handies import Mnemorator

m = Mnemorator()

# We take 20 words as words_top and 120 as words_other
# from Mnemonics.wordlist just for demonstration purposes.
# Use you own words (from wordlist) to get results you'll like.
print("\n========== Generating mnemonics containing preferred words ==========")
for (w, c) in m.gen_prefer(
        words_top=m.mnemo.wordlist[:20],
        words_other=m.mnemo.wordlist[20:140]):
    print(f"{c} : {w}")

# We take 12 (alphabetically) first words for demonstration purpose
# and replace 11th word with ?. Then, first 20 valid mnemonic phrases
# following this pattern are produced
print("\n========== Generating mnemonics by filling in missed words ==========")
words = m.mnemo.wordlist[:12]
words[-2] = '?'
print(f"Pattern: {' '.join(words)}")
for r in m.fill_words(words, max_count=20):
    print(r)

print("\n========== Generating mnemonics by shuffling given words ==========")
print(">>> Shuffling 12 words - the same words will be in all phrases <<<")
print('\n'.join(m.shuffle_words(m.mnemo.wordlist[:12], max_out=3)))
print(">>> Shuffling 15 words - only they will be in all phrases <<<")
print('\n'.join(m.shuffle_words(m.mnemo.wordlist[:15], max_out=3)))
print(">>> Shuffling 11 words - one word will be randomly inserted <<<")
print('\n'.join(m.shuffle_words(m.mnemo.wordlist[:11], max_out=3)))
