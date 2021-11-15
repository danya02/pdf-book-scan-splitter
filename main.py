#!/usr/bin/python3
# Copyright (C) 2021  Danya Generalov
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
import pdf2image
import tempfile
import os
import image_cache
from page_selector import PageSelector

src_file = ''
while not os.path.isfile(src_file):
    src_file = input('Path to PDF: ').replace('file://', '').strip()
    print("Converting file", repr(src_file), "to pages...")

temp_dir = tempfile.TemporaryDirectory()
temp_dir_name = temp_dir.name
image_paths = pdf2image.convert_from_path(src_file, output_folder=temp_dir_name, paths_only=True)
images = image_cache.ImageCache(image_paths)

print("Converted PDF into", len(image_paths), "pages")

widths = []
heights = []
print("Determining output resolution...")
for file in image_paths:
    with open(file, 'rb') as f:
        f.readline()  # ignore first line, it is the magic byte
        w, h = map(int, f.readline().strip().decode().split(' '))
        widths.append(w)
        heights.append(h)
SIZE_MARGIN = 100
min_w, max_w = min(widths), max(widths)
min_h, max_h = min(heights), max(heights)

size_warning = False
if max_w - min_w > SIZE_MARGIN:
    print("WARNING: the width varies widely! Min:", min_w, "Max:", max_w)
    size_warning = True
if max_h - min_h > SIZE_MARGIN:
    print("WARNING: the height varies widely! Min:", min_h, "Max:", max_h)
    size_warning = True

if size_warning:
    print("The pages do not appear to be of a similar size. This may cause them to be misaligned.")
    input("Press <ENTER> to proceed...")

print(f"Double page resolution: {max_w}x{max_h}")
double_page_bounds = pygame.Rect((0, 0, max_w, max_h))

MAX_WINDOW_SIZE = (800, 600)
if max_w > max_h:
    disp_w = MAX_WINDOW_SIZE[0]
    disp_h = int(max_h * (disp_w / max_w))
else:
    disp_h = MAX_WINDOW_SIZE[1]
    disp_w = int(max_w * (disp_h / max_h))

interfaces = [PageSelector(images, "include in overlay", "do_overlay", default=True)]
current_interface_index = 0
interfaces[current_interface_index].on_enter()
clock = pygame.time.Clock()
pygame.init()
while 1:
    for event in pygame.event.get(eventtype=pygame.KEYDOWN):
        if event.key != pygame.K_TAB:
            pygame.event.post(event)
            continue
        # tab pressed, switching UIs
        interfaces[current_interface_index].on_exit()
        clock.tick(30)
        current_interface_index += 1
        current_interface_index %= len(interfaces)
        interfaces[current_interface_index].on_enter()
    interfaces[current_interface_index].on_frame()
    clock.tick(30)

input()
