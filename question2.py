from z3 import Int, Solver, Or, And, Implies
# chip is 30 by 30
# power 4 by 3
# center of power 16 away in at least one x or y
# other components must be touching power
# components may be turned 90 but cannot overlap

chip = (30, 30)

powerSize = (4, 3)
powerNum = 2
powerDistance = 16

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
cLocations = [ [Int(f"comp{c}_topx"), Int(f"comp{c}_topy"), Int(f"comp{c}_bottomx"), Int(f"comp{c}_bottomy")] for c in range(0, len(componentList))]

# add the power components onto the list
for i in range(powerNum):
	componentList.append(powerSize)
powerLocations = [ [Int(f"power{p}_topx"), Int(f"power{p}_topy"), Int(f"power{p}_bottomx"), Int(f"power{p}_bottomy")] for p in range(powerNum)]
# create a list with all types of components
componentLocations = cLocations + powerLocations

solver = Solver()


for c in range(0, len(componentList)):
	# component must be the correct dimmensions
	# distance between xs and distance between ys correct for either as is or 90 degrees turned
	solver.add(Or( And((componentLocations[c][1] - componentLocations[c][3]) == componentList[c][0], 
		(componentLocations[c][2] - componentLocations[c][0]) == componentList[c][1]),
		And((componentLocations[c][1] - componentLocations[c][3]) == componentList[c][1],
		(componentLocations[c][2] - componentLocations[c][0]) == componentList[c][0])))

	# components must be within chip
	solver.add(componentLocations[c][0] >= 0)
	solver.add(componentLocations[c][1] <= chip[1])
	solver.add(componentLocations[c][2] <= chip[0])
	solver.add(componentLocations[c][3] >= 0)

	# # specifying the non-power components
	# # must be touch a power component
	# if c < len(cLocations):
	# 	pOptions = []
	# 	for i in range(0, powerNum):
	# 		pMatch = componentLocations[len(cLocations) + i]

	# 		# creating the option to be touching this specific power component
	# 		pOptions.append(Or(And(componentLocations[c][3] == pMatch[1], componentLocations[c][2] > pMatch[0], componentLocations[c][0] < pMatch[2]),
	# 			And(componentLocations[c][1] == pMatch[3], componentLocations[c][2] > pMatch[0], componentLocations[c][0] < pMatch[2]),
	# 			And(componentLocations[c][0] == pMatch[2], componentLocations[c][1] > pMatch[3], componentLocations[c][3] < pMatch[1]),
	# 			And(componentLocations[c][2] == pMatch[2], componentLocations[c][1] > pMatch[3], componentLocations[c][3] < pMatch[1])))


	# 	# enure at least one of the power components is being touched
	# 	solver.add(Or(pOptions))


	# power must be at least 16 away in one direction
	if c >= len(cLocations):
		# only compare to power components ahead in list to avoid redundancies 
		for i in range(c + 1, (len(componentList))):
			otherPower = componentLocations[i]
			solver.add(Or((((otherPower[1] - otherPower[3]) / 2) + otherPower[3]) - (((componentLocations[c][1] - componentLocations[c][3]) / 2) + componentLocations[c][3]) >= powerDistance,
				(((componentLocations[c][1] - componentLocations[c][3]) / 2) + componentLocations[c][3]) - (((otherPower[1] - otherPower[3]) / 2) + otherPower[3]) >= powerDistance,
				(((otherPower[2] - otherPower[0]) / 2) + otherPower[0]) - (((componentLocations[c][2] - componentLocations[c][0]) / 2) + componentLocations[c][0]) >= powerDistance,
				(((componentLocations[c][2] - componentLocations[c][0]) / 2) + componentLocations[c][0]) - (((otherPower[2] - otherPower[0]) / 2) + otherPower[0]) >= powerDistance))


	# components must not overlap
	# only compare to components ahead in list to avoid redundancies 
	for i in range(c + 1, (len(componentList))):
		otherComponent = componentLocations[i]

		# if the components shares the x range, it cannot share y range
		solver.add(Implies(And(componentLocations[c][0] < otherComponent[2], componentLocations[c][2] > otherComponent[0]),
			Or(componentLocations[c][1] <= otherComponent[3], componentLocations[c][3] >= otherComponent[1])))

		# if the components shares the y range, it cannot share x range
		solver.add(Implies(And(componentLocations[c][1] <= otherComponent[1], componentLocations[c][3] >= otherComponent[0]),
			Or(componentLocations[c][0] >= otherComponent[2], componentLocations[c][2] <= otherComponent[0])))


print(solver.check())
m = solver.model()

for i in range(len(componentLocations)):
	print(i)
	for j in componentLocations[i]:
		print(j + m[j])

import tkinter as Tk

root = Tk.Tk()
root.geometry('500x500')
root.config(bg='#345')

canvas = Tk.Canvas(
    root,
    height=450,
    width=450,
    bg="#fff"
    )
    
canvas.pack()

scale = 15
for i in range(len(componentLocations)):
	if i < len(cLocations):
		canvas.create_rectangle(
		    m.evaluate(componentLocations[i][0] * scale), m.evaluate((chip[1] - componentLocations[i][1]) * scale), m.evaluate(componentLocations[i][2] * scale), m.evaluate((chip[1] - componentLocations[i][3]) * scale),
		    outline="#000",
		    fill="#fb0")
	else:
		canvas.create_rectangle(
	    m.evaluate(componentLocations[i][0] * scale), m.evaluate((chip[1] - componentLocations[i][1]) * scale), m.evaluate(componentLocations[i][2] * scale), m.evaluate((chip[1] - componentLocations[i][3]) * scale),
	    outline="#000",
	    fill="#bb0")

root.mainloop()
