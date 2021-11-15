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

def scale_to_screen(img: pygame.Surface) -> pygame.Surface:
    W,H = (800, 600)
    w,h = img.get_size()
    if w>h:
        rw = W
        rh = int(h * (W/w))
    else:
        rh = H
        rw = int(w * (H/h))

    return pygame.transform.scale(img, (rw, rh))

def draw_transformed(target, images, ind, real_surface=None, special_flags=0):
    if real_surface is None:
        real_surface = images[ind]
    scale_fac = images.data[ind].get('scale', 1)
    rot_deg = images.data[ind].get('rotate', 0)
    if scale_fac==1 and rot_deg==0:
        target.blit(real_surface, images.data[ind].get('position', (0,0)), special_flags=special_flags)
        return

    rotated = pygame.transform.rotate(real_surface, rot_deg)
    nx,ny = rotated.get_size()
    nx *= scale_fac
    ny *= scale_fac
    nx = int(nx)
    ny = int(ny)
    zoomed = pygame.transform.scale(rotated, (nx, ny))
    target.blit(zoomed, images.data[ind].get('position', (0,0)), special_flags=special_flags)

