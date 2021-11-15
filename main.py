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
from overlay_rect_editor import OverlayRectEditor
from page_aligner import PageAligner
import PIL
import common
import io

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

interfaces = [PageSelector(images, "include in overlay", "do_overlay", default=True), OverlayRectEditor(images, "do_overlay", default=True), PageAligner(images)]
current_interface_index = 0
interfaces[current_interface_index].on_enter()
clock = pygame.time.Clock()
pygame.init()
pygame.display.set_mode((800, 600))

def save(images):
    print("Saving initiated!")
    path = input("Path to save PDF to (no extension): ") + ".pdf"
    rect = images.globals.get('rect', double_page_bounds)
    offset = images.globals.get('offset', rect.width//2)
    left_rect = rect.copy()
    left_rect.width = offset
    right_rect = rect.copy()
    right_rect.width -= offset
    right_rect.left = left_rect.right
    pil_img = []
    for i in range(images.count):
        print("Rendering page", i)
        trans_img = pygame.Surface(images[i].get_rect().inflate(images[i].get_size()).size)
        trans_img.fill('white')
        common.draw_transformed(trans_img, images, i)
        left_sub = pygame.Surface(left_rect.size)
        left_sub.blit(trans_img, (-left_rect.x, -left_rect.y))
        right_sub = pygame.Surface(right_rect.size)
        right_sub.blit(trans_img, (-right_rect.x, -right_rect.y))
        left = io.BytesIO()
        right = io.BytesIO()
        pygame.image.save(left_sub, left, "left.pbm")
        pygame.image.save(right_sub, right, "right.pbm")
        pil_img.append(PIL.Image.open(left))
        pil_img.append(PIL.Image.open(right))

    print("Writing all pages to file...")
    pil_img[0].save(path, "PDF", resolution=100.0, save_all=True, append_images=pil_img[1:])
    print("Saving completed!")
    

while 1:
    for event in pygame.event.get(eventtype=pygame.KEYDOWN):
        if event.key not in [pygame.K_TAB, pygame.K_RETURN]:
            pygame.event.post(event)
            continue
        if event.key == pygame.K_TAB:
            interfaces[current_interface_index].on_exit()
            clock.tick(30)
            current_interface_index += 1
            current_interface_index %= len(interfaces)
            interfaces[current_interface_index].on_enter()
        elif event.key == pygame.K_RETURN:
            screen = pygame.display.get_surface()
            screen.fill('black')
            font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
            text = font.render("Switch to the terminal now.", True, 'white', 'black')
            rect = text.get_rect()
            scr_rect = screen.get_rect()
            rect.center = scr_rect.center
            screen.blit(text, rect)
            pygame.display.update()
            
            save(images)
            
    interfaces[current_interface_index].on_frame()
    clock.tick(30)
