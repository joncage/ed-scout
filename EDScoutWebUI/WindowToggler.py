import win32con as wcon
import win32gui as wgui
from pynput import keyboard


class ScoutToggler:

    def __init__(self):
        # The key combination to check
        self.COMBINATIONS = [
            {keyboard.Key.cmd, keyboard.KeyCode(char='z')},
            {keyboard.Key.cmd, keyboard.KeyCode(char='Z')}
        ]

        # The currently active modifiers
        self.current = set()

        self.scout_toggled = False

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    @staticmethod
    def get_scout_handle():
        return wgui.FindWindow(None, "ED Scout v1.4.0")

    @staticmethod
    def get_elite_handle():
        return wgui.FindWindow(None, "Elite - Dangerous (CLIENT)")

    @staticmethod
    def hide_scout():
        scout_handle = ScoutToggler.get_scout_handle()
        elite_handle = ScoutToggler.get_elite_handle()
        wgui.SetWindowPos(scout_handle, elite_handle, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)

    @staticmethod
    def show_scout():
        scout_handle = ScoutToggler.get_scout_handle()
        wgui.SetWindowPos(scout_handle, wcon.HWND_TOPMOST, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)
        wgui.SetWindowPos(scout_handle, wcon.HWND_NOTOPMOST, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)

    def toggle_scout_visibility(self):
        self.scout_toggled
        if self.scout_toggled:
            ScoutToggler.hide_scout()
        else:
            ScoutToggler.show_scout()
        self.scout_toggled = not self.scout_toggled

    def on_press(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.add(key)
            if any(all(k in self.current for k in COMBO) for COMBO in self.COMBINATIONS):
                self.toggle_scout_visibility()

    def on_release(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.remove(key)
