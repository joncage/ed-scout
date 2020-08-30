import win32con as wcon
import win32gui as wgui
from pynput import keyboard


def get_scout_handle():
    return wgui.FindWindow(None, "ED Scout v1.4.0")


def get_elite_handle():
    return wgui.FindWindow(None, "Elite - Dangerous (CLIENT)")


def hide_scout():
    scout_handle = get_scout_handle()
    elite_handle = get_elite_handle()
    wgui.SetWindowPos(scout_handle, elite_handle, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)


def show_scout():
    scout_handle = get_scout_handle()
    wgui.SetWindowPos(scout_handle, wcon.HWND_TOPMOST, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)
    wgui.SetWindowPos(scout_handle, wcon.HWND_NOTOPMOST, 0,0,0,0, wcon.SWP_NOMOVE | wcon.SWP_NOSIZE | wcon.SWP_NOACTIVATE)

#############

# The key combination to check
COMBINATIONS = [
    {keyboard.Key.cmd, keyboard.KeyCode(char='z')},
    {keyboard.Key.cmd, keyboard.KeyCode(char='Z')}
]

# The currently active modifiers
current = set()

scout_toggled = False

def execute():
    global scout_toggled
    if scout_toggled:
        hide_scout()
    else:
        show_scout()
    scout_toggled = not scout_toggled

def on_press(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            execute()

def on_release(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.remove(key)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()


if __name__ == "__main__":
    #show_scout()
    #import time
    #time.sleep(1)
    #hide_scout()
    pass
