import re
from underthesea import word_tokenize
# import cld3

# def detect_lang(text):
#     r = cld3.get_language(text)
#     if r is None:
#         return False
#     if r.language == "vi":
#         return True
#     return False

def _load_words(path):
    words = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip().lower()

            if not line:
                continue

            # tokens = line.split()

            # chỉ lấy dòng có đúng 1 từ
            # if len(tokens) == 1:
            #     words.append(tokens[0])
            words.append(line)

    # for i in range(38000):
    #     tokens = word_tokenize(words[i])
    #     if len(tokens) > 1:
    #         for token in tokens:
    #             words.append(token) 

    return words

dictionary_vi = _load_words("/home/trandat/Documents/stt/src/util/vietnam.txt")

dictionary_vi = set(dictionary_vi)

# with open("/home/trandat/Documents/stt/src/util/vietnam.txt", "w", encoding="utf-8") as ftmp:
#     for w in sorted(dictionary_vi):
#         ftmp.write(w + "\n")

def check_text(text: str) -> bool:
    text = text.lower()
    tokens = word_tokenize(text)
    # breakpoint()

    for token in tokens:
        text = re.sub(r"[^\w\s]", "", token, flags=re.UNICODE)
        if not text.strip():
            continue
        # print(text)
        # breakpoint()
        if text not in dictionary_vi:
            return False
    return True

def _check_text(text: str) -> bool:
    text = text.lower()
    tokens = word_tokenize(text)
    res = []

    for token in tokens:
        text = re.sub(r"[^\w\s]", "", token, flags=re.UNICODE)
        if not text.strip():
            continue
        if text not in dictionary_vi:
            res.append(text)
    return res

if __name__ == "__main__":
    print(check_text("Đầu năm cũng đã cùng với Bên khuyến nông khuyến lâm kết hợp Bên ủy ban đã chỉ đạo để bên khuyến nông khuyến lâm xuống tuyên truyền bà con nhân dân."))