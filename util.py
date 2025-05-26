import datetime, os, pytz, shutil, tempfile
from subprocess import Popen, PIPE

from PySide6.QtCore import Qt, QDateTime, QTimeZone
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QCompleter

import rawpy

supported_extensions = ["cr2", "jpg", "jpeg", "rw2"]

def items(list_widget):
    """Generates the items of the given list widget."""

    for i in range(list_widget.count()):
        item = list_widget.item(i)
        yield item

class DotDict(dict):
    """Allows dot notation access to dictionary attributes."""

    def __init__(self, dct):
        for key, value in dct.items():
            if isinstance(value, dict):
                value = DotDict(value)
            self[key] = value

    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, value):
        if isinstance(value, dict):
            value = DotDict(value)
        self[key] = value
    
def list_files(path, extensions=None, recursive=False, hidden=False, followlinks=True):
    """Get the files from the path that have the specified extension.
    Optionally recursively and include hidden files and follow symlinks."""

    if extensions is None:
        extensions = ["." + e for e in supported_extensions]

    result_files = []
    try:
        if recursive:
            for root, dirs, files in os.walk(path, followlinks=followlinks):
                if not hidden:
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    files = [f for f in files if not f.startswith(".")]
                for entry in files:
                    if not any(entry.lower().endswith(e) for e in extensions): continue
                    full_path = os.path.join(root, entry)
                    result_files.append(full_path)
        else:
            for entry in os.listdir(path):
                if not any(entry.lower().endswith(e) for e in extensions): continue
                full_path = os.path.join(path, entry)
                if not os.path.isfile(full_path): continue
                result_files.append(full_path)
    except PermissionError:
        # TODO: This should be handled.
        raise

    result_files.sort()
    return result_files

