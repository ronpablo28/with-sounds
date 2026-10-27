import atexit
import os
import sys

try:
    import winsound
except ImportError:              # hindi Windows
    winsound = None

# Walang kailangang i-install. MCI ay built-in sa Windows at kaya
# ang maraming sound nang sabay, kaya hindi napuputol ang music.
_winmm = None
if sys.platform.startswith("win"):
    try:
        import ctypes
        _winmm = ctypes.windll.winmm
    except Exception:
        _winmm = None

HAS_MCI = _winmm is not None

SOUND_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- SETTINGS (puwede ninyong baguhin) ----------------
SFX_ENABLED = True       # False = walang sound effects
MUSIC_ENABLED = True     # False = walang background music
MUSIC_FILE = "Energizing Game.wav"

# pangalan -> (filename, volume 0.0-1.0)
SFX = {
    # laban
    "bell":          ("bell.wav", 1.0),
    "punch":         ("punch.wav", 1.0),
    "crit":          ("crit.wav", 1.0),
    "ult":           ("ult.wav", 1.0),              # Twin Punch
    "ult_berserk":   ("ult_berserk.wav", 1.0),
    "ult_bloodlust": ("ult_bloodlust.wav", 1.0),
    "ult_lava":      ("ult_lava.wav", 1.0),
    "hurt":          ("hurt.wav", 1.0),
    "roar":          ("roar.wav", 0.9),             # kapag galit na ang kalaban
    "tick":          ("tick.wav", 0.6),             # paubos na ang oras
    "ko_win":        ("ko_win.wav", 1.0),
    "ko_lose":       ("ko_lose.wav", 1.0),
    # menu at shop
    "move":          ("move.wav", 0.6),
    "select":        ("select.wav", 0.7),
    "back":          ("back.wav", 0.7),
    "buy":           ("buy.wav", 0.9),
    "denied":        ("denied.wav", 0.8),
    "cheat":         ("cheat.wav", 1.0),
}

# Ang mga ito ay tumutunog lang kapag gumagana ang MCI. Kapag winsound lang
# ang magagamit, puputulin nila ang background music, kaya nilalaktawan.
MCI_ONLY = {"move", "select", "back", "buy", "denied", "cheat", "tick", "roar"}

_aliases = {}            # name -> MCI alias (o None kapag hindi nabuksan)
_music_on = False


def _mci(command):
    if _winmm is None:
        return -1
    try:
        return _winmm.mciSendStringW(command, None, 0, None)
    except Exception:
        return -1


def _open(name):
    """Buksan ang sound sa MCI isang beses lang, tapos gamitin ulit."""
    if name in _aliases:
        return _aliases[name]
    alias = None
    entry = SFX.get(name)
    if entry and HAS_MCI:
        path = os.path.join(SOUND_DIR, entry[0])
        if os.path.exists(path):
            a = "sfx_" + name
            _mci("close " + a)
            if _mci('open "%s" type waveaudio alias %s' % (path, a)) == 0:
                _mci("setaudio %s volume to %d" % (a, int(entry[1] * 1000)))  # kung hindi suportado, okay lang
                alias = a
    _aliases[name] = alias
    return alias


def preload():
    """I-load na lahat ng sound sa simula para walang delay sa unang tunog."""
    if HAS_MCI and SFX_ENABLED:
        for name in SFX:
            _open(name)


def _close_all():
    if HAS_MCI:
        _mci("close all")


atexit.register(_close_all)


def play_music():
    global _music_on
    if not MUSIC_ENABLED or _music_on:
        return              # tuloy lang ang music, huwag i-restart
    path = os.path.join(SOUND_DIR, MUSIC_FILE)
    if winsound and os.path.exists(path):
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        _music_on = True


def stop_music():
    global _music_on
    if winsound:
        winsound.PlaySound(None, winsound.SND_PURGE)
    _music_on = False


def play_sfx(name):
    if not SFX_ENABLED:
        return
    entry = SFX.get(name)
    if not entry:
        return
    if HAS_MCI:
        alias = _open(name)
        if alias:
            _mci("play %s from 0" % alias)
            return
    # Wala o hindi gumana ang MCI: winsound na lang (isang sound lang sabay)
    if winsound is None or name in MCI_ONLY:
        return
    path = os.path.join(SOUND_DIR, entry[0])
    if not os.path.exists(path):
        return              # kapag walang file, hindi magka-crash ang game
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except RuntimeError:
        pass

preload()

if __name__ == "__main__":
    print("HAS_MCI:", HAS_MCI)
    for n in SFX:
        print(f"{n:15}", "OK" if _aliases.get(n) else "FAILED")