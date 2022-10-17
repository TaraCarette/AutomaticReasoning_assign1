from z3 import Solver, Bool, PbLe, Implies, Sum, And, Or

# 5 couples in different houses want dinner
# dinner in 5 rounds
# 5 people max per house
# each round will have 2 houses serving dinner at the same time
# every couple serves 2 rounds in their own house
# every 2 people meet each other at most 4 times

# a - every 2 people meet each other at least once
# b - every 2 people meet each otehr at most 3 times
# c - couples never meet outside of their house
# d - for every house the 6 guests are distinct (couple stay same, each house hosts 2 rounds)


# show a with c or d but not both
# show b possible with c and d

# parameters
roundNum = 5
houseNum = 5
maxPerHouse = 5
hostNum = 2

# booleans about which optional rules to implement
a = False
b = False
c = False
d = False

solver = Solver()


personPlacement = [ [ [Bool(f"r{r}_h{h}_person{p}") for p in range(houseNum * 2)] for h in range(houseNum)] for r in range(roundNum)]

for r in personPlacement:
	for h in range(len(r)):
		# in one house only allowed number of people
		solver.add(PbLe([(x,1) for x in r[h]], maxPerHouse))

		# if the house belongs to the couple they must be there
		solver.add(Implies(Sum(r[h]) > 0, And(r[h][h * 2], r[h][(h * 2) + 1])))


	# a person must be present exactly once in a round
	for p in range(houseNum * 2):
		pPlace = []
		for h in r:
			pPlace.append(h[p])

		solver.add(Sum(pPlace) == 1)



# each house hosts a set number of times
for h in range(houseNum):
	houseHost = []
	for r in range(roundNum):
		houseHost.append(Or(personPlacement[r][h]))

	solver.add(Sum(houseHost) == 2)


# people meet at most 4 times
# across all rounds, Sum is less than 4 with 0:1 

# only compare ahead to avoid reduncies
for p1 in range(houseNum * 2):
	for p2 in range(p1 + 1, houseNum * 2):
		dinnerTogether = []
		for r in personPlacement:
			for h in r:
				dinnerTogether.append(And([h[p1], h[p2]]))

		solver.add(Sum(dinnerTogether) <= 4)



print(solver.check())
m = solver.model()

for r in range(len(personPlacement)):
	print("Round: " + str(r))

	for h in range(len(personPlacement[r])):
		print("House: " + str(h))

		host = False
		for p in personPlacement[r][h]:
			if m[p]:
				host = True
				break
		if host:
			for p in personPlacement[r][h]:
				print(str(p) + " " + str(m[p]))

		print("---")