def load_photo(file_name):
    """Loads the pixel data from the given file and returns it as a QPixmap
    object."""

    if any(file_name.lower().endswith("." + e) for e in ["cr2", "rw2"]):
        raw = rawpy.imread(file_name)
        rgb = raw.postprocess(use_camera_wb=True)
        height, width, channels = rgb.shape
        image = QImage(rgb, width, height, channels*width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        raw.close()
    else:
        pixmap = QPixmap(file_name)

    return pixmap

def setup_separator_completer(lineEdit, word_list, separator=","):
    """Given a QLineEdit object lineEdit, set it up with with a
    case-insensitive autocompleter for the words in word_list. The completion
    begins anew as each occurrence of the given separator is encountered. This
    can be disabled by setting the separator to be empty."""

    completer = QCompleter(word_list)
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    # Uncomment this if you want the matches to match everywhere not just
    # at the prefix.
    #self.completer.setFilterMode(Qt.MatchFlag.MatchContains)

    def handleTextChanged(text, lineEdit, completer):
        """Handle the event that the text changes."""

        # Match only the prefix of the current prefix between occurrences
        # of the separator.
        found_match = False
        p = text.find(separator, lineEdit.cursorPosition())
        if p < 0: p = len(text)
        prefix = text[:p].rpartition(separator)[-1]
        if len(prefix) > 0:
            completer.setCompletionPrefix(prefix)
            if completer.currentRow() >= 0:
                found_match = True
                # We have a match, but we want to hide the popup if there
                # is a single possible match and it is exact.
                if completer.completionCount() == 1 and prefix == completer.currentCompletion():
                    found_match = False

        if found_match:
            # Display the completion popup.
            completer.complete()
        else:
            # Hide the completion popup.
            completer.popup().hide()

    def handleCompletion(text, lineEdit, completer):
        """Handle the actual completion event."""

        prefix = completer.completionPrefix()
        current_text = lineEdit.text()
        p1 = lineEdit.cursorPosition()
        p2 = current_text.find(separator, p1)
        if p2 < 0: p2 = len(current_text)
        new_text = current_text[:p2 - len(prefix)] + text
        new_pos = len(new_text)
        new_text += current_text[p2:]
        lineEdit.setText(new_text)
        lineEdit.setCursorPosition(new_pos)
        completer.popup().hide()

    completer.setWidget(lineEdit)
    if len(separator) > 0:
        # Nonempty separator.
        completer.activated.connect(lambda text: handleCompletion(text, lineEdit, completer))
        lineEdit.textChanged.connect(lambda text: handleTextChanged(text, lineEdit, completer))
    else:
        # Empty separator.
        lineEdit.setCompleter(completer)

def datetime_to_qdatetime(dt, default_utc_offset=0):
    """Convert a Python datetime object to a QDateTime object."""

    # This appears more complex than it needs to be, but it works.
    year = dt.year
    month = dt.month
    day = dt.day
    h = dt.hour
    m = dt.minute
    s = dt.second
    utc_offset = dt.utcoffset().total_seconds() if dt.tzinfo is not None else default_utc_offset

    qdt = QDateTime(year, month, day, h, m, s)
    date = qdt.date()
    time = qdt.time()
    qdt = QDateTime(date, time, QTimeZone.fromSecondsAheadOfUtc(utc_offset))
    return qdt

def qdatetime_to_datetime(qdt):
    """Convert a QDateTime datetime object to a Python datetime object."""

    date = qdt.date()
    time = qdt.time()
    tz = qdt.timeZone()
    utc_offset = tz.offsetFromUtc(qdt)
    timedelta = datetime.timedelta(seconds=utc_offset)

    dt = datetime.datetime(
        year=date.year(),
        month=date.month(),
        day=date.day(),
        hour=time.hour(),
        minute=time.minute(),
        second=time.second(),
        tzinfo=datetime.timezone(timedelta)
    )

    return dt

def rotate_image(file_name, angle):
    """Rotate the image file by the given angle (multiple of 90 degrees)."""

    # TODO: Handle errors.

    if angle == 0: return

    if angle % 90 != 0:
        raise ValueError("Rotation only by multiples of 90 degrees is supported.")

    angle %= 360

    temp_file_name = tempfile.mktemp()
    result = Popen(["jpegtran", "-copy", "all", "-rotate", str(angle), "-outfile", temp_file_name, file_name], stdout=PIPE, stderr=PIPE).communicate()

    # Check if EXIF information about the orientation exists. If it does,
    # resets it.
    result1 = Popen(["exiv2", "-pt", "pr", temp_file_name], stdout=PIPE, stderr=PIPE)
    result2 = Popen(["grep", "Exif.Image.Orientation"], stdin=result1.stdout, stdout=PIPE, stderr=PIPE)
    result1.stdout.close()
    result2.communicate()
    if result2.returncode == 0:
        result = Popen(["exiv2", "-k", "-M", "set Exif.Image.Orientation 1", temp_file_name], stdout=PIPE, stderr=PIPE).communicate()

    shutil.move(temp_file_name, file_name)

def optimize_image(file_name):
    """Optimize an image file for size. Remove embedded EXIF thumbnail data."""

    # TODO: Handle errors.

    temp_file_name = tempfile.mktemp()

    # Optimize DFT coefficients for JPG.
    extensions = ["jpg", "jpeg"]
    if any(file_name.endswith("." + e) for e in extensions):
        result = Popen(["jpegtran", "-opt", "-perfect", "-copy", "all", "-outfile", temp_file_name, file_name], stdout=PIPE, stderr=PIPE).communicate()
    else:
        shutil.copy(file_name, temp_file_name)

    # Remove thumbnail.
    result = Popen(["exiv2", "-dt", "rm", temp_file_name], stdout=PIPE, stderr=PIPE).communicate()

    shutil.move(temp_file_name, file_name)

def set_image_permissions(file_name):
    """Sets image permissions to 644."""

    result = Popen(["chmod", "644", file_name], stdout=PIPE, stderr=PIPE).communicate()

def set_image_timestamp(file_name, date_time):
    """Sets the image creation timestamp according to the given datetime
    object."""

    env = os.environ.copy()  # Make a copy of the current environment
    env["TZ"] = "UTC"

    dt = date_time.astimezone(pytz.utc)
    dt = f"{dt.year:04}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}"
    result = Popen(["touch", "-d", dt, file_name], stdout=PIPE, stderr=PIPE, env=env).communicate()

