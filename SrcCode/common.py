import json

sep = ":;"


# e.g: 5:;hello
def Encode(string):
    string = str(len(string)) + sep + string
    return string

