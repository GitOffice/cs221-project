# English-Chinese Name Machine Transliteration Using Search and Neural Network Models
Approximate transcription of English names (or names written with Latin characters using English phonetics) into Chinese pinyin.

We put every test in its own file in the scripts directory. To run any test, you should be able to run `python <filename> eval` to generate the results in the paper. (Note that entire evaluations take a little while to run). If you want to just play around with how a certain method translates certain names, you can run `python <filename>` and it should prompt for the name.

Some example filenames:
* Baseline: `baseline.py`
* Edit Distance Search: `search.py`
* Edit Distance Search with Phoneme-Adjustment: `search_phonememod.py`
* Co-occurrence Table Search: `ngrams_search.py`
* Character Decoding DL: `model.py`
* Syllable Decoding DL: `model_syll.py`

To investigate the seq2seq models we used more closely, you can find them in the notebooks directory. These are in the Jupyter Notebooks:
* Character Decoding DL: `Translation with Pytorch Tutorial.ipynb`
* Syllable Decoding DL: `Transliteration Pytorch-Syllables.ipynb`
* Character Decoding From Search DL: `Translation with Pytorch Tutorial Search as Input.ipynb`
* Syllable Decoding From Search DL: `Transliteration Pytorch-Syllables Search as Input.ipynb`

All code is written in with Python3.6
