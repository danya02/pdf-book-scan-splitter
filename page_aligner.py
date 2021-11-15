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
        self.frame_timer = float('inf')  # to force a render of the overlay image
        self.render_mode = 0
        self.inv_img = None
        self.overlayable_cache = dict()

    def on_enter(self):
        pygame.display.set_caption("Align pages: WASD move, QE rotate, [] scale, R reset")
        pygame.key.set_repeat(1000, 10)
        if 'overlay_surf' not in self.__dict__:
            self.render_current_overlay()

    def on_exit(self):
        pygame.key.set_repeat()

    def render_current_overlay(self):
        screen = pygame.display.get_surface()
        screen.fill('black')
        font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        text = font.render("Processing...", True, 'white', 'black')
        rect = text.get_rect()
        scr_rect = screen.get_rect()
        rect.center = scr_rect.center
        screen.blit(text, rect)
        pygame.display.update()

        
        rect = pygame.Rect((0,0,0,0))
        for i in range(self.images.count):
            rect.union_ip(self.images[i].get_rect())
        
        self.overlay_surf = pygame.Surface(rect.size)
        self.overlay_surf.fill('white')
        
        for i in range(self.images.count):
            if i == self.current_page: continue
            if self.images.data[i].get("do_overlay", True):
                draw_transformed(self.overlay_surf, self.images, i, special_flags=pygame.BLEND_MIN)

        pygame.event.clear()

    def render_this_page(self):
        self.current_page_overlayable = self.overlayable_cache.get(self.render_mode)
        if self.current_page_overlayable is not None: return

        inv_img = self.inv_img
        if inv_img is None:
            src_img = self.images[self.current_page]
            inv_img = pygame.Surface(src_img.get_size())
            inv_img.fill('white')
            inv_img.blit(src_img, (0,0), special_flags=pygame.BLEND_SUB)
            self.inv_img = inv_img
            del src_img
        inv_buf = bytearray(pygame.image.tostring(inv_img, 'RGB'))
        size = inv_img.get_size()

        for i in range(len(inv_buf)//3):
            inv_buf[i*3] *= int(self.render_mode==0)
            inv_buf[i*3+1] *= int(self.render_mode==1)
            inv_buf[i*3+2] *= int(self.render_mode==2)

        self.current_page_overlayable = pygame.image.frombuffer(inv_buf, size, 'RGB')
        self.current_page_overlayable.set_colorkey('black')
        self.overlayable_cache[self.render_mode] = self.current_page_overlayable

    def on_frame(self):
        self.frame_timer += 1
        if self.frame_timer >= 30:
            self.frame_timer = 0
            self.render_mode += 1
            self.render_mode %= 3
            self.render_this_page()

        target_img = self.overlay_surf.copy()
        draw_transformed(target_img, self.images, self.current_page, real_surface=self.current_page_overlayable)
        target_small = scale_to_screen(target_img)
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
                    self.render_current_overlay()
                    self.inv_img = None
                    self.frame_timer = float('inf')
                    self.overlayable_cache.clear()
                if ev.key == pygame.K_RIGHT:
                    self.current_page += 1
                    self.current_page %= self.images.count
                    self.render_current_overlay()
                    self.inv_img = None
                    self.frame_timer = float('inf')
                    self.overlayable_cache.clear()
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
