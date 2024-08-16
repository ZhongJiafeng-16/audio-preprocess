import itertools
import re
from loguru import logger
from phonemizer import phonemize

LANGUAGE_UNICODE_RANGE_MAP = {
    "ZH": [(0x4E00, 0x9FFF)],
    "JP": [(0x4E00, 0x9FFF), (0x3040, 0x309F), (0x30A0, 0x30FF), (0x31F0, 0x31FF)],
    "EN": [(0x0000, 0x007F)],  # ASCII码字符范围
    "AR":[(0x0600, 0x06FF), (0x0750, 0x077F)],
}

SYMBOLS_MAPPING = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "·": ",",
    "、": ",",
    "...": ".",
    "…": ".",
    "“": "'",
    "”": "'",
    "‘": "'",
    "’": "'",
    "（": "'",
    "）": "'",
    "(": "'",
    ")": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "～": "-",
    "~": "-",
    "・": "-",
    "「": "'",
    "」": "'",
    ";": ",",
    ":": ",",
    # ar
    "،": ",",
    "۔": ".",
    "؛": ",",
    "؟": "?",
    "«": "'",
    "»": "'",
}
PUNCTUATION = ''.join(set(list(SYMBOLS_MAPPING.values())))

REPLACE_SYMBOL_REGEX = re.compile(
    "|".join(re.escape(p) for p in SYMBOLS_MAPPING.keys())
)
ALL_KNOWN_UTF8_RANGE = list(
    itertools.chain.from_iterable(LANGUAGE_UNICODE_RANGE_MAP.values())
)
REMOVE_UNKNOWN_SYMBOL_REGEX = re.compile(
    "[^"
    + "".join(
        f"{re.escape(chr(start))}-{re.escape(chr(end))}"
        for start, end in ALL_KNOWN_UTF8_RANGE
    )
    + "]"
)

def is_text_in_language_ranges(text):
    unicode_ranges = ALL_KNOWN_UTF8_RANGE    
    for char in text:
        char_code = ord(char)
        if not any(start <= char_code <= end for start, end in unicode_ranges):
            return f"<{char}> is not available in LANGUAGE_UNICODE_RANGE_MAP"
        
    return None
        
def clean_and_phonemize_text(texts, lang):
    if not isinstance(texts, list):
        texts = [texts]
    
    clean_texts = []
    for text in texts:
        text = text.strip()
        # Replace all chinese symbols with their english counterparts
        text = REPLACE_SYMBOL_REGEX.sub(lambda x: SYMBOLS_MAPPING[x.group()], text)

        # Check char is available
        message = is_text_in_language_ranges(text)
        if not message is None:
            logger.warning(message)

        text = REMOVE_UNKNOWN_SYMBOL_REGEX.sub("", text)
        clean_texts.append(text)

    clean_texts = phonemize(
            clean_texts,
            language=lang,
            backend='espeak',
            strip=True,
            preserve_punctuation=True,
            punctuation_marks=PUNCTUATION,
        )
    return clean_texts
    

def clean_text(text):
    # Clean the text
    text = text.strip()
    # Replace all chinese symbols with their english counterparts
    text = REPLACE_SYMBOL_REGEX.sub(lambda x: SYMBOLS_MAPPING[x.group()], text)
    text = REMOVE_UNKNOWN_SYMBOL_REGEX.sub("", text)
    return text


if __name__ == '__main__':
    text = ['هل أكلت اليوم؟']
    
    for i, j in zip(clean_and_phonemize_text(text,'ar'), text):
        print(i);
        print(j);
        print('------------')
