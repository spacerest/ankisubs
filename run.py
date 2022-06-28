from subs_to_flashcards import FlashcardMaker
import sys

SUB_PATH = sys.argv[1]

fm = FlashcardMaker(SUB_PATH)
fm.make_subtitle_word_count()
fm.make_translations()
fm.make_anki_deck()