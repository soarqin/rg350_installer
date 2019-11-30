# coding=utf-8
import subprocess
import os
from runner import Runner


class Progress(Runner):
    def __init__(self, installer, text, width):
        Runner.__init__(self, installer)
        self.text = text
        self.w = width
        self.h = 40
        self.x = (320 - width) / 2
        self.y = (240 - 40) / 2
        self.on_complete = None
        self.size = 1
        self.progress = 0

    def set_callbacks(self, on_complete):
        self.on_complete = on_complete

    def draw_progress(self):
        pct = self.progress * 100 / self.size
        area = (self.x, self.y, self.w, self.h)
        self.installer.fill(area, (16, 16, 128))
        area = (self.x, self.y, self.w, 24)
        self.installer.draw_string_centered([self.text], area)
        area = (self.x, self.y + 24, self.w * pct / 100, 16)
        self.installer.fill(area, (128, 192, 16))
        area = (self.x, self.y + 24, self.w, 16)
        self.installer.draw_string_centered([str(pct) + '%'], area)


class DecompressionProgress(Progress):
    def __init__(self, installer, text, area):
        Progress.__init__(self, installer, text, area)
        self.proc = None
        self.fp = None

    def __del__(self):
        if self.fp:
            self.fp.close()
        if self.proc:
            self.proc.stdin.close()
            self.proc.stdout.close()

    def decompress(self, filename, target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, 0755)
        self.size = os.path.getsize(filename)
        self.proc = subprocess.Popen(['tar', 'xzf', '-', '-C', target_dir], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.fp = open(filename, 'rb')

    def process(self):
        chunk = self.fp.read(256 * 1024)
        if chunk == '':
            try:
                subprocess.call('sync', shell=True)
            except:
                pass
            if self.on_complete:
                return self.on_complete()
            else:
                return False
        self.proc.stdin.write(chunk)
        self.progress += len(chunk)
        self.draw_progress()
        return True
