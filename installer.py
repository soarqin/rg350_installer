# coding=utf-8
from time import sleep
import pygame
import progress
import dialog
import executor
import json
import struct
import subprocess
import sys


class Installer:
    def __init__(self, title, steps):
        if pygame.display.get_init():
            raise RuntimeError('Cannot create 2 installer instances')
        pygame.display.init()
        pygame.font.init()
        self.title = title
        self.steps = steps
        self.step = 0
        self.screen = pygame.display.set_mode((320, 240), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.font = None
        pygame.display.set_caption(title)
        self.runner = None
        self.bg = None
        self.colors = {
            'dialog': ['#FFFFFF', '#101080C0'],
            'button_normal': ['#FFFFFF', '#101080C0'],
            'button_selected': ['#80FF80', '#2020C0C0'],
            'progress': ['#FFFFFF', '#808000C0']
        }

    def __del__(self):
        pygame.font.quit()
        pygame.display.quit()

    def setup_bg(self, bg):
        try:
            self.bg = pygame.image.load(bg)
        except pygame.error:
            self.bg = None

    def setup_colors(self, colors):
        for k, v in colors.items():
            self.colors[k] = v

    def convert_colors(self):
        colors = {}
        for k, v in self.colors.items():
            converted = []
            for c in v:
                if c[0] == '#':
                    c = c[1:]
                if len(c) == 6:
                    converted.append((int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)))
                if len(c) == 8:
                    converted.append((int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)))
            colors[k] = converted
        self.colors = colors
        pass

    def load_fonts(self, fonts):
        for f in fonts:
            try:
                self.font = pygame.font.Font(f, 12)
            except:
                pass
            else:
                return

    def set_runner(self, runner):
        self.runner = runner

    def run_step(self):
        def dialog_confirm(idx):
            self.step = self.steps[self.step]['buttons'][idx]['value']
            return self.run_step()

        def normal_complete():
            self.step = self.steps[self.step]['next']
            return self.run_step()

        if self.step < 0:
            if self.step == -2:
                subprocess.call('reboot', shell=True)
                exit(0)
            return False

        s = self.steps[self.step]
        tp = s['type']
        if tp == 'dialog':
            buttons = [x['name'] for x in s['buttons']]
            size = s['size']
            dialog.Dialog(self, s['text'], buttons, (size[0], size[1]))\
                .set_callbacks(dialog_confirm)
        elif tp == 'executor':
            size = s['size']
            executor.Executor(self, s['command'], s['text'], (size[0], size[1]))\
                .set_callbacks(normal_complete)
        elif tp == 'decompress':
            prg = progress.DecompressionProgress(self, s['text'], s['width'])
            prg.decompress(s['file'], s['targetDir'])
            prg.set_callbacks(normal_complete)
        return True

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.runner:
                        self.runner = None
                    return
                if event.type == pygame.KEYDOWN:
                    if self.runner and not self.runner.key_event(event.key):
                        self.runner = None
                        return
            self.paint_bg()
            if self.runner:
                if not self.runner.process():
                    self.runner = None
                    return
            pygame.display.flip()
            sleep(0.001)

    def paint_bg(self):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0), (0, 0, 320, 240))
        self.draw_string_centered([self.title], (0, 0, 320, 20))

    def draw_string(self, text, offset, color=(255, 255, 255)):
        self.screen.blit(self.font.render(text, True, color), offset)

    def draw_string_centered(self, texts, area, color=(255, 255, 255)):
        line_spacing = 1
        max_w = 0
        max_h = 0
        for text in texts:
            (w, h) = self.font.size(text)
            if max_w < w:
                max_w = w
            if max_h < h:
                max_h = h
        max_h += line_spacing
        x = area[0] + (area[2] - max_w) / 2
        y = area[1] + (area[3] - max_h * len(texts) + line_spacing) / 2
        for text in texts:
            self.screen.blit(self.font.render(text, True, color), (x, y))
            y += max_h

    def fill(self, area, color=(32, 32, 192)):
        if len(color) < 4:
            self.screen.fill(color, area)
        else:
            s = pygame.Surface(area[2:], pygame.SRCALPHA)
            s.fill(color)
            self.screen.blit(s, area[:2])

    def wrap_string(self, texts, w):
        res = []
        f = self.font
        for s in texts:
            while len(s) > 0:
                low = 0
                high = len(s)
                cur = high
                while True:
                    (fw, fh) = f.size(s[0:cur])
                    if fw > w:
                        high = cur - 1
                        cur = (low + cur) / 2
                    else:
                        if cur == high:
                            res.append(s[0:cur])
                            s = s[cur:]
                            break
                        low = cur
                        cur = (low + high + 1) / 2
        return res


if __name__ == '__main__':
    reload(sys)  # Reload does the trick!
    sys.setdefaultencoding('UTF8')

    j = json.load(open('config.json'))
    steps = []
    for k, v in j['steps'].items():
        idx = int(k)
        if idx >= len(steps):
            for n in range(len(steps), idx):
                steps.append({'type': 'none'})
            steps.append(v)
        else:
            steps[idx] = v
    installer = Installer(j['title'], steps)
    if 'bg' in j:
        installer.setup_bg(j['bg'])
    if 'colors' in j:
        installer.setup_colors(j['colors'])
    installer.convert_colors()
    installer.load_fonts(j["fonts"])
    installer.run_step()
    installer.loop()
    installer = None
