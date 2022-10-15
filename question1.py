from z3 import Bool, Solver, Or, Not, PbEq, PbLe, Sum, Int, If
from func_timeout import func_timeout, FunctionTimedOut

# question 1
cannotMixState = False

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

palletTypes = [nuzzles, prittles, skipples, crottles, dupples]

# the index of the pallet type with an unknown number you want maxmized
palletMaxType = "prittles"

solver = Solver()


# create a list containing each truck, and for each slot, have a variable for each possible type + empty
truckList = [ [ [ Bool(f"{t}_truck{i}_space{j}") for t in ["nuzzles", "prittles", "skipples", "crottles", "dupples", "empty"] ] for j in range(maxPalletTruck) ] for i in range(normalTruckNum + coolingTruckNum)]


# each slot can only contain one type of pallet or be empty
for t in truckList:
	for s in t:
		solver.add(PbEq([(x,1) for x in s], 1))



# there must be the correct number of pallets of each type in the trucks
for p in range(0, len(palletTypes)):
	possibleSlots = []

	# create a list of each possible place a pallet type can be
	for t in truckList:
		for s in t:
			possibleSlots.append(s[p])

	# if there is a set number for that pallet, make sure it is followed
	if not(type(palletTypes[p]["num"]) == str):
		solver.add(PbEq([(x,1) for x in possibleSlots], palletTypes[p]["num"]))
		# solver.add(PbEq([(x,1) for x in possibleSlots], 1))



# no truck can have too much weight
for t in truckList:
	# create an array per truck that has each pallet type as a subarray
	typeAmount = []
	for p in range(0, len(palletTypes)):
		typeAmount.append([])
		for s in t:
			typeAmount[p].append(s[p])

	# use each subarray to calculate the weight contributed by that type
	# make sure the overall sum is not too large
	solver.add(Sum([ Sum(typeAmount[i]) * palletTypes[i]["weight"] for i in range(0, len(typeAmount)) ]) <= maxWeightTruck)


# make sure that any pallet needing it is in a cooling truck
# looping through the non-cooling trucks
for t in range(coolingTruckNum, (normalTruckNum + coolingTruckNum)):
	# creating an array of the possible slots for pallets requiring cooling
	coolType = []
	for p in range(0, len(palletTypes)):
		if palletTypes[p]["cool"]:
			for s in truckList[t]:
				coolType.append(s[p])
	# declaring none of those slots can be true
	solver.add(Not(Or(coolType)))


# make sure only one of valuable pallet type is assigned per truck
for t in truckList:
	# create an array of possible slots for valuable pallets
	for p in range(0, len(palletTypes)):
		valuableType = []
		if palletTypes[p]["notSame"]:
			for s in t:
				valuableType.append(s[p])

			# make sure that there is only 1 or less of that type in the truck
			solver.add(PbLe([(x,1) for x in valuableType], 1))



# this condition only occurs if state is true
if cannotMixState:
	for p in range(0, len(palletTypes)):
		if palletTypes[p]["cannotMix"] != []:
			for mixType in palletTypes[p]["cannotMix"]:
				# get index in pallettype
				mixIndex = [i for i in range(0, len(palletTypes)) if palletTypes[i]["name"] == mixType][0]

				for t in truckList:
					firstType = []
					incompatibleType = []
					for s in t:
						firstType.append(s[p])
						incompatibleType.append(s[mixIndex])

					# for each truck if firt type is there, other type cannot be
					solver.add(If(Or(firstType), Not(Or(incompatibleType)), Not(Or(firstType))))


# define the variables containing the number of pallets that are not pre-defined
missingInt = [Int(f"type_{i['name']}") for i in palletTypes if i["num"] == "" and i["name"] == palletMaxType][0]

# create an array of all possible slots of the pallet type missing a defined number
for p in range(0, len(palletTypes)):
	if palletTypes[p]["num"] == "" and palletTypes[p]["name"] == palletMaxType:
		missingTypeList = []
		for t in truckList:
			for s in t:
				missingTypeList.append(s[p])

		# defines the integer as the how many pallets there are on the trucks
		solver.add(Sum(missingTypeList) == missingInt)

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


# clearly print out how the pallets are assigned to each truck
# and the weight in each truck
for t in range(0, len(truckList)):
	weight = 0
	if t < coolingTruckNum:
		print("On truck " + str(t) + " (cooling)")
	else:
		print("On truck " + str(t))
	for s in range(0, len(truckList[t])):
		filledIndex = [m[x] for x in truckList[t][s]].index(True)
		if filledIndex >= len(palletTypes):
			print("Slot " + str(s) + ": empty")
		else:
			print("Slot " + str(s) + ": " + palletTypes[filledIndex]["name"])

			weight += palletTypes[filledIndex]["weight"]

	print("Weight: " + str(weight))
