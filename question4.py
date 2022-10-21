from z3 import Solver, Int, Bool, If, And, Implies, Not, Z3Exception

# parameters of the program
rangeNum = 10
startA = 1
startB = 1

# setting up the changing variables
a = Int("a")
aVars = [ Int(f"a_{i}") for i in range(rangeNum) ] 
aVars = [a] + aVars

b = Int("b")
bVars = [ Int(f"b_{i}") for i in range(rangeNum) ] 
bVars = [b] + bVars


# the possible conditions
conditions = [ Bool(f"cond_{i}") for i in range(rangeNum)]

# the starting values
prog = [And(a == startA, b == startB)]
# capturing the code for entire loop
for i in range(rangeNum):
	prog.append(If(conditions[i], 
		And(aVars[i + 1] == aVars[i] + (2 * bVars[i]), bVars[i + 1] == bVars[i] + i + 1),
		And(bVars[i + 1] == aVars[i] + bVars[i], aVars[i + 1] == aVars[i] + i + 1)))




# looping through different values of n to see if can satisfy crash condition
n = Int("n")
neverCrash = []
for i in range(1, 11):
	solver = Solver()
	solver.add(n == i)
	solver.add()
	# program working properly, does that there is a valid value of the final b that is equal to n + 700?
	# if looking for cases where it will never crash, then saying for a valid program, it will never be the case
	# that n + 700 is equal to the final value of b
	# the Not of that, would therefore be where a valid program CAN result in a the crashing condition
	# which is what we want to see modelled
	solver.add(Not(Implies(And(prog), Not(bVars[-1] == n + 700))))
	print(str(i) + " " + str(solver.check()))
	# if possible, print the model values of the crashing condition
	try:
		m = solver.model()
		print([m[x] for x in aVars])
		print([m[y] for y in bVars])
		print([m[z] for z in conditions])
	# if no model, record this value of n as one that cannot crash
	except Z3Exception:
		neverCrash.append(i)

print("Safe values of n:")
print(neverCrash)
