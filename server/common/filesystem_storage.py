import multiprocessing

from common.utils import Bet
from common.utils import store_bets, load_bets

class FilesystemStorage:
	def __init__(self):
		self._lock = multiprocessing.Lock()


	def store_bets(self, bets):
		self._lock.acquire()
		store_bets(bets)
		self._lock.release()


	def load_bets(self):
		self._lock.acquire()
		bets = load_bets()
		self._lock.release()

		return bets
