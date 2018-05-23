import sys
import xinput
import time
import winsound

SOUND_ON = True

BTN_BIT_0 = 0x01
BTN_BIT_1 = BTN_BIT_0 << 1
BTN_BIT_2 = BTN_BIT_1 << 1
BTN_BIT_3 = BTN_BIT_2 << 1
BTN_BIT_4 = BTN_BIT_3 << 1
BTN_BIT_5 = BTN_BIT_4 << 1
BTN_BIT_STRUM_DOWN = BTN_BIT_5 << 1
BTN_BIT_STRUM_UP = BTN_BIT_STRUM_DOWN << 1
BTN_BIT_BACK = BTN_BIT_STRUM_UP << 1
BTN_BIT_START = BTN_BIT_BACK << 1
BTN_BIT_PAD_DOWN = BTN_BIT_START << 1
BTN_BIT_PAD_UP = BTN_BIT_PAD_DOWN << 1

THROW_EDGE = 25000
THROW_HYSTERESIS = 6000
WHAMMY_EDGE = 0
WHAMMY_HYSTERESIS = 5000

opTable = {
	0: "+",
	1: "*",
	2: "^"
}


def main():

	print("Startup")

	controller = xinput.XInputJoystick(0)

	# Dynamic get rate
	#rate = xinput.determine_optimal_sample_rate()
	rate = 200

	operands = [0]
	operators = []
	outStr = ""
	i = 0
	j = 0
	ans = 0
	opCounter = 0
	sign = 1

	print("Operation: +")

	state = controller.get_state()
	prevState = state
	up = GetOrientation(state) > THROW_EDGE
	prevUp = up
	whammyDown = GetWhammy(state) > WHAMMY_EDGE
	prevWhammyDown = whammyDown

	while True:
		# Wait on sample rate
		time.sleep(1.0 / rate);

		# Get state of controller
		state = controller.get_state()
		#print(xinput.struct_dict(state.gamepad))

		# Check orientation
		if up is False and GetOrientation(state) > THROW_EDGE + THROW_HYSTERESIS:
			up = True
		elif up is True and GetOrientation(state) < THROW_EDGE - THROW_HYSTERESIS:
			up = False

		# Check whammy
		if whammyDown is False and GetWhammy(state) > WHAMMY_EDGE + WHAMMY_HYSTERESIS:
			whammyDown = True
		elif whammyDown is True and GetWhammy(state) < WHAMMY_EDGE - WHAMMY_HYSTERESIS:
			whammyDown = False

		# Check various controls
		# Check strum down
		if GetButtons(state) & BTN_BIT_STRUM_DOWN and not GetButtons(prevState) & BTN_BIT_STRUM_DOWN:
			#print("Strum down")
			#print('i = ' + str(i))

			# Check for insert operand
			operand = GetButtons(state) & 0x1F
			# Overwrite ans
			ans = 0
			
			#print("j: " + str(j))
			if operands[i] == 0:
				if j >= 0:
					operands[i] = operand
					outStr = outStr[:-1] + "{0:d}".format(operand)
					if operand < 10:
						j += 1
					else:
						j += 2
				else:
					if operand < 10:
						operands[i] = operand/10
						j -= 1
					else:
						operands[i] = operand/100
						j-= 2
					outStr = outStr + str(operand)

			elif j >= 0:
				if operand < 10:
					operands[i] = operands[i]*10 + operand*sign
					j += 1
				else:
					operands[i] = operands[i]*100 + operand*sign
					j += 2
				outStr = outStr + str(operand)
				

			elif j < 0:
				if operand < 10:
					operands[i] = operands[i] + operand*(10**j)*sign
					j -= 1
				else:
					operands[i] = operands[i] + operand*(10**(j-1))*sign
					j -= 2

				outStr = outStr + str(operand)

			#print("Operands: " + str(operands))
			print(outStr + "\t\t\tOperation: " + opTable[opCounter] + "               ", end = '\r')
			playStrum(state)

		# Check strum up
		if GetButtons(state) & BTN_BIT_STRUM_UP and not GetButtons(prevState) & BTN_BIT_STRUM_UP:
			#print("Strum up")

			if operands[0] == 0 and len(operands) == 1:
				#outStr = '0'
				outStr = str(ans)
				operands[0] = ans

			operator = opTable[opCounter]
			operators.append(operator)
			operands.append(0)
			outStr = outStr + ' ' + operator + ' 0'

			i += 1
			j = 0
			sign = 1

			if outStr != "":
				print(outStr, end = '\r')
			else:
				print("Please input at an operand.")

			#sys.stdout.flush

		# Check for whammy press
		if whammyDown and not prevWhammyDown:
			#print("Whammy down")

			opCounter += 1
			if opCounter >= len(opTable):
				opCounter = 0
				
			#print("opCounter: " + str(opCounter))
			print(outStr + "\t\t\tOperation: " + opTable[opCounter] + "               ", end = '\r')

		# Check for thrown guitar
		if up and not prevUp:
			#winsound.PlaySound('slide_whistle_up.wav', winsound.SND_FILENAME)
			try:
				# Lists to hold what ops go where
				expOps = []
				mulOps = []
				addOps = []
				result = 0
				for i in range(len(operators)):
					if operators[i] == '^':
						expOps.append(i)
					if operators[i] == '*':
						mulOps.append(i)
					elif operators[i] == '+':
						addOps.append(i)

				# Perform ops in order of operations
				for i in range(len(expOps)):
					expOp = expOps[len(expOps) - i - 1]
					result = operands[expOp]**operands[expOp+1]
					operands[expOp] = result
					operands.pop(expOp+1)
					shortenList(expOps, expOp)
					shortenList(mulOps, expOp)
					shortenList(addOps, expOp)

				for mulOp in mulOps:
					result = operands[mulOp]*operands[mulOp+1]
					operands[mulOp] = result
					operands.pop(mulOp+1)
					shortenList(mulOps, mulOp)
					shortenList(addOps, mulOp)

				for addOp in addOps:
					result = operands[addOp]+operands[addOp+1]
					operands[addOp] = result
					operands.pop(addOp+1)
					shortenList(addOps, addOp)

				result = operands[0]
				ans = result

				outStr = outStr + " = " + str(result) + "\t\t\t        "
				if not outStr == " = 0" + "\t\t\t             ":
					print(outStr)
					print("\t\t\t\tOperation: " + opTable[opCounter], end = "\r")

			#except:
			#	print("Invalid equation, clearing.")

			finally:
				i = 0
				j = 0
				sign = 1
				outStr = ""
				operands = [0]
				operators.clear()

		# Check for back button
		if GetButtons(state) & BTN_BIT_BACK and not GetButtons(prevState) & BTN_BIT_BACK:
			# Erase last character of operand or delete operator
			if operands[i] != 0 and j >= 0:
				operands[i] = int(operands[i]/10)
				outStr = outStr[:-1]
				j -= 1
				if operands[i] == 0:
					outStr = outStr + "0"

			elif operands[i] != 0 and j <= -1:
				operands[i] -= operands[i]%(10**(j+2))
				j += 1
				outStr = outStr[:-1]

			elif outStr[-1:] == ".":
				outStr = outStr[:-1]
				j = len(str(operands[i]))-1

			elif operands[i] == 0 and len(operators) >= 1:
				operands.pop(i)
				operators.pop(len(operators)-1)
				i -= 1
				outStr = outStr[:-4]

			else:
				pass

			print(outStr + "         ", end = '\r')
			#print("Operands: " + str(operands))
			#print("j: " + str(j))
			#print("Operators:" + str(operators))

		# Check for pad down button
		if GetButtons(state) & BTN_BIT_PAD_DOWN and not GetButtons(prevState) & BTN_BIT_PAD_DOWN:
			# Make negative
			if operands[i] != 0:
				operands[i] *= -1
				#outStr = outStr[:-(j+1)] + '-' + outStr[-(j+1):]
				outStr = negateOperand(outStr)
				sign = sign*-1
				
			#print(operands)
			print(outStr, end = '\r')

		# Check for Start button
		if GetButtons(state) & BTN_BIT_START and not GetButtons(prevState) & BTN_BIT_START:
			# If no dot yet, add one
			if j >= 0:
				j = -1
				outStr = outStr + "."

			print(outStr, end = '\r')

		prevState = state
		prevUp = up
		prevWhammyDown = whammyDown


