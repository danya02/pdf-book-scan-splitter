import pygame
from user_interface import UserInterface 
from common import scale_to_screen

class PageSelector(UserInterface):
    def __init__(self, images, reason, prop, default=True):
        self.images = images
        self.selected_reason = reason
        self.prop_name = prop
        self.default_value = default
        self.current_page = 0
        self.cached_scaled_image = None

    def on_enter(self):
        pygame.display.set_caption("Select pages to " + self.selected_reason + ": GREEN means selected, toggle SPACE, switch LEFT/RIGHT")
        pygame.display.set_mode((800,600))

    def on_frame(self):
        if self.cached_scaled_image is None:
            self.cached_scaled_image = scale_to_screen(self.images[self.current_page])

        screen = pygame.display.get_surface()
        screen.blit(self.cached_scaled_image, (0, 0))

        rect = self.cached_scaled_image.get_rect()
        color = 'green' if self.default_value else 'darkred'
        if self.prop_name in self.images.data[self.current_page]:
            color = 'green' if self.images.data[self.current_page][self.prop_name] else 'darkred'

        pygame.draw.rect(screen, color, rect, width=20)

        navbar_margin = 5
        navbar_height = 30
        navbar_item_width = (screen.get_width() / self.images.count) - navbar_margin

        navbar_y = int(0.8 * screen.get_height())

        for i in range(self.images.count):
            value = self.default_value
            if self.prop_name in self.images.data[i]:
                value = self.images.data[i][self.prop_name]
            color = 'darkgreen' if value else 'red'
            rect = pygame.Rect((0, 0, navbar_item_width, navbar_height))
            rect.centery = navbar_y
            rect.x = i*(navbar_item_width + navbar_margin)
            pygame.draw.rect(screen, color, rect, width=(0 if i==self.current_page else 5))

        pygame.display.update()

        page_changed = False
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.prop_name in self.images.data[self.current_page]:
                        self.images.data[self.current_page][self.prop_name] = not self.images.data[self.current_page][self.prop_name]
                    else:
                        self.images.data[self.current_page][self.prop_name] = not self.default_value
                elif event.key == pygame.K_LEFT:
                    self.current_page -= 1
                    self.current_page %= self.images.count
                    page_changed = True
                elif event.key == pygame.K_RIGHT:
                    self.current_page += 1
                    self.current_page %= self.images.count
                    page_changed = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button not in (1, 3): continue  # left and right buttons only
                x,y = event.pos
                if not (navbar_y - navbar_height/2 <= y <= navbar_y + navbar_height/2): continue
                for i in range(self.images.count):
                    rect = pygame.Rect((0, 0, navbar_item_width, navbar_height))
                    rect.centery = navbar_y
                    rect.x = i*(navbar_item_width + navbar_margin)
                    if rect.collidepoint(x,y):
                        self.current_page = i
                        page_changed = True


        if page_changed:
            self.cached_scaled_image = scale_to_screen(self.images[self.current_page])
            pygame.display.set_mode(self.cached_scaled_image.get_size())



