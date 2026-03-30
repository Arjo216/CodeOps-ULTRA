# test.py
def find_dupes(arr):
    dupes = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j] and arr[i] not in dupes:
                dupes.append(arr[i])
    print(dupes)

find_dupes([1, 2, 2, 3, 4, 4, 5])