def shortenList(inList, x):
	for i in range(len(inList)):
		if inList[i] > x:
			inList[i] -= 1

def GetWhammy(state):
	return state.gamepad.r_thumb_x

def GetOrientation(state):
	return state.gamepad.r_thumb_y

def negateOperand(inStr):
	i = 0
	while i < len(inStr):
		i += 1
		if inStr[-i:-i+1] == " ":
			inStr = inStr[:-i+1] + "-" + inStr[-i+1:]
			return inStr

		elif inStr[-i:-i+1] == "-":
			inStr = inStr[:-i] + inStr[-i+1:]
			return inStr

	return "-" + inStr

def GetButtons(state):
	out = 0

	buttons = state.gamepad.buttons
	#print("Raw: {0:x}".format(buttons))
	if buttons & 0x100:
		out =  out | BTN_BIT_0
	if buttons & 0x4000:
		out =  out | BTN_BIT_1
	if buttons & 0x8000:
		out =  out | BTN_BIT_2
	if buttons & 0x2000:
		out =  out | BTN_BIT_3
	if buttons & 0x1000:
		out =  out | BTN_BIT_4
	if buttons & 0x02:
		out =  out | BTN_BIT_STRUM_DOWN
	if buttons & 0x01:
		out =  out | BTN_BIT_STRUM_UP
	if buttons & 0x10:
		out = out | BTN_BIT_START
	if buttons & 0x20:
		out = out | BTN_BIT_BACK
	if buttons & 0x08:
		out |= BTN_BIT_PAD_DOWN
	if buttons & 0x04:
		out |= BTN_BIT_PAD_UP
 
	return out

def playOp(op):
	if op == '+':
		pass

def playStrum(state):
	if SOUND_ON:
		buttons = GetButtons(state) & 0x1F
		winsound.Beep(50*(buttons+1), 200)

if __name__ == "__main__":
	main()