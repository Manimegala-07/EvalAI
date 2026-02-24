import re

STOPWORDS = {
    "is","the","a","an","and","or","of","to","in","on","for","with","that","this","are"
}

def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def keyword_coverage(reference, student):
    ref_words = set(tokenize(reference))
    stu_words = set(tokenize(student))

    if not ref_words:
        return 0

    common = ref_words.intersection(stu_words)
    return len(common) / len(ref_words)


def contradiction_penalty(reference, student):
    """
    Detect reversed relationships:
    if reference says A -> B but student says B -> A
    """
    ref = reference.lower()
    stu = student.lower()

    # extract simple relations: "x stores y"
    pattern = r"(\w+)\s+(stores?|contains?|holds?)\s+(\w+)"

    ref_pairs = re.findall(pattern, ref)
    stu_pairs = re.findall(pattern, stu)

    ref_map = {(a,b):c for a,b,c in ref_pairs}
    stu_map = {(a,b):c for a,b,c in stu_pairs}

    penalty = 0

    for (a,verb),c in ref_map.items():
        for (sa,sverb),sc in stu_map.items():
            if a == sc and c == sa:
                penalty += 1

    return min(penalty * 0.5, 1)


def concept_score(reference, student):
    coverage = keyword_coverage(reference, student)
    contradiction = contradiction_penalty(reference, student)

    consistency = max(0, 1 - contradiction)

    return coverage, consistency