import urllib
import requests_html
import logging

from collections import OrderedDict


def get_logging():

    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


def clean_word(word):
    return word.strip()


def get_meanings(word):
    """
    >>> "misleading" in " ".join(get_meanings("red herring"))
    True
    >>> "that feel when" in " ".join(get_meanings("tfw")).lower()
    True
    """
    sess = requests_html.HTMLSession()
    r = sess.get(
        "http://tratu.soha.vn/dict/en_vn/{}".format(
            urllib.parse.quote(word), timeout=10
        )
    )
    meaning_divs = r.html.xpath('//*[@id="content-5"]/h5/span')[1:]
    logger.debug('meaning_divs: %s', meaning_divs)
    if not meaning_divs:
        if "Tìm thêm với Google.com" in r.html.full_text:
            return []
        else:
            raise Exception("Unknown result for {}".format(word))

    return [node.text for node in meaning_divs]

def main():
    list_words = []
    while True:
        voca = input('VOCA>>>').strip()
        print('press y, yes, ok to start answer !')
        if voca in ['y', 'yes', 'ok', 'OK', 'n', 'no', 'start']:
            break
        list_words.append(voca)
    d = OrderedDict()
    counter = 0
    list_words = iter(list_words)
    while True:
        try:
            word = next(list_words)
            print(f"what meaning of {word} is:?")
            answer = input()
            meaning = get_meanings(word)
            print('meaning', meaning)
            if answer in meaning:
                d[word] = answer
                print("your are corect !")
            else:
                print('answer wrong !')
            counter += 1
        except StopIteration:
            print(f"finished with {counter} answer !!!")
            print('Your answer is:')
            for key, ans in d.items():
                print(key, ans)
            break


if __name__ == "__main__":
    logger = get_logging()
    logger.debug('Setup logger success !')
    print(get_meanings("Establish")[0])
    main()

