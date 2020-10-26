import platform
if platform.system() == 'Windows':
    import win32con as wcon
    import win32gui as wgui
from pynput import keyboard


class WindowFinder:

    @staticmethod
    def get_scout_handle():
        if platform.system() == 'Windows':
            return wgui.FindWindow(None, "ED Scout v1.4.0")
        else:
            return None

    @staticmethod
    def get_elite_handle():
        if platform.system() == 'Windows':
            return wgui.FindWindow(None, "Elite - Dangerous (CLIENT)")
        else:
            return None

    @staticmethod
    def adjust_window_visibility(window_handle, adjustment):
        if platform.system() == 'Windows':
            wgui.SetWindowPos(window_handle, adjustment, 0, 0, 0, 0,
                              wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)
        else:
            pass


class TransparencySetter:

    def __init__(self, window_title):
        self.transparency = 255
        self.window_title = window_title

        # The key combination to check
        self.COMBINATIONS = [
            {keyboard.Key.cmd, keyboard.KeyCode(char='[')},
            {keyboard.Key.cmd, keyboard.KeyCode(char=']')}
        ]

        # The currently active modifiers
        self.current = set()

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.add(key)
            if any(all(k in self.current for k in COMBO) for COMBO in self.COMBINATIONS):
                if key.char == ']':
                    self.increase_transparency()
                else:
                    self.decrease_transparency()

    def on_release(self, key):
        if any([key in COMBO for COMBO in self.COMBINATIONS]):
            self.current.remove(key)

    def decrease_transparency(self):
        self.transparency = max(self.transparency-10, 5)
        self.set_transparency()

    def increase_transparency(self):
        self.transparency = min(self.transparency+10, 255)
        self.set_transparency()

    def set_transparency(self):
        if platform.system() == 'Windows':
            from EDScoutWebUI.TransparencyAdjuster import set_transparency_by_window
            set_transparency_by_window(self.window_title, self.transparency)


class ScoutToggler:

    def __init__(self):
        # The key combination to check
        self.COMBINATIONS = [
            {keyboard.Key.cmd, keyboard.KeyCode(char='z')},
            {keyboard.Key.cmd, keyboard.KeyCode(char='Z')}
        ]

        # The currently active modifiers
        self.current = set()

        self.scout_toggled = True

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()

    @staticmethod
    def hide_scout():
        scout_handle = WindowFinder.get_scout_handle()
        elite_handle = WindowFinder.get_elite_handle()
        WindowFinder.adjust_window_visibility(scout_handle, elite_handle)

    @staticmethod
    def show_scout():
        scout_handle = WindowFinder.get_scout_handle()
        if platform.system() == 'Windows':
            WindowFinder.adjust_window_visibility(scout_handle, wcon.HWND_TOPMOST)
            WindowFinder.adjust_window_visibility(scout_handle, wcon.HWND_NOTOPMOST)

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
