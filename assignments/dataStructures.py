"""
Author: L. Flygare
Description: demonstrate using built-in methods and other loops with various data structures to manipulate the data
"""

import random

#creating a tuple in a normal order and a list with the same elements in the reversed order
print("\n***Build Data Structures***")
aTuple = ("pangolin", "axolotl", "okapi", "quokka", "narwhal", "kakapo", "fossa", "tarsier", "shoebill", "aye-aye")
bList = list(reversed(aTuple))
idTuple = id(aTuple)
idList = id(bList)

#printing both to show the data structures with the elements in their starting orders before manipulating them
print("Tuple (normal order): ", aTuple)
print("List (reverse order): ", bList)

#print the 3rd element of each structure
print("\n***Print 3rd Element***")
print("Tuple (3rd element): ", aTuple[2])
print("List (3rd element): ", bList[2])

#print elements in a random order
randTuple = random.sample(aTuple, k=len(aTuple))    #creates a randomized view despite tuples being immutable
randList = bList[:] #shallow copy so I can preserve original order of the list when using random.shuffle
random.shuffle(randList)    #shuffle copy, not original - could have used random.sample but wanted to mess around

print("\n*** Print Elements Randomly***")
print("Tuple (randomized order using alternate tuple): ", randTuple)
print("ID aTuple: ", idTuple)
print("ID randTuple: ", id(randTuple))
print("List (randomized order using alternate list to preserve original list order): ", randList)
print("ID bList: ", idList)
print("ID randList: ", id(randList))

#add an eleventh element to the end of both
aTuple = aTuple + ("Maned Wolf", )  #create new tuple with same name to circumvent immutabilty and add a new element
bList.append("Maned Wolf")

print("\n***Add 11th Element to End***")
print("Tuple (new tuple to add element): ", aTuple)
print("ID original aTuple: ", idTuple)
print("ID new aTuple: ", id(aTuple))
print("List (same list, appended element): ", bList)
print("ID original bList: ", idList)
print("ID new bList: ", id(bList))

#remove the first element
aTuple = aTuple[1:] #new tuple starting with index position one to omit first item
bList.pop(0)

print("\n***Remove 1st Element***")
print("Tuple (new tuple to remove element): ", aTuple)
print("ID original aTuple: ", idTuple)
print("ID new aTuple: ", id(aTuple))
print("List (same list, popped element): ", bList)
print("ID original bList: ", idList)
print("ID new bList: ", id(bList))

#remove same element from both structures
to_remove = "okapi"

tempList = list(aTuple) #once again have to work around immutability of tuples and cast it to a list for easier manipulation
if to_remove in tempList:
    tempList.remove(to_remove)
aTuple = tuple(tempList)    #convert back from list to a tuple

if to_remove in bList:
    bList.remove(to_remove)

print("\n***Remove Same Element From Both Structures***")
print("Tuple (new tuple without okapi): ", aTuple)
print("ID original aTuple: ", idTuple)
print("ID new aTuple: ", id(aTuple))
print("List (same list without okapi): ", bList)
print("ID original bList: ", idList)
print("ID new bList: ", id(bList))