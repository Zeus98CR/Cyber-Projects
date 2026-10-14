import math
import struct
import wave
import array
import os

# ============================================================
# MORSE CODE TABLE
# ============================================================

MORSE = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",
    "E": ".",     "F": "..-.", "G": "--.",   "H": "....",
    "I": "..",    "J": ".---", "K": "-.-",   "L": ".-..",
    "M": "--",    "N": "-.",   "O": "---",   "P": ".--.",
    "Q": "--.-",  "R": ".-.",  "S": "...",   "T": "-",
    "U": "..-",   "V": "...-", "W": ".--",   "X": "-..-",
    "Y": "-.--",  "Z": "--..",

    "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..",
    "9": "----.",

    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "'": ".----.",
    "!": "-.-.--",
    "/": "-..-.",
    "(": "-.--.",
    ")": "-.--.-",
    "&": ".-...",
    ":": "---...",
    ";": "-.-.-.",
    "=": "-...-",
    "+": ".-.-.",
    "-": "-....-",
    "_": "..--.-",
    '"': ".-..-.",
    "$": "...-..-",
    "@": ".--.-."
}

REVERSE_MORSE = {value: key for key, value in MORSE.items()}


# ============================================================
# TEXT <-> MORSE
# ============================================================

def text_to_morse(text):
    """
    Convert normal text into Morse code.

    Spaces between Morse characters represent letters.
    '/' represents a word space.
    """

    words = text.upper().split()

    encoded_words = []

    for word in words:
        encoded_letters = []

        for character in word:
            if character in MORSE:
                encoded_letters.append(MORSE[character])
            else:
                print(f"Warning: unsupported character ignored: {character}")

        encoded_words.append(" ".join(encoded_letters))

    return " / ".join(encoded_words)


def morse_to_text(morse):
    """
    Convert Morse code back into normal text.
    """

    words = morse.strip().split(" / ")

    decoded_words = []

    for word in words:
        letters = word.split()
        decoded = ""

        for letter in letters:
            if letter in REVERSE_MORSE:
                decoded += REVERSE_MORSE[letter]
            else:
                decoded += "?"

        decoded_words.append(decoded)

    return " ".join(decoded_words)


# ============================================================
# AUDIO GENERATION
# ============================================================

SAMPLE_RATE = 44100
FREQUENCY = 700

# Duration of one Morse timing unit in seconds.
UNIT = 0.10


def generate_tone(duration, frequency=FREQUENCY):
    """
    Generate a sine-wave tone.
    """

    samples = []

    number_of_samples = int(SAMPLE_RATE * duration)

    for i in range(number_of_samples):
        t = i / SAMPLE_RATE

        # Sine wave
        value = math.sin(2 * math.pi * frequency * t)

        # Convert to 16-bit audio
        sample = int(value * 32767)

        samples.append(sample)

    return samples


def generate_silence(duration):
    """
    Generate silence for a specified duration.
    """

    number_of_samples = int(SAMPLE_RATE * duration)

    return [0] * number_of_samples


def morse_to_audio_samples(morse):
    """
    Convert Morse code into raw audio samples.

    Timing:
        dot       = 1 unit
        dash      = 3 units
        gap inside character = 1 unit
        gap between characters = 3 units
        gap between words = 7 units
    """

    audio = []

    # Remove accidental leading/trailing whitespace
    morse = morse.strip()

    i = 0

    while i < len(morse):

        character = morse[i]

        # Word separator
        if character == "/":
            audio.extend(generate_silence(7 * UNIT))
            i += 1

            # Skip spaces following /
            while i < len(morse) and morse[i] == " ":
                i += 1

            continue

        # Morse dot
        elif character == ".":
            audio.extend(generate_tone(1 * UNIT))

            # Gap between elements
            audio.extend(generate_silence(1 * UNIT))

        # Morse dash
        elif character == "-":
            audio.extend(generate_tone(3 * UNIT))

            # Gap between elements
            audio.extend(generate_silence(1 * UNIT))

        # Space between Morse letters
        elif character == " ":

            # We already add one unit after every dot/dash.
            # Add two more units to make a total of three.
            audio.extend(generate_silence(2 * UNIT))

            # Skip additional spaces
            while i + 1 < len(morse) and morse[i + 1] == " ":
                i += 1

        i += 1

    return audio


def save_wav(samples, filename):
    """
    Save 16-bit mono PCM audio as a WAV file.
    """

    with wave.open(filename, "wb") as wav:

        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)

        frames = array.array("h", samples)

        wav.writeframes(frames.tobytes())


def morse_to_wav(morse, filename="morse.wav"):
    """
    Convert Morse code into a WAV file.
    """

    print("Generating audio...")

    samples = morse_to_audio_samples(morse)

    save_wav(samples, filename)

    print(f"Audio saved to: {os.path.abspath(filename)}")


# ============================================================
# SIMPLE AUDIO DECODER
# ============================================================

