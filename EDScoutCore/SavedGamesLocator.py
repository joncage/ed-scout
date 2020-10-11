

import os
import platform

osname = platform.system()
if osname == 'Windows':
    import winreg

def get_saved_games_path():
    """Returns the default downloads path for linux or windows

    Adapted from this: https://stackoverflow.com/questions/35851281/python-finding-the-users-downloads-folder?lq=1
    """
    save_game_root = None
    osname = platform.system()
    if osname == 'Windows':
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{4C5C32FF-BB9D-43b0-B5B4-2D72E54EAAA4}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        save_game_root = location
    elif osname == 'Linux':
        save_game_root = os.path.join(os.path.expanduser('~'),
                                      '.local',
                                      'share',
                                      'Steam',
                                      'steamapps',
                                      'compatdata',
                                      '359320',
                                      'pfx',
                                      'drive_c',
                                      'users',
                                      'steamuser',
                                      'Saved Games')

    return os.path.join(save_game_root, "Frontier Developments", "Elite Dangerous")



if __name__ == "__main__":
    print(get_saved_games_path())
    assert os.path.exists(get_saved_games_path())
