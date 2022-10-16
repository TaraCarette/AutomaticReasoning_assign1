from z3 import Real, Solver, Or, And, Not
# chip is 30 by 30
# power 4 by 3
# center of power 16 away in at least one x or y
# other components must be touching power
# components may be turned 90 but cannot overlap

chip = (30, 30)

powerSize = (4, 3)
powerNum = 2

c1 = (4, 5)
c2 = (4, 6)
c3 = (5, 20)
c4 = (6, 9)
c5 = (6, 10)
c6 = (6, 11)
c7 = (7, 8)
c8 = (7, 12)
c9 = (10, 10)
c10 = (10, 20)

componentList = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

# create values associated with each component
cLocations = [ [Real(f"comp{c}_topx"), Real(f"comp{c}_topy"), Real(f"comp{c}_bottomx"), Real(f"comp{c}_bottomy")] for c in range(0, len(componentList))]

# add the power components onto the list
for i in range(powerNum):
	componentList.append(powerSize)
powerLocations = [ [Real(f"power{p}_topx"), Real(f"power{p}_topy"), Real(f"power{p}_bottomx"), Real(f"power{p}_bottomy")] for p in range(powerNum)]
# create a list with all types of components
componentLocations = cLocations + powerLocations


solver = Solver()


for c in range(0, len(componentList)):
	# component must be the correct dimmensions
	solver.add(Or( And((componentLocations[c][1] - componentLocations[c][3]) == componentList[c][0], 
		(componentLocations[c][2] - componentLocations[c][0]) == componentList[c][1]),
		And((componentLocations[c][1] - componentLocations[c][3]) == componentList[c][1],
		(componentLocations[c][2] - componentLocations[c][0]) == componentList[c][0])))

	# components must be within chip
	solver.add(componentLocations[c][0] >= 0)
	solver.add(componentLocations[c][1] <= chip[1])
	solver.add(componentLocations[c][2] <= chip[0])
	solver.add(componentLocations[c][3] >= 0)

	# specifying the non-power components
	# must be touch a power component
	if c < len(cLocations):
		pOptions = []
		for i in range(0, powerNum):
			pMatch = componentLocations[len(cLocations) + i]

			# creating the option to be touching this specific power component
			pOptions.append(Or(componentLocations[c][3] == pMatch[1], componentLocations[c][2] > pMatch[0], componentLocations[c][0] < pMatch[2],
				componentLocations[c][1] == pMatch[3], componentLocations[c][2] > pMatch[0], componentLocations[c][0] < pMatch[2],
				componentLocations[c][0] == pMatch[2], componentLocations[c][1] > pMatch[3], componentLocations[c][3] < pMatch[1],
				componentLocations[c][2] == pMatch[2], componentLocations[c][1] > pMatch[3], componentLocations[c][3] < pMatch[1]))

		# enure at least one of the power components is being touched
		solver.add(pOptions)


print(solver.check())
# print(solver.model())