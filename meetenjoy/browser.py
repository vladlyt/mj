import os
import subprocess
import sys


class Browser:

    def __init__(self, platform: str = None):
        platform = platform or sys.platform
        if platform == 'win32':
            method = self.windows
        elif platform == 'darwin':
            method = self.macos
        else:
            method = self.other
        self.method = method

    def windows(self, url):
        os.startfile(url)

    def macos(self, url):
        subprocess.Popen(['open', url])

    def other(self, url):
        try:
            subprocess.Popen(['xdg-open', url])
        except OSError:
            print('Please open a browser on: ' + url)

    def open_url(self, url):
        return self.method(url)
