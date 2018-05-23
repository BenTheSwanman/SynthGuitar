# Handles synth data in a convenient object.
class SynthController:

	def __init__(self):
		self.sources = {}
		self.frets={}
		return

	def AddSource(self, name, source):
		self.sources[name] = source
		self.frets[name] = 1
		return

	def StopSource(self, name):
		self.sources[name].stop()
		return

	def OutSource(self, name):
		self.sources[name].out()
		return

	def OutAllSources(self):
		for source in self.sources.values():
			source.out()
		return

	def StopAllSources(self):
		for source in self.sources.values():
			source.stop()
		return