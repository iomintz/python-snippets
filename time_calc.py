#!/usr/bin/env python3
# encoding: utf-8

"""
my attempt at doing a four-function time calculator

maybe use the datetime module instead
"""

from numbers import Integral as _Integral, Real as _Real
import operator as _operator

from simple_rstrip import rstrip

class Time:
	"""represents either:
		- an absolute time of day, such as 23:34:03, or
		- a duration of time, such as 23 hours, 34 minutes, and 3 seconds
	"""

	__slots__ = ('days', 'hours', 'minutes', 'seconds')

	def __new__(cls, hours: _Integral = 0, minutes: _Integral = 0, seconds: _Real = 0, *, days: _Integral = 0):
		self = super().__new__(cls)

		# a silly way to achieve immutability
		# we do this because our __setattr__ denies access
		super(cls, self).__setattr__('days', days)
		super(cls, self).__setattr__('hours', hours)
		super(cls, self).__setattr__('minutes', minutes)
		super(cls, self).__setattr__('seconds', seconds)

		return self

	@classmethod
	def from_seconds(cls, seconds: _Real):
		minutes, seconds = divmod(seconds, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		return cls(int(hours), int(minutes), seconds, days=int(days))

	def total_seconds(self) -> _Real:
		return 60**2 * (self.hours + 24 * self.days) + 60 * self.minutes + self.seconds

	def __float__(self):
		return float(self.total_seconds())

	def normalize(self):
		"""return a copy of self where minutes and seconds do not exceed 59

		leap seconds are NOT ALLOWED :<
		"""
		return self.from_seconds(self.total_seconds())

	def __sub__(self, other: 'Time'):
		"""implements self - other"""
		# subtraction and addition require that *other* be typed
		# because 5:03:02 - 3 is undefined (3 seconds, minutes, or hours?)
		return self.from_seconds(self.total_seconds() - other.total_seconds())

	def __add__(self, other: 'Time'):
		"""implements self + other"""
		return self.from_seconds(self.total_seconds() + other.total_seconds())

	def __mul__(self, other: _Real):
		"""implements self * other"""
		return self.from_seconds(self.total_seconds() * other)

	def __truediv__(self, other: _Real):
		return self.from_seconds(self.total_seconds() / other)

	def __floordiv__(self, other: _Real):
		return self.from_seconds(self.total_seconds() // other)

	def __repr__(self):
		t = self.normalize()

		# Time(5, 4, 0) -> Time(5, 4)
		# Time(0, 0, 0) -> Time()
		no_trailing_zeros = rstrip([t.hours, t.minutes, t.seconds], lambda x: x == 0)
		kwargs = ''
		if t.days:
			kwargs = f'days={t.days!r}'

		pos_args = ', '.join(map(repr, no_trailing_zeros))
		if not pos_args or not kwargs:
			args = pos_args or kwargs
		else:
			args = f'{pos_args}, {kwargs}'
		return f'{type(self).__qualname__}({args})'

	def __str__(self):
		seconds = float(self.seconds)  # allow zero padding even if seconds is a Fraction
		s = '{0.hours}:{0.minutes:02}:{seconds:04}'.format(self.normalize(), seconds=seconds)
		if self.days:
			return f'{self.days}d {s}'
		return s

	def __hash__(self):
		t = self.normalize()
		return hash((t.days, t.hours, t.minutes, t.seconds))

	def __setattr__(self, name, *_):
		raise TypeError(f'{type(self).__qualname__} objects are immutable')

	__delattr__ = __setattr__
