import xinput
import sys

# These describe the bits that GetButtons() returns. To check for a particular
# button, use the bitwise & operator with the return value of GetButtons()
# with the relevant define(s) below.
BTN_0 = 0x01
BTN_1 = BTN_0 << 1
BTN_2 = BTN_1 << 1
BTN_3 = BTN_2 << 1
BTN_4 = BTN_3 << 1
BTN_5 = BTN_4 << 1
BTN_STRUM_DOWN = BTN_5 << 1
BTN_STRUM_UP = BTN_STRUM_DOWN << 1
BTN_BACK = BTN_STRUM_UP << 1
BTN_START = BTN_BACK << 1
BTN_PAD_DOWN = BTN_START << 1
BTN_PAD_UP = BTN_PAD_DOWN << 1

# Experimentally determined value for a typical low-loss sample rate in Hz.
DEFAULT_SAMPLE_RATE = 200

THROW_EDGE = 25000
THROW_HYSTERESIS = 6000
WHAMMY_EDGE = 0
WHAMMY_HYSTERESIS = 5000

class Guitar:

	# self.controller = xinput.XInputJoystick(0)
	# self.curState = self.controller.get_state()
	# self.prevState = self.curState
	# self.whammyDown = self.GetWhammy() > WHAMMY_EDGE
	# self.prevWhammyDown = self.whammyDown
	# self.thrown = self.GetOrientation() > THROW_EDGE
	# self.prevThrown = self.thrown

	def __init__(self):

		# Set initial values for guitar state
		self.controller = xinput.XInputJoystick(0)
		self.curState = self.controller.get_state()
		# Check a controller is plugged in
		if self.curState is None:
			sys.exit("Please plug in a guitar.")
		self.prevState = self.curState
		self.whammyDown = self.GetWhammy() > WHAMMY_EDGE
		self.prevWhammyDown = self.whammyDown
		self.thrown = self.GetOrientation() > THROW_EDGE
		self.prevThrown = self.thrown

	# Updates state from controller.
	def UpdateGuitar(self):
		self.prevState = self.curState
		self.curState = self.controller.get_state()

		# Update whammy position
		self.prevWhammyDown = self.whammyDown
		if self.whammyDown is False and self.GetWhammy() > WHAMMY_EDGE + WHAMMY_HYSTERESIS:
			self.whammyDown = True
		elif self.whammyDown is True and self.GetWhammy() < WHAMMY_EDGE - WHAMMY_HYSTERESIS:
			self.whammyDown = False

		# Update guitar position
		self.prevThrown = self.thrown
		# Check orientation
		if self.thrown is False and self.GetOrientation() > THROW_EDGE + THROW_HYSTERESIS:
			self.thrown = True
		elif self.thrown is True and self.GetOrientation() < THROW_EDGE - THROW_HYSTERESIS:
			self.thrown = False

	# Returns True if the whammy went from resting to inward position,
	# else returns False.
	def WhammySmacked(self):
		return self.whammyDown and not self.prevWhammyDown


	# Returns True if the whammy went from resting to inward position,
	# else returns False.
	def WhammyReleased(self):
		return self.prevWhammyDown and not self.whammyDown


	# Returns True if the guitar is changed from resting to thrown position,
	# else returns False.
	def GuitarThrown(self):
		return self.thrown and not self.prevThrown


	# Returns True if the guitar is changed from thrown to resting position,
	# else returns False.
	def GuitarReturned(self):
		return self.prevThrown and not self.thrown


	# Returns buttons that were pressed since the last update.
	def ButtonsPressed(self):
		out = self.GetButtons() & ~self.GetButtons(state=self.prevState)
		return out


	# Returns buttons released since last update.
	def ButtonsReleased(self):
		out = self.GetButtons(state=self.prevState) & ~self.GetButtons()
		return out


	# Gets the position of the whammy bar.
	def GetWhammy(self, state=None):
		if state is None:
			state = self.curState
		return state.gamepad.r_thumb_x

	# Gets whammy position on a scale of 0-1, with 0 being resting.
	def GetWhammyScaled(self, state=None):
		if state is None:
			state = self.curState
		out = state.gamepad.r_thumb_x + 32768
		out /= 32768*2
		print(out)
		return out

	# Returns true if whammy has changed
	def WhammyChanged(self):
		return self.GetWhammy() != self.GetWhammy(state=self.prevState)


	# Gets the orientation of the guitar.
	def GetOrientation(self, state=None):
		if state is None:
			state = self.curState
		return state.gamepad.r_thumb_y


	# Gets the states of various buttons.
	def GetButtons(self, state=None):
		if state is None:
			state = self.curState
		out = 0

		buttons = state.gamepad.buttons
		#print("Raw: {0:x}".format(buttons))
		if buttons & 0x100:
			out =  out | BTN_0
		if buttons & 0x4000:
			out =  out | BTN_1
		if buttons & 0x8000:
			out =  out | BTN_2
		if buttons & 0x2000:
			out =  out | BTN_3
		if buttons & 0x1000:
			out =  out | BTN_4
		if buttons & 0x02:
			out =  out | BTN_STRUM_DOWN
		if buttons & 0x01:
			out =  out | BTN_STRUM_UP
		if buttons & 0x10:
			out = out | BTN_START
		if buttons & 0x20:
			out = out | BTN_BACK
		if buttons & 0x08:
			out |= BTN_PAD_DOWN
		if buttons & 0x04:
			out |= BTN_PAD_UP
	 
		return out