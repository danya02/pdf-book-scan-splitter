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
from common import scale_to_screen, draw_transformed

class OverlayRectEditor(UserInterface):
    def __init__(self, images, prop_name, default=True):
        self.images = images
        self.prop_name = prop_name
        self.default_value = default

        self.modes = [pygame.BLEND_MIN, pygame.BLEND_MULT]
        self.mode = 0
        self.color_factor = 0
        self.is_resetting = False

    def on_enter(self):
        pygame.display.set_caption("View overlay image, SPACE switch mode, WASD move rect, ARROWS resize rect, [] move separator")
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
        
        pygame.key.set_repeat(100, 10)

    def on_exit(self):
        pygame.key.set_repeat()

    def render(self):
        rect = pygame.Rect((0,0,0,0))
        for i in range(self.images.count):
            rect.union_ip(self.images[i].get_rect())
        
        self.surface = pygame.Surface(rect.size)
        self.surface.fill('white')
        
        for i in range(self.images.count):
            if self.images.data[i].get(self.prop_name, self.default_value):
                draw_transformed(self.surface, self.images, i, special_flags=self.modes[self.mode])
        self.small_surface = scale_to_screen(self.surface)
        pygame.display.set_mode(self.small_surface.get_size())

    def get_display_rect(self):
        surf = pygame.Surface(self.surface.get_size())
        surf.convert_alpha()
        surf.set_colorkey('black')
        rect = self.images.globals.get('rect', surf.get_rect())
        color = pygame.Color('black')
        color.hsva = (self.color_factor, 100, 100, 100)
        pygame.draw.rect(surf, color, rect, width=5)
        color.hsva = ( (self.color_factor+180)%360, 100, 100, 100)
        offset = self.images.globals.get('offset', rect.width//2)
        pygame.draw.line(surf, color, (rect.x + offset, rect.top), (rect.x+offset, rect.bottom), width=5)
        return scale_to_screen(surf)

    def on_frame(self):
        self.color_factor = (self.color_factor + 1)%360
        screen = pygame.display.get_surface()
        screen.fill('white')
        screen.blit(self.small_surface, (0,0))
        screen.blit(self.get_display_rect(), (0,0))
        pygame.display.update()

        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    if self.is_resetting: continue
                    self.is_resetting = True
                    self.mode += 1
                    self.mode %= len(self.modes)
                    self.on_enter()

                if ev.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                    shifts = {
                            pygame.K_w: (0, -1),
                            pygame.K_a: (-1, 0),
                            pygame.K_s: (0,  1),
                            pygame.K_d: (1,  0)
                            }
                    rect = self.images.globals.get('rect', self.surface.get_rect())
                    ox,oy = shifts[ev.key]
                    rect.x += ox
                    rect.y += oy
                    clipped = rect.clip(self.surface.get_rect())
                    if clipped != rect:
                        rect = clipped
                        self.color_factor += 45

                    self.images.globals.rect = rect

                if ev.key in [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT]:
                    shifts = {
                            pygame.K_UP: (0, -1),
                            pygame.K_LEFT: (-1, 0),
                            pygame.K_DOWN: (0,  1),
                            pygame.K_RIGHT: (1,  0)
                            }
                    rect = self.images.globals.get('rect', self.surface.get_rect())
                    ox,oy = shifts[ev.key]
                    rect.width += ox
                    rect.height += oy
                    clipped = rect.clip(self.surface.get_rect())
                    if clipped != rect:
                        rect = clipped
                        self.color_factor += 45
                if ev.key in [pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET]:
                    rect = self.images.globals.get('rect', self.surface.get_rect())
                    offset = self.images.globals.get('offset', rect.width//2)
                    if ev.key == pygame.K_LEFTBRACKET:
                        offset -= 1
                        if offset <= 0:
                            offset = 1
                            self.color_factor += 45
                    else:
                        offset += 1
                        if offset > rect.width:
                            offset = rect.width - 1
                            self.color_factor += 45
                    self.images.globals.offset = offset
                if ev.key == pygame.K_r:
                    if self.is_resetting:
                        continue
                    if 'offset' in self.images.globals:
                        del self.images.globals.offset
                        self.is_resetting = True
                    else:
                        del self.images.globals.rect
                        self.is_resetting = True

                if ev.key == pygame.K_RETURN and False:
                    rect = self.images.globals.get('rect', self.surface.get_rect())
                    offset = self.images.globals.get('offset', rect.width//2)
                    print(rect)
                    left_rect = rect.copy()
                    left_rect.width = offset
                    right_rect = rect.copy()
                    right_rect.width -= offset
                    right_rect.left = left_rect.right
                    print(left_rect, right_rect)
                    import os
                    os.chdir('/tmp')
                    try:
                        os.mkdir('test')
                    except: pass
                    os.chdir('test')
                    for i in os.listdir('.'):os.unlink(i)

                    for i in range(self.images.count):
                        print(i)
                        left_sub = pygame.Surface(left_rect.size)
                        left_sub.blit(self.images[i], (-left_rect.x, -left_rect.y))
                        right_sub = pygame.Surface(right_rect.size)
                        right_sub.blit(self.images[i], (-right_rect.x, -right_rect.y))
                        pygame.image.save(left_sub, "%3d-01-left.png" % i)
                        pygame.image.save(right_sub, "%3d-02-right.png" % i)
                    raise Exception



            elif ev.type == pygame.KEYUP:
                if ev.key == pygame.K_r or ev.key == pygame.K_SPACE:
                    self.is_resetting = False


                    


