import sys, os, json
import srt
import codecs
import re
from collections import Counter
from deep_translator import GoogleTranslator
import genanki
import spacy


class FlashcardMaker:

    # get args for the subtitle file and destination file
    def __init__(self, srt_path):
        self.SRT_PATH = srt_path 
        if srt_path[-4:] == ".srt":
            # todo use os to get filename
            self.SRT_FN = srt_path[4:-4]
        else:
            raise Exception(f"{srt_path} doesn't look like a srt file")
        self.TRANSLATION_DICT_PATH = "dest/" + self.SRT_FN + ".txt"

        self.translator = GoogleTranslator(source='de', target='en')
        self.nlp = spacy.load("de_core_news_sm")
        self.GENDER_DICT = {"Fem": "die", "Masc": "der", "Neut": "das"}

    # get all the words from the subtitle file and save in dict with counts
    def make_subtitle_word_count(self):
        with codecs.open('./' + self.SRT_PATH, 'r', encoding='utf-8-sig', errors='ignore') as f:
            self.subtitles = Subtitles(self.SRT_PATH)
            file_content = f.read()
            try:
                self.subtitles.set_file_content(file_content)
                self.subtitles.parse_subtitles()
            except Exception as e:
                raise Exception(self.SRT_PATH + " wasn't correctly parsed into subtitles because " + str(e))

        lines = [char.lower() for char in " ".join(self.subtitles).split(" ") if char.isalpha()]
        self.vocab_word_count = Counter(lines)

    # get translation of words
    def make_translations(self):

        # check if you've already got translations for any words
        if os.path.isfile(self.TRANSLATION_DICT_PATH):
            print("opening the translation dict")
            with open(self.TRANSLATION_DICT_PATH, 'r', encoding="utf-8") as f:
                self.translation_dict = json.loads(f.read())
        else:
            self.translation_dict = {}


        for word in self.vocab_word_count:

            # only keep words for parts of speech you're interested in
            spacy_token = self.nlp(word)[0]
            if spacy_token.pos_ in ["AUX", "VERB", "NOUN", "ADJ", "ADV"]:

                # get the lemma of this word
                # for example, if the word is "bin", you'll be
                # using "sein"
                lemma = spacy_token.lemma_


                # if the lemma is a noun, get the gender and add die/der/das
                if spacy_token.pos_ == "NOUN":
                    print(lemma)
                    gender = spacy_token.morph.get("Gender")
                    if gender:
                        lemma = self.GENDER_DICT[gender[0]] + " " + lemma

                # check if you already have a translation for this word, 
                # like maybe you got partway through translations on this
                # file already
                if not self.translation_dict.get(lemma):

                    self.translation_dict[lemma] = self.translator.translate(lemma)
                    print(lemma, self.translation_dict[lemma])

        # write to file
        with open(self.TRANSLATION_DICT_PATH, 'w', encoding="utf-8") as f:
            f.write(json.dumps(self.translation_dict))


    # print words and translations into anki format for flashcards
    def make_anki_deck(self):
        anki_deck = genanki.Deck(
            2059400110,
            "subtitle vocab: " + self.SRT_FN)

        anki_model = genanki.Model(
            1607392319,
            'Simple Model',
            fields=[
              {'name': 'Movie Language'},
              {'name': 'Answer Language'},
            ],
            templates=[
              {
                'name': 'Card 1',
                'qfmt': '{{Movie Language}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer Language}}',
              },
            ])

        for word in self.translation_dict:
            note = genanki.Note(
                model=anki_model,
                fields=[word, self.translation_dict[word]])
            anki_deck.add_note(note)

        genanki.Package(anki_deck).write_to_file(f"dest/{self.SRT_FN}.apkg")




class Subtitles():
    def __init__(self, filename):
        self.filename = filename
        self.lines = []
        
        # as per recommendation from @freylis, compile once only
        # https://stackoverflow.com/questions/9662346/python-code-to-remove-html-tags-from-a-string
        self.CLEANR = re.compile('<.*?>') 

    def cleanhtml(self, raw_html):
        cleantext = re.sub(self.CLEANR, '', raw_html)
        return cleantext

    def __getitem__(self, item):
        return self.lines[item].content

    def set_file_content(self, file_content):
        self.file_content = file_content

    def parse_subtitles(self):
        self.lines = list(srt.parse(self.file_content))
        for line in self.lines:
            line.content = self.cleanhtml(line.content)


# would be nice, but probably not possible with subtitle files:

        # get the noun chunks from the sentence and get lemma

        # if there's a word marked ADP (adposition) at the end of a sentence,
        # see if it might be a separable verb and can fit with a verb earlier in the sentence

# todo get gender of nouns - done
