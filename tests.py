import unittest
from subs_to_flashcards import FlashcardMaker

SUB_PATH = "src/goodbye_lenin.deu.srt"

class TestFlashcardMaker(unittest.TestCase):
    def test_gets_first_line(self):
        fm = FlashcardMaker(SUB_PATH)
        fm.make_subtitle_word_count()
        assert fm.subtitles[0] == "Untertitel: WDR mediagroup GmbH\nim Auftrag des WDR"

    def test_gets_a_count(self):
        fm = FlashcardMaker(SUB_PATH)
        fm.make_subtitle_word_count()
        assert fm.vocab_word_count["und"] > 0

    def test_removes_punctuation(self):
        fm = FlashcardMaker(SUB_PATH)
        fm.make_subtitle_word_count()
        assert fm.vocab_word_count.get("sind...") == None 

    def test_translate_words(self):
        fm = FlashcardMaker(SUB_PATH)
        fm.make_subtitle_word_count()
        fm.make_translations()
        assert fm.translation_dict["sind"] == "are"

    def test_make_anki_deck(self):
        fm = FlashcardMaker(SUB_PATH)
        fm.make_subtitle_word_count()
        fm.make_translations()
        fm.make_anki_deck()
        assert "made" == "deck"



