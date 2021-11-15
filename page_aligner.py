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
from user_interface import UserInterface
from common import draw_transformed, scale_to_screen


class PageAligner(UserInterface):
    def __init__(self, images):
        self.images = images
        self.current_page = 0
        self.color_factor = 0

    def on_enter(self):
        pygame.display.set_caption("Align pages: WASD move, QE rotate, [] scale, R reset")
        pygame.key.set_repeat(200, 10)

    def on_exit(self):
        pygame.key.set_repeat()
    
    def get_fullsize_rect(self):
        surf = pygame.Surface(self.images[self.current_page].get_size())
        surf.convert_alpha()
        surf.set_colorkey('black')
        rect = self.images.globals.get('rect', surf.get_rect())
        color = pygame.Color('black')
        color.hsva = (self.color_factor, 100, 100, 100)
        pygame.draw.rect(surf, color, rect, width=5)
        color.hsva = ( (self.color_factor+180)%360, 100, 100, 100)
        offset = self.images.globals.get('offset', rect.width//2)
        pygame.draw.line(surf, color, (rect.x + offset, rect.top), (rect.x+offset, rect.bottom), width=5)
        return surf

    def on_frame(self):
        self.color_factor += 1
        self.color_factor %= 360
        full_rect = self.get_fullsize_rect()
        target = pygame.Surface(full_rect.get_size())
        draw_transformed(target, self.images, self.current_page)
        target.blit(full_rect, (0,0))
        target_small = scale_to_screen(target)
        screen = pygame.display.get_surface()
        if screen.get_size() != target_small.get_size():
            screen = pygame.display.set_mode(target_small.get_size())
        screen.blit(target_small, (0,0))
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    self.current_page -= 1
                    self.current_page %= self.images.count
                if ev.key == pygame.K_RIGHT:
                    self.current_page += 1
                    self.current_page %= self.images.count
                if ev.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    offsets = {
                            pygame.K_w: (0, -1),
                            pygame.K_a: (-1, 0),
                            pygame.K_s: (0,  1),
                            pygame.K_d: (1,  0)
                            }
                    x,y = self.images.data[self.current_page].get('position', (0,0))
                    ox,oy = offsets[ev.key]
                    self.images.data[self.current_page].position = (x+ox, y+oy)

                if ev.key in [pygame.K_q, pygame.K_e]:
                    rot = self.images.data[self.current_page].get('rotate', 0)
                    if ev.key == pygame.K_q:
                        rot -= 1
                    else:
                        rot += 1
                    self.images.data[self.current_page].rotate = rot

                if ev.key in [pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET]:
                    scale_fac = self.images.data[self.current_page].get('scale', 1)
                    if ev.key == pygame.K_LEFTBRACKET:
                        scale_fac *= 0.9
                        scale_fac = max(scale_fac, 0.01)
                    else:
                        scale_fac *= 1.1
                    self.images.data[self.current_page].scale = scale_fac

                if ev.key == pygame.K_r:
                    del self.images.data[self.current_page].position
                    del self.images.data[self.current_page].rotate
                    del self.images.data[self.current_page].scale
