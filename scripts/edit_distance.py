# Returns the a score representing how similar two strings are
def edit_distance(str1, str2):
    cache = {}
    def recurse(str1, str2):
        # base cases
        if len(str1) == 0:
            return len(str2)
        elif len(str2) == 0:
            return len(str1)
        
        if cache.get((str1, str2), -1) != -1:
            return cache[(str1, str2)]
        # recursive case
        if str1[0] == str2[0]:
            ed = recurse(str1[1:], str2[1:])
            cache[(str1, str2)] = ed
            return ed
        else:
            # min of insert into 1, insert into 2, replace
            ed = 1 + min(recurse(str1, str2[1:]), recurse(str1[1:], str2), recurse(str1[1:], str2[1:]))
            cache[(str1, str2)] = ed
            return ed

    return recurse(str1, str2) - common_chars(str1, str2)
    
def common_chars(str1, str2):
    str1 = set(str1)
    str2 = set(str2)
    count = 0
    for char1 in str1:
        for char2 in str2:
            if char1 == char2:
                count += 1
    return count

# specifically for pinyin 
def have_diff_tones(v1, v2):
    result = False
    if v1 in 'āáǎàa' and v2 in 'āáǎàa':
        return True
    elif v1 in 'ēéěèe' and v2 in 'ēéěèe':
        return True
    elif v1 in 'īíǐìi' and v2 in 'īíǐìi':
        return True
    elif v1 in 'ōóǒòo' and v2 in 'ōóǒòo':
        return True
    elif v1 in 'ūúǔùu' and v2 in 'ūúǔùu':
        return True
    elif v1 in 'ǖǘǚǜü' and v2 in 'ǖǘǚǜü':
        return True
    else:
        return False


# specifically for pinyin - doesn't penalize wrong tones as much
def edit_distance_pinyin(str1, str2):
    cache = {}
    def recurse(str1, str2):
        # base cases
        if len(str1) == 0:
            return len(str2)
        elif len(str2) == 0:
            return len(str1)
        
        if cache.get((str1, str2), -1) != -1:
            return cache[(str1, str2)]
        # recursive case
        if str1[0] == str2[0]:
            ed = recurse(str1[1:], str2[1:])
            cache[(str1, str2)] = ed
            return ed
        if have_diff_tones(str1[0], str2[0]):
            ed = 0.5 + recurse(str1[1:], str2[1:])
            cache[(str1, str2)] = ed
            return ed
        else:
            # min of insert into 1, insert into 2, replace
            ed = 1 + min(recurse(str1, str2[1:]), recurse(str1[1:], str2), recurse(str1[1:], str2[1:]))
            cache[(str1, str2)] = ed
            return ed

    return recurse(str1, str2) #- common_chars(str1, str2)

def test_edit_distance():
    assert edit_distance("hello", "hell") == 1-3
    assert edit_distance("hello", "hellos") == 1-4
    assert edit_distance("hello", "hllos") == 2-3
    assert edit_distance("hello", "hillo") == 1-3

    assert have_diff_tones("ā", "a")
    assert not have_diff_tones("ā", "i")

    assert edit_distance_pinyin("buǒ", "buó") == 0.5-2
    
    print("All tests passed!")

if __name__ == "__main__":
    test_edit_distance()
