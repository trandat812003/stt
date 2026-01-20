import re

def _load_single_words(path):
    single_words = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            tokens = line.split()

            # chỉ lấy dòng có đúng 1 từ
            if len(tokens) == 1:
                single_words.append(tokens[0])

    return single_words

dictionary_vi = _load_single_words("/home/trandat/Documents/stt/src/util/vietnam11K.txt")

def check_text(text: str) -> bool:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    words = text.lower().split(" ")
    words = text.split()

    for word in words:
        if word not in dictionary_vi:
            print(word)
            return False
    
    return True

if __name__ == "__main__":
    print(check_text("Tên Bờ rao ơ cúi sang nháy, mai đi à?"))