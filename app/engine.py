import random
import string
import threading
import time

import pyautogui

# pyautogui adds a hidden 0.1s pause after EVERY call (write, press, etc)
# by default. That stacks on top of our own timing model and makes real
# typing much slower than intended, so it's disabled here — ONLY our
# custom delay model controls the speed.
pyautogui.PAUSE = 0

# Keys physically near each other on a QWERTY layout, used to generate
# plausible fat-finger typos.
NEARBY_KEYS = {
    'a': 'sqwz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfcx', 'e': 'wsdr',
    'f': 'drtgvc', 'g': 'ftyhbv', 'h': 'gyujnb', 'i': 'ujko', 'j': 'huikmn',
    'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
    'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awedxz', 't': 'rfgy',
    'u': 'yhji', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc', 'y': 'tghu',
    'z': 'asx',
}

# Default timing model (seconds), used unless the UI's Delay settings
# override them.
DEFAULT_MIN_DELAY = 0.135
DEFAULT_MAX_DELAY = 0.18
DEFAULT_TYPO_RATE = 0.035


class TypingEngine:
    """Humanized typing engine driven by pyautogui.

    Types text character by character with punctuation/newline/space
    pauses, a warm-up + speed-drift model, and occasional realistic
    typos that get "noticed" and corrected — all controllable at
    runtime (pause/resume/stop) and tunable (delay range, typo rate).
    """

    def __init__(
        self,
        min_delay=DEFAULT_MIN_DELAY,
        max_delay=DEFAULT_MAX_DELAY,
        typo_rate=DEFAULT_TYPO_RATE,
    ):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.typo_rate = typo_rate

        self._stop_event = threading.Event()
        # Set = running, cleared = paused. Starts set (not paused).
        self._pause_event = threading.Event()
        self._pause_event.set()

    # -----------------------------------------
    # Runtime configuration
    # -----------------------------------------

    def set_delay_range(self, min_delay, max_delay):
        self.min_delay = min(min_delay, max_delay)
        self.max_delay = max(min_delay, max_delay)

    def set_typo_rate(self, rate):
        self.typo_rate = max(0.0, min(1.0, rate))

    # -----------------------------------------
    # Controls
    # -----------------------------------------

    def stop(self):
        self._stop_event.set()
        # Wake up immediately even if currently paused.
        self._pause_event.set()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    # -----------------------------------------
    # Internal helpers
    # -----------------------------------------

    def _typo_char(self, ch):
        lower = ch.lower()
        if lower in NEARBY_KEYS:
            wrong = random.choice(NEARBY_KEYS[lower])
            return wrong.upper() if ch.isupper() else wrong
        return random.choice(string.ascii_lowercase)

    def _character_delay(self, char, previous_char, speed_factor):
        if char in ".,!?;:":
            return random.uniform(0.145, 0.205)

        if char == "\n":
            return random.uniform(0.21, 0.29)

        if char == " ":
            return random.uniform(0.075, 0.10)

        if previous_char in ".,!?;:":
            return random.uniform(0.095, 0.125)

        delay = random.uniform(self.min_delay, self.max_delay) * speed_factor

        # Occasional hesitation
        if random.random() < 0.025:
            delay += random.uniform(0.04, 0.07)

        return delay

    def _type_char(self, ch):
        if ch == "\n":
            pyautogui.press("enter")
        else:
            pyautogui.write(ch)

    def _backspace(self):
        pyautogui.press("backspace")

    def _sleep(self, seconds):
        """Sleep in small chunks so stop()/pause() interrupt promptly."""
        end = time.time() + seconds

        while True:
            if self._stop_event.is_set():
                return

            if not self._pause_event.is_set():
                self._pause_event.wait()
                continue

            remaining = end - time.time()
            if remaining <= 0:
                return

            time.sleep(min(0.02, remaining))

    # -----------------------------------------
    # Main entry point
    # -----------------------------------------

    def type_text(self, text, wpm, on_progress=None):
        """Type `text` at roughly `wpm` words per minute.

        Calls on_progress(chars_typed, total_chars) after every
        character so the UI can render live progress. Returns
        "Completed" or "Stopped".
        """
        self._stop_event.clear()
        self._pause_event.set()

        total_chars = len(text)
        previous_char = ""
        speed_factor = 1.08  # start slightly slower (warm-up)
        chars_typed = 0

        # Scale the base delay range so the requested WPM is roughly
        # honored: ~5 chars per word -> target seconds/char.
        target_char_time = 60.0 / max(1, wpm) / 5.0
        base_mid = (self.min_delay + self.max_delay) / 2
        wpm_scale = (target_char_time / base_mid) if base_mid > 0 else 1.0

        for char in text:
            if self._stop_event.is_set():
                return "Stopped"

            if not self._pause_event.is_set():
                self._pause_event.wait()

            if self._stop_event.is_set():
                return "Stopped"

            # Occasionally mistype, notice it, and correct it
            if (
                self.typo_rate > 0
                and char not in (" ", "\n")
                and random.random() < self.typo_rate
            ):
                wrong = self._typo_char(char)
                self._type_char(wrong)
                self._sleep(
                    random.uniform(self.min_delay, self.max_delay)
                    * speed_factor
                    * wpm_scale
                )

                self._sleep(random.uniform(0.08, 0.16))
                self._backspace()
                self._sleep(
                    random.uniform(self.min_delay, self.max_delay)
                    * 0.7
                    * wpm_scale
                )

                if self._stop_event.is_set():
                    return "Stopped"

            self._type_char(char)

            delay = self._character_delay(char, previous_char, speed_factor)
            self._sleep(delay * wpm_scale)

            previous_char = char
            chars_typed += 1

            if on_progress:
                on_progress(chars_typed, total_chars)

            # Warm-up: ease speed_factor from 1.08 down to ~1.0 over
            # the first ~15 characters.
            if chars_typed <= 15:
                speed_factor = max(1.0, 1.08 - (chars_typed / 15) * 0.08)

            # Drift speed slowly (burst typing then slowing down)
            speed_factor += random.uniform(-0.008, 0.008)
            speed_factor = min(1.08, max(0.94, speed_factor))

        return "Completed"