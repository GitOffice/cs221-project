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

    return recurse(str1, str2)
    

def test_edit_distance():
    assert edit_distance("hello", "hell") == 1
    assert edit_distance("hello", "hellos") == 1
    assert edit_distance("hello", "hllos") == 2
    assert edit_distance("hello", "hillo") == 1
    print("All tests passed!")

if __name__ == "__main__":
    test_edit_distance()
