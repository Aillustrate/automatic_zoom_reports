import re

def hasproper(entity):
    for word in entity.split():
        if word.istitle():
            return True
        if word.startswith('"'):
            return True
    return False

def hasnum(entity):
    num_pattern = re.compile("\d+")
    if num_pattern.search(entity):
        return True
    return False

if __name__ == "__main__":
    assert hasproper("меня зовут Аня") == True
    assert hasproper("меня зовут аня") == False
    assert hasproper("my name is Ann") == True
    assert hasproper('ООО "Пивозавр"') == True
    assert hasnum('23') == True
    assert hasnum('дом 15') == True
    assert hasnum('ООО "Пивозавр"') == False