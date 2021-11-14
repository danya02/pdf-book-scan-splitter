import weakref
import pygame

class ImageCache:
    def __init__(self, images):
        self.image_paths = images
        self.image_refs = dict()

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
