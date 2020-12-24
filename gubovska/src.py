import math
from random import *
from scipy.constants import Boltzmann

temperature = 0.5
cities = []
distances = []
visited = set()
tabulist = []


def calculate_distance(a, b):       # Euklidova vzdialenost
    global distances
    distance = math.sqrt((int(a[0]) - int(b[0]))**2 + (int(a[1]) - int(b[1]))**2)
    return distance


def create_distance_matrix(cities):     # 2D pole vzdialenosti medzi mestami
    for i in range(0, len(cities)):
        distances.append([])
        for j in range(0, len(cities)):
            distances[i].append(calculate_distance(cities[i], cities[j]))


def load_cities_coords(file):       # zo suboru nacita suradnice miest
    global cities
    x = 0
    for line in file:
        ln = line.split(', ')
        cities.append([])
        cities[x].append(ln[0])
        cities[x].append(ln[1][:-1])
        x += 1


def find_permutation_length(permutation):       # zisti dlzku cesty v permutacii
    length = 0
    for j in range(len(permutation)-1):
        length += distances[permutation[j]][permutation[j+1]]
    return length + distances[permutation[len(permutation)-1]][permutation[0]]      # pripocita este cestu medzi prvym a poslednym prvkom permutacie pre uzavretie cesty do kruhu


def hash_function(permutation):     # vrati zahashovanu permutaciu
    hashed = ""
    for k in range(0, len(permutation)):
        hashed += chr(permutation[k] + 65)      #kazde cislo mesta bude jeden char, z intervalu  <A; A + pocet_miest>
    return hashed


def reverse_path(permutation, start, end):      # vrati novu permutaciu
    segment = permutation[start:end+1]          # zoberie cast povodnej permutacie [start:end] a obrati ju (prvy prvok bude posledny atd)
    segment.reverse()
    new_permutation = []

    for i in range(0, len(permutation[:start])):
        new_permutation.append(permutation[i])

    for j in range(len(segment)):
        new_permutation.append(segment[j])

    for k in range(len(permutation[:start]) + len(segment), len(permutation)):
        new_permutation.append(permutation[k])

    return new_permutation


def transport_path(permutation, start, end):        # vrati novu permutaciu
    segment = permutation[start:end+1]              # zoberie cast povodnej permutacie [start:end] a vlozi ju na nahodne miesto v poli, zvysok sa skopiruje porade na pozicie okolo
    randposition = randrange(0, len(cities)-len(segment)+1)
    if randposition == start:
        return None

    new_permutation = permutation.copy()

    for i in range(len(segment)):
        new_permutation.remove(permutation[start+i])

    for j in range(len(segment)):
        new_permutation.insert(randposition+j, segment[j])

    return new_permutation


def annealing(permutation):     # simulovane zihanie
    global temperature

    while temperature > 0:
        better_permutations = 0
        for p in range(0, 100*len(cities)):
            curr_length = find_permutation_length(permutation)
            visited.add(hash_function(permutation))
            start = randrange(0, len(cities)-1)
            end = randrange(start+1, len(cities)+1)
            coin = randint(0, 1)

            if coin == 0:       # rozhodne ktoru modifikaciu permutacie vykona
                new_permutation = reverse_path(permutation, start, end)

            else:
                new_permutation = transport_path(permutation, start, end)

            if new_permutation is not None:     # ak je tato permutacia platna
                hashed = hash_function(new_permutation)     # zahashuj ju
                if hashed not in visited:                   # ak si ju este predtym nevygeneroval
                    new_length = find_permutation_length(new_permutation)       # najdi dlzku novej permutacie
                    cost_difference = new_length - curr_length
                    if cost_difference < 0:     #akceptuje lepsi stav
                        permutation = new_permutation
                        better_permutations += 1
                        visited.add(hashed)
                        #print(new_length)

                    else:
                        number = float(randrange(0, 101))/100
                        probability = math.exp(-(new_length-curr_length)/(Boltzmann*temperature))

                        if probability > number:        # akceptuje horsi stav
                            permutation = new_permutation
                            better_permutations += 1
                            visited.add(hashed)
                            #print(new_length)

            if better_permutations >= 10:       #optimalizacia - prejdi na dalsie prehladavnie, ak si nasiel aspon 10 lepsich stavov na danej teplote
                break

        temperature *= 0.90     # znizi teplotu o 10%

        if better_permutations == 0:        # ak uz nenajdes lepsie permutacie, ukonci a vypis finalnu postupnost
            print("Najdena postupnost navstivenia miest:")
            for i in range(len(cities)):
                print(permutation[i]+1, end=" ")
            print("\n")
            return permutation

    return None


