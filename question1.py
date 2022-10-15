from z3 import Bool, Solver, Or, Not, PbEq, PbLe, Sum, Int, If
from func_timeout import func_timeout, FunctionTimedOut

# question 1
cannotMixState = True

# defining the variables to do with trucks
normalTruckNum = 5
coolingTruckNum = 3
maxWeightTruck = 8000
maxPalletTruck = 8

# defining the requirements of each pallet
nuzzles = {"name": "nuzzles", "num": 4, "weight": 700, "cool": False, "notSame": True, "cannotMix": []}
prittles = {"name": "prittles", "num": "", "weight": 400, "cool": False, "notSame": False, "cannotMix": ["crottles"]}
skipples = {"name": "skipples", "num": 8, "weight": 1000, "cool": True, "notSame": False, "cannotMix": []}
crottles = {"name": "crottles", "num": 10, "weight": 2500, "cool": False, "notSame": False, "cannotMix": ["prittles"]}
dupples = {"name": "dupples", "num": 20, "weight": 200, "cool": False, "notSame": False, "cannotMix": []}

paletTypes = [nuzzles, prittles, skipples, crottles, dupples]

# the index of the palet type with an unknown number you want maxmized
paletMaxType = "prittles"

solver = Solver()


# create a list containing each truck, and for each slot, have a variable for each possible type + empty
truckList = [ [ [ Bool(f"{t}_truck{i}_space{j}") for t in ["nuzzles", "prittles", "skipples", "crottles", "dupples", "empty"] ] for j in range(maxPalletTruck) ] for i in range(normalTruckNum + coolingTruckNum)]


# each slot can only contain one type of palet or be empty
for t in truckList:
	for s in t:
		solver.add(PbEq([(x,1) for x in s], 1))



# there must be the correct number of palets of each type in the trucks
for p in range(0, len(paletTypes)):
	possibleSlots = []

	# create a list of each possible place a palet type can be
	for t in truckList:
		for s in t:
			possibleSlots.append(s[p])

	# if there is a set number for that palet, make sure it is followed
	if not(type(paletTypes[p]["num"]) == str):
		solver.add(PbEq([(x,1) for x in possibleSlots], paletTypes[p]["num"]))
		# solver.add(PbEq([(x,1) for x in possibleSlots], 1))



# no truck can have too much weight
for t in truckList:
	# create an array per truck that has each palet type as a subarray
	typeAmount = []
	for p in range(0, len(paletTypes)):
		typeAmount.append([])
		for s in t:
			typeAmount[p].append(s[p])

	# use each subarray to calculate the weight contributed by that type
	# make sure the overall sum is not too large
	solver.add(Sum([ Sum(typeAmount[i]) * paletTypes[i]["weight"] for i in range(0, len(typeAmount)) ]) <= maxWeightTruck)


# make sure that any palet needing it is in a cooling truck
# looping through the non-cooling trucks
for t in range(coolingTruckNum, (normalTruckNum + coolingTruckNum)):
	# creating an array of the possible slots for palets requiring cooling
	coolType = []
	for p in range(0, len(paletTypes)):
		if paletTypes[p]["cool"]:
			for s in truckList[t]:
				coolType.append(s[p])
	# declaring none of those slots can be true
	solver.add(Not(Or(coolType)))


# make sure only one of valuable palet type is assigned per truck
for t in truckList:
	# create an array of possible slots for valuable palets
	for p in range(0, len(paletTypes)):
		valuableType = []
		if paletTypes[p]["notSame"]:
			for s in t:
				valuableType.append(s[p])

			# make sure that there is only 1 or less of that type in the truck
			solver.add(PbLe([(x,1) for x in valuableType], 1))


# define the variables containing the number of palets that are not pre-defined
missingInt = [Int(f"type_{i['name']}") for i in paletTypes if i["num"] == "" and i["name"] == paletMaxType][0]

# create an array of all possible slots of the palet type missing a defined number
for p in range(0, len(paletTypes)):
	if paletTypes[p]["num"] == "" and paletTypes[p]["name"] == paletMaxType:
		missingTypeList = []
		for t in truckList:
			for s in t:
				missingTypeList.append(s[p])

		# defines the integer as the how many palets there are on the trucks
		solver.add(Sum(missingTypeList) == missingInt)



# this condition only occurs if state is true
if cannotMixState:
	for p in range(0, len(paletTypes)):
		if paletTypes[p]["cannotMix"] != []:
			for mixType in paletTypes[p]["cannotMix"]:
				# get index in palettype
				mixIndex = [i for i in range(0, len(paletTypes)) if paletTypes[i]["name"] == mixType][0]

				for t in truckList:
					firstType = []
					incompatibleType = []
					for s in t:
						firstType.append(s[p])
						incompatibleType.append(s[mixIndex])

					# for each truck if firt type is there, other type cannot be
					solver.add(If(Or(firstType), Not(Or(incompatibleType)), Not(Or(firstType))))

# checking if there is a valid model
# in a function so can time out if unsat
def check():
	solver.check()
	return True

# loop through trying to maxmize defined integer until check is unsat
try:
	while func_timeout(2, check):
		m = solver.model()
		currentLargest = m[missingInt]
		solver.add(missingInt > m.evaluate(m[missingInt]))
except FunctionTimedOut:
	print("The largest is " + str(currentLargest))

