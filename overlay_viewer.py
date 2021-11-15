# Copyright (C) <year>  <name of author>
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
from user_interface import UserInterface
from common import scale_to_screen

class OverlayViewer(UserInterface):
    def __init__(self, images, prop_name, default=True):
        self.images = images
        self.prop_name = prop_name
        self.default_value = default

        self.modes = [pygame.BLEND_MIN, pygame.BLEND_MULT]
        self.mode = 0

    def on_enter(self):
        pygame.display.set_caption("View overlay image, SPACE to switch overlay mode")
        screen = pygame.display.get_surface()
        screen.fill('black')
        font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        text = font.render("Processing...", True, 'white', 'black')
        rect = text.get_rect()
        scr_rect = screen.get_rect()
        rect.center = scr_rect.center
        screen.blit(text, rect)
        pygame.display.update()


        self.render()

    def render(self):
        rect = pygame.Rect((0,0,0,0))
        for i in range(self.images.count):
            rect.union_ip(self.images[i].get_rect())
        
        self.surface = pygame.Surface(rect.size)
        self.surface.fill('white')
        
        for i in range(self.images.count):
            if self.images.data[i].get(self.prop_name, self.default_value):
                self.surface.blit(self.images[i], (0,0), special_flags=self.modes[self.mode])
        self.small_surface = scale_to_screen(self.surface)
        pygame.display.set_mode(self.small_surface.get_size())

    def on_frame(self):
        screen = pygame.display.get_surface()
        screen.fill('white')
        screen.blit(self.small_surface, (0,0))
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    self.mode += 1
                    self.mode %= len(self.modes)
                    self.on_enter()
