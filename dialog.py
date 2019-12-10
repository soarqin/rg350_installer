# coding=utf-8
import pygame
from runner import Runner


class Dialog(Runner):
    def __init__(self, installer, text, buttons, area=(320, 240), wrap=True):
        Runner.__init__(self, installer)
        if wrap:
            self.text = installer.wrap_string(text.splitlines(), area[0] - 8)
        else:
            self.text = text.splitlines()
        self.buttons = buttons
        self.index = 0
        self.w = area[0]
        self.h = area[1]
        self.text_w = area[0]
        self.text_h = area[1] - 20
        self.button_w = area[0]
        self.button_h = 18
        self.on_press = None
        self.on_cancel = None

    def set_selection(self, index):
        self.index = index

    def set_callbacks(self, on_press, on_cancel = None):
        self.on_press = on_press
        self.on_cancel = on_cancel

    def process(self):
        x = (320 - self.w) / 2
        y = (240 - self.h) / 2
        area = (x, y, self.text_w, self.text_h)
        self.installer.fill(area, (16, 16, 128, 192))
        self.installer.draw_string_centered(self.text, area)
        button_y = y + self.h - self.button_h
        count = len(self.buttons)
        if count > 0:
            button_w = (self.button_w + 2) / count - 2
            button_x = x
            index = 0
            for btn in self.buttons[:count-1]:
                area = (button_x, button_y, button_w, self.button_h)
                if index == self.index:
                    self.installer.fill(area, (32, 32, 192, 192))
                    self.installer.draw_string_centered([btn], area, (128, 255, 128))
                else:
                    self.installer.fill(area, (16, 16, 128, 192))
                    self.installer.draw_string_centered([btn], area)
                button_x += button_w + 2
                index += 1
            area = (button_x, button_y, x + self.button_w - button_x, self.button_h)
            if index == self.index:
                self.installer.fill(area, (32, 32, 192, 192))
                self.installer.draw_string_centered([self.buttons[count - 1]], area, (128, 255, 128))
            else:
                self.installer.fill(area, (16, 16, 128, 192))
                self.installer.draw_string_centered([self.buttons[count - 1]], area)
        return True

    def key_event(self, key):
        if key == pygame.K_LEFT:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.buttons) - 1
        elif key == pygame.K_RIGHT:
            self.index += 1
            if self.index >= len(self.buttons):
                self.index = 0
        elif key == pygame.K_RETURN or key == pygame.K_LCTRL:
            if self.on_press:
                return self.on_press(self.index)
        elif key == pygame.K_ESCAPE or key == pygame.K_LALT:
            if self.on_cancel:
                return self.on_cancel()
        return True
