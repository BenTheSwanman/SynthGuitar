import sched
import time
from SynthController import SynthController
from GuitarInput import *
from pyo import *

baseFreq = 100
samplePeriod = 0.005


def main():
	# Initialize pyo server
	s = Server(winhost="asio").boot()
	s.start()

	# Set basic server params
	s.amp = 0.1
	#a = Sine(freq=baseFreq)

	# Init guitar
	g = Guitar()

	# Init synth controller
	sc = SynthController()
	sc.AddSource("base", Sine(freq=baseFreq))
	#sc.AddSource("base", Noise())

	# Start update scheduler
	scheduler = sched.scheduler(time.time, time.sleep)
	scheduler.enter(samplePeriod, 1, UpdateSynth, (g, sc, scheduler))
	scheduler.run()

	while(1):
		# Wait for scheduler
		pass


def UpdateSynth(guitar, sc, scheduler):
	# Restart scheduler immediately to uphold sample rate
	scheduler.enter(samplePeriod, 1, UpdateSynth, (guitar, sc, scheduler))

	# Update state of guitar
	guitar.UpdateGuitar()

	# Check for inputs
	buttons = guitar.GetButtons()
	frets = buttons & 0x1F + 1

	# Check to begin sound
	buttonsPressed = guitar.ButtonsPressed()
	if buttonsPressed & BTN_STRUM_DOWN:
		sc.sources["base"].setFreq(baseFreq*frets)
		sc.frets["base"] = frets
		sc.OutAllSources()

	# Check to end sound
	if buttonsPressed & BTN_STRUM_UP:
		sc.StopAllSources()

	# Check for whammy modifier
	if guitar.WhammyChanged():
		pureFreq = sc.frets["base"]*baseFreq
		updatedFreq = (1 + guitar.GetWhammyScaled())*pureFreq
		sc.sources["base"].setFreq(updatedFreq)

	# Check released buttons to turn sound off
	if guitar.ButtonsReleased() & BTN_STRUM_DOWN:
		#sc.StopAllSources()
		pass

	# If strumming down
	if buttons & BTN_STRUM_DOWN:
		# Play tone for current button press
		#sc.sources["base"].setFreq(baseFreq*(frets+1))
		pass

if __name__ == "__main__":
	main()