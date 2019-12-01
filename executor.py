# coding=utf-8
import pygame
import subprocess
from runner import Runner


class Executor(Runner):
    def __init__(self, installer, command, text, area=(320, 240), wrap=True):
        Runner.__init__(self, installer)
        if wrap:
            self.text = installer.wrap_string(text.splitlines(), area[0] - 8)
        else:
            self.text = text.splitlines()
        self.w = area[0]
        self.h = area[1]
        self.on_complete = None
        if isinstance(command, list):
            self.proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.proc = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(self.proc.pid)

    def __del__(self):
        if self.proc:
            self.proc.stdout.close()
            self.proc.stderr.close()

    def set_callbacks(self, on_complete):
        self.on_complete = on_complete

    def process(self):
        x = (320 - self.w) / 2
        y = (240 - self.h) / 2
        area = (x, y, self.w, self.h)
        self.installer.fill(area, (16, 16, 128))
        self.installer.draw_string_centered(self.text, area)
        if self.proc.poll() is not None:
            if self.on_complete:
                return self.on_complete()
            else:
                return False
        return True
