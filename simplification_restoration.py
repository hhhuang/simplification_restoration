class SR():
    def __init__(self, dictionary, word_matching=True):
        self.dictionary = dictionary
        self.max_len = max([len(w) for w in self.dictionary])
        self.word_matching = word_matching

    def match(self, text, offset):
        """In the word matching mode, a match will not be a subword segment."""
        if self.word_matching:
            if offset != 0 and text[offset-1].isalnum():
                return None, None

        """Longest first matching from left to right."""
        for width in range(self.max_len, 0, -1):
            if self.word_matching:
                if offset+width < len(text) and text[offset+width].isalnum():
                    continue
            haystack = text[offset:offset+width]
            if haystack in self.dictionary:
                return haystack, self.dictionary[haystack]
        return None, None

    def simplify(self, text):
        inv_indexes = []
        result = []
        i = 0
        while i < len(text):
            m, r = self.match(text, i) 
            if m is None:
                result.append(text[i])
                inv_indexes.append(i)
                i += 1
            else:
                inv_indexes.append(i)
                inv_indexes += [-1]*(len(r)-1)
                result += list(r)
                i += len(m)
        return "".join(result), inv_indexes

    def restore(self, simplified, original, inv_indexes):
        return self.extract_restore(simplified, original, inv_indexes, 0, len(inv_indexes))

    def extract_restore(self, simplified, original, inv_indexes, begin, end):
        while begin > 0 and inv_indexes[begin] == -1:
            begin -= 1
        while end < len(inv_indexes) and inv_indexes[end] == -1:
            end += 1
        result = []
        offset = None
        for i in range(begin, end):
            #print("(%d, %s, %s)" % (inv_indexes[i], simplified[i], original[inv_indexes[i]]))
            if inv_indexes[i] == -1:
                if i > 0 and inv_indexes[i-1] != -1:
                    offset = inv_indexes[i-1] + 1
            elif i > 0 and inv_indexes[i-1] == -1:
                result += list(original[offset:(inv_indexes[i])+1])
                offset = None
            else:
                result.append(original[inv_indexes[i]])
        if offset:
            if end < len(inv_indexes):
                result += list(original[offset:inv_indexes[end]])
            else:
                result += list(original[offset:])
        return "".join(result)


if __name__ == "__main__":
    dictionary = {'lung cancer': 'disease', 'fever': 'symptom', 'aspirin': 'drug', 'head': 'body part', 'x ray': 'examine', 'lung': 'body part'}
    preprocessor = SR(dictionary)

    text = 'lung cancer patient suffers from fever, headache, and other symptoms. aspirin was given with x ray on his head and lung has been performed without significant finding in his lung' 

    simplified, inv = preprocessor.simplify(text)
    print(simplified)
    print(inv)
    restored = preprocessor.restore(simplified, text, inv) 
    #   Restore the whole string
    print(restored)
    assert restored == text

    #   Restore the first symptom
    p = simplified.find("symptom")
    assert preprocessor.extract_restore(simplified, text, inv, p, p+1) == 'fever'

    #   Restore all body parts
    p = 0
    while True:
        p = simplified.find("body part", p)
        if p == -1:
            break
        print(preprocessor.extract_restore(simplified, text, inv, p, p+1))
        p += 1





        
