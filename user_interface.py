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

import pygame

class UserInterface:
    """ Base class for all UIs. """
    def __init__(self, images):
        """
        images is a ImageCache pointing to the images in the processed PDF.
        """
        self.images = images

    def on_enter(self):
        """
        Called on the first frame when the interface
        is displayed visible on screen. 
        """
        pass

    def on_exit(self):
        """
        Called on the last frame before the interface
        is hidden from the screen.

        This instance may be reused when the interface is next displayed,
        so it must remain functional after this is called.
        """
        pass

    def on_frame(self):
        """
        Called every frame.

        Subclasses are expected to render and process events here.
        """
        pass
