# Copyright (C) 2021 Danya Generalov
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import weakref
import pygame

# js-style object implementation from http://www.adequatelygood.com/JavaScript-Style-Objects-in-Python.html
class JsObject(object):
	def __init__(self, *args, **kwargs):
		for arg in args:
			self.__dict__.update(arg)

		self.__dict__.update(kwargs)

	def __getitem__(self, name):
		return self.__dict__.get(name, None)

	def __setitem__(self, name, val):
		return self.__dict__.__setitem__(name, val)

	def __delitem__(self, name):
		if self.__dict__.has_key(name):
			del self.__dict__[name]

	def __getattr__(self, name):
		return self.__getitem__(name)

	def __setattr__(self, name, val):
		return self.__setitem__(name, val)

	def __delattr__(self, name):
		return self.__delitem__(name)

	def __iter__(self):
		return self.__dict__.__iter__()

	def __repr__(self):
		return self.__dict__.__repr__()

	def __str__(self):
		return self.__dict__.__str__()

	def get(self, *args, **kwargs):
		return self.__dict__.get(*args, **kwargs)


class ImageCache:
    def __init__(self, images):
        self.image_paths = images
        self.image_refs = dict()
        self.data = [JsObject() for _ in images]

    def get_real_image(self, item):
        img = pygame.image.load(self.image_paths[item])
        self.image_refs[item] = weakref.ref(img)
        return img

    def __getitem__(self, item):
        if item not in self.image_refs:
            return self.get_real_image(item)
        ref = self.image_refs[item]
        image = ref()
        if not image:
            return self.get_real_image(item)
        else:
            return image

    @property
    def count(self):
        return len(self.image_paths)