def swap(permutation, a, b):        # vymeni dva prvky v permutacii
    permutation[a], permutation[b] = permutation[b], permutation[a]
    return permutation


def permutation_code(permutation):      # vrati zakodovanu permutaciu, ktora moze byt v tabuliste
    code = ""
    for i in range(len(permutation)):
        code += str(permutation[i])
    return code


def tabu_search(permutation, listsize):       # zakazane prehladavanie
    global tabulist
    best_permutation, curr_permutation = permutation, permutation
    best_length = find_permutation_length(best_permutation)
    for i in range(1000):
        pos = randrange(0, len(cities)-1)
        for j in range(len(cities)):        # pre kazdu permutaciu najdi N novych permutacii a najlepsiu z nich zvol za novu aktualnu a pridaj ju do tabulistu
            temp = reverse_path(curr_permutation, pos, randrange(pos+1, len(cities)))       # vytvor novu permutacie z aktualnej
            # temp = swap(curr_permutation, pos, j)                                         # vymen prvky permutacie na danych indexoch
            temp_length = find_permutation_length(temp)
            code = permutation_code(temp)

            if temp_length < best_length and code not in tabulist:      # ak je nova permutacia lepsia a este nie je v tabuliste
                best_permutation = temp                                 # stane sa novou najlepsou
                best_length = temp_length
                curr_permutation = temp

        if len(tabulist) == int(listsize):                              # ak sa naplnil tabulist, vymaz najstarsi prvok
            tabulist.pop(0)

        tabulist.append(permutation_code(best_permutation))             # pridaj nove najlepsie riesenie do tabulistu

    return best_permutation


while True:
    print("Zadaj cislo suboru - 1-3\n1: 20 miest, 2: 4 mestá, 3: 30 miest\nPre ukoncenie programu napis 'koniec'")
    n = input()
    if n == "koniec":
        exit()

    print("Zadaj algoritmus - 'zihanie' = simulovane zihanie\n'tabu' = tabu search")
    algorithm = input()

    file = open(n + ".txt", "r")
    load_cities_coords(file)
    create_distance_matrix(cities)
    first_permutation = []
    for i in range(0, len(cities)):
        first_permutation.append(i)
    shuffle(first_permutation)
    vysledky = []
    if algorithm == 'zihanie':
        shuffle(first_permutation)
        final = annealing(first_permutation)
        print("Dlzka cesty: ", find_permutation_length(final), "\n")
        # for j in range(100):
        #     shuffle(first_permutation)
        #     final = annealing(first_permutation)
        #     x = find_permutation_length(final)
        #     print(x)
        #     #print("Dlzka vyslednej cesty: ", x, "\n")
        #     vysledky.append(x)

        # vysledky.clear()
        visited.clear()

    elif algorithm == 'tabu':
        print("Zadaj velkost zoznamu zakazanych stavov: ")
        listsize = input()

        result = tabu_search(first_permutation, listsize)
        print("Dlzka cesty: ", find_permutation_length(result), "\n")
        # for i in range(1000):
        #     result = tabu_search(first_permutation, listsize)
        #     x = find_permutation_length(result)
        #     #print("\n")
        #     print(i, x)
        #     vysledky.append(x)
        #     tabulist.clear()
        tabulist.clear()
        # vysledky.clear()

    else:
        print("Nespravny vstup")

    cities.clear()
    distances.clear()

    file.close()