def read_wav(filename):
    """
    Read a mono WAV file and return its samples.
    """

    with wave.open(filename, "rb") as wav:

        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()

        if channels != 1:
            raise ValueError("WAV must be mono.")

        if sample_width != 2:
            raise ValueError("WAV must use 16-bit samples.")

        frames = wav.readframes(wav.getnframes())

    samples = list(struct.unpack("<" + "h" * (len(frames) // 2), frames))

    return samples, sample_rate


def detect_signal(samples, threshold=3000):
    """
    Convert audio samples into:

        True  = tone
        False = silence

    This is intentionally simple so the algorithm is easy to understand.
    """

    result = []

    for sample in samples:

        if abs(sample) > threshold:
            result.append(True)
        else:
            result.append(False)

    return result


def group_signal(signal):
    """
    Convert a sequence such as:

        True True True False False False ...

    into duration groups.
    """

    if not signal:
        return []

    groups = []

    current = signal[0]
    count = 1

    for value in signal[1:]:

        if value == current:
            count += 1

        else:
            groups.append((current, count))

            current = value
            count = 1

    groups.append((current, count))

    return groups


def audio_to_morse(filename):
    """
    Decode a clean Morse WAV file.

    This works best with audio generated by this program.
    """

    samples, sample_rate = read_wav(filename)

    signal = detect_signal(samples)

    groups = group_signal(signal)

    morse = ""
    current_letter = ""

    for is_tone, sample_count in groups:

        duration = sample_count / sample_rate

        # ----------------------------
        # Tone
        # ----------------------------

        if is_tone:

            if duration < 2 * UNIT:
                current_letter += "."

            else:
                current_letter += "-"

        # ----------------------------
        # Silence
        # ----------------------------

        else:

            if duration < 2 * UNIT:
                # Gap inside a Morse character
                pass

            elif duration < 5 * UNIT:

                # Letter boundary
                morse += current_letter + " "
                current_letter = ""

            else:

                # Word boundary
                morse += current_letter + " / "
                current_letter = ""

    # Add final character
    if current_letter:
        morse += current_letter

    return morse.strip()


# ============================================================
# USER INTERFACE
# ============================================================

def print_menu():

    print()
    print("=" * 50)
    print("        MORSE CODE COMMUNICATION SYSTEM")
    print("=" * 50)
    print()
    print("1. Text -> Morse")
    print("2. Morse -> Text")
    print("3. Text -> Morse WAV")
    print("4. Morse -> WAV")
    print("5. WAV -> Morse")
    print("6. WAV -> Text")
    print("7. Show Morse table")
    print("0. Exit")
    print()


def show_table():

    print()
    print("MORSE CODE TABLE")
    print("-" * 40)

    for character, code in MORSE.items():
        print(f"{character:3} {code}")

    print()


def main():

    while True:

        print_menu()

        choice = input("Select an option: ").strip()

        # ----------------------------------------------------
        # Text -> Morse
        # ----------------------------------------------------

        if choice == "1":

            text = input("Enter text: ")

            result = text_to_morse(text)

            print()
            print("Morse:")
            print(result)

        # ----------------------------------------------------
        # Morse -> Text
        # ----------------------------------------------------

        elif choice == "2":

            morse = input("Enter Morse: ")

            result = morse_to_text(morse)

            print()
            print("Text:")
            print(result)

        # ----------------------------------------------------
        # Text -> WAV
        # ----------------------------------------------------

        elif choice == "3":

            text = input("Enter text: ")

            morse = text_to_morse(text)

            print()
            print("Morse:")
            print(morse)

            filename = input(
                "Output filename [morse.wav]: "
            ).strip()

            if not filename:
                filename = "morse.wav"

            morse_to_wav(morse, filename)

        # ----------------------------------------------------
        # Morse -> WAV
        # ----------------------------------------------------

        elif choice == "4":

            morse = input("Enter Morse: ")

            filename = input(
                "Output filename [morse.wav]: "
            ).strip()

            if not filename:
                filename = "morse.wav"

            morse_to_wav(morse, filename)

        # ----------------------------------------------------
        # WAV -> Morse
        # ----------------------------------------------------

        elif choice == "5":

            filename = input("WAV filename: ").strip()

            try:

                morse = audio_to_morse(filename)

                print()
                print("Detected Morse:")
                print(morse)

            except Exception as error:

                print()
                print("Error:", error)

        # ----------------------------------------------------
        # WAV -> Text
        # ----------------------------------------------------

        elif choice == "6":

            filename = input("WAV filename: ").strip()

            try:

                morse = audio_to_morse(filename)

                text = morse_to_text(morse)

                print()
                print("Detected Morse:")
                print(morse)

                print()
                print("Decoded text:")
                print(text)

            except Exception as error:

                print()
                print("Error:", error)

        # ----------------------------------------------------
        # Table
        # ----------------------------------------------------

        elif choice == "7":

            show_table()

        # ----------------------------------------------------
        # Exit
        # ----------------------------------------------------

        elif choice == "0":

            print("Goodbye!")
            break

        else:

            print("Invalid option.")


if __name__ == "__main__":
    main()