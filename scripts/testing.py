from copy import copy

hidden_prev = [0,1,2]
hidden_next = [8,9,10]
curr = [3,4,5,6,7]

size = 5




def next_():
    rem = copy(curr[0])
    print(f'Copying {rem} at index 0')
    new = hidden_next.pop(0)
    print(f'Popping Hidden Next {new} -> {hidden_next}')
    hidden_prev.append(rem)
    print(f'Appending Hidden Prev {rem} -> {hidden_prev}')
    curr.append(new)
    print(f'Appending New {new} -> {curr}')
    curr.remove(curr[0])
    print(f'Removing index 0 -> {curr}')

def prev():
    rem = copy(curr[size - 1])
    print(f'Copying {rem} at index {size - 1}')
    new = hidden_prev.pop()
    print(f'Popping Hidden Prev {new} -> {hidden_prev}')
    hidden_next.insert(0, rem)
    print(f'Inserting Hidden Next at index 0 -> {hidden_next}')
    curr.insert(0, new)    
    print(f'Changing value at index 0 -> {curr}')
    curr.remove(curr[size])
    print(f'removing last element -> {curr}')

if __name__ == "__main__":
    while True:
        choice = input('Next or Prev')
        if choice == '1':
            next_()
        else:
            prev()
        print(f'Current: {curr}')
        print(f'Hidden Next: {hidden_next}')
        print(f'Hidden Prev: {hidden_prev}')