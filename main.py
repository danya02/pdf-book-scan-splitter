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

src_file = ''
while not os.path.isfile(src_file):
    src_file = input('Path to PDF: ').replace('file://', '').strip()
    print("Converting file", repr(src_file), "to pages...")

temp_dir = tempfile.TemporaryDirectory()
temp_dir_name = temp_dir.name
image_paths = pdf2image.convert_from_path(src_file, output_folder=temp_dir_name, paths_only=True)

print("Converted PDF into", len(image_paths), "pages")

