from z3 import Solver, Bool, Implies, Sum, And, Or, Not


# parameters
roundNum = 5
houseNum = 5
maxPerHouse = 5
hostNum = 2

# booleans about which optional rules to implement
a = False
b = True
c = True
d = True

solver = Solver()

# a list per round, a sublist per each house, and within that house, a boolean for each person, true if they are there
personPlacement = [ [ [Bool(f"r{r}_h{h}_person{p}") for p in range(houseNum * 2)] for h in range(houseNum)] for r in range(roundNum)]

for r in personPlacement:
	for h in range(len(r)):
		# in one house only allowed number of people
		solver.add(Sum(r[h]) <= maxPerHouse)

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
# only compare ahead to avoid redundacies
for p1 in range(houseNum * 2):
	for p2 in range(p1 + 1, houseNum * 2):
		dinnerTogether = []
		for r in personPlacement:
			for h in r:
				dinnerTogether.append(And([h[p1], h[p2]]))

		solver.add(Sum(dinnerTogether) <= 4)

		# people meet everyone at least once
		if a:
			solver.add(Sum(dinnerTogether) >= 1)

		# people meet each other at most 3 times
		if b:
			solver.add(Sum(dinnerTogether) <= 3)

# couples never meet outside of their house
if c:
	for p in range(0, houseNum * 2, 2):
		for r in personPlacement:
			for h in range(len(r)):
				# if not own house do not allow combination
				if not((h * 2) == p):
					solver.add(Not(And([r[h][p], r[h][p + 1]])))

# all of the house guests are distinct
if d:
	for h in range(houseNum):
		houseGuest = [[] for i in range(houseNum * 2 - 2)]
		for r in personPlacement:
			count = 0
			for p in range(len(r[h])):
				# only look at guests of the house
				if not((h * 2) == p or (h * 2) + 1 == p):
					houseGuest[count].append(r[h][p])
					count += 1
		solver.add(Sum([Sum(g) == 1 for g in houseGuest]) == 6)



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
