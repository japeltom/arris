import copy, os, pytz
from datetime import datetime
from subprocess import Popen, PIPE

from exceptions import EXIFReadError, EXIFWriteError, XMPReadError, XMPWriteError

def get_empty_picture_data():
    d = dict(
        author=None,
        date_time=None,
        city=None,
        country=None,
        title=None,
        description=None,
        tags=None,
    )

    return d

def load_xmp_from_file(file_name, default_time_zone=None, ignore_errors=False):
    """Loads XMP metadata entries from the given file. If flag ignore_errors is
    true, then attempt to fetch the metadata even in presence of some errors
    from the exiv2 tool."""

    if not os.path.exists(file_name):
        raise IOError(f"File '{file_name}' does not exist.")

    data = get_empty_picture_data()

    result = Popen(["exiv2", "-px", "pr", file_name], stdout=PIPE, stderr=PIPE).communicate()
    if len(result[1]) > 0 and not ignore_errors:
        raise XMPReadError(file_name, result[1].decode("utf-8"))

    has_language = ["dc.title", "dc.description"]
    for line in result[0].splitlines():
        line = line.decode("utf-8")
        pieces = line.split()

        tag_name = pieces[0][4:]
        value = pieces[3:] if tag_name not in has_language else pieces[4:]
        value = " ".join(value)

        if tag_name == "dc.creator":
            k = "author"
        elif tag_name == "dc.date":
            k = "date_time"
            value = datetime.fromisoformat(value)
            # It is possible that the UTC offset is now None, so we set it to
            # the default.
            if value.utcoffset() is None and default_time_zone is not None:
                value = pytz.timezone(default_time_zone).localize(value)
        elif tag_name == "iptcExt.City":
            k = "city"
        elif tag_name == "iptcExt.CountryName":
            k = "country"
        elif tag_name == "dc.title":
            k = "title"
        elif tag_name == "dc.description":
            k = "description"
        elif tag_name == "dc.subject":
            k = "tags"
            value = [x.strip() for x in value.split(",")]
        else:
            continue

        data[k] = value

    return data

def write_xmp_to_file(file_name, metadata, language, ignore_errors=False):
    """Writes the metadata entries as XMP tags tothe given file."""

    entries = {
        "language": {
            "tag":      ("dc", "language"),
            "type":     "sequence",
        },
        "author": {
            "tag":      ("dc", "creator"),
            "type":     "sequence",
        },
        "date_time": {
            "tag":      ("dc", "date"),
            "type":     "value",
            "callback": lambda dt: dt.isoformat(),
        },
        "city": {
            "tag":      ("iptcExt", "City"),
            "type":     "value",
        },
        "country": {
            "tag":      ("iptcExt", "CountryName"),
            "type":     "value",
        },
        "title": {
            "tag":      ("dc", "title"),
            "language": True,
            "type":     "bag",
        },
        "description": {
            "tag":      ("dc", "description"),
            "language": True,
            "type":     "bag",
        },
        "tags": {
            "tag":      ("dc", "subject"),
            "type":     "bag",
        },
    }

    # We edit the metadata entries to be lists of values for convenience below.
    metadata = copy.deepcopy(metadata)
    for entry in metadata:
        if entry == "tags": continue
        metadata[entry] = [metadata[entry]] if metadata[entry] is not None else None
    metadata["language"] = [language]

    if not os.path.exists(file_name):
        raise IOError(f"File '{file_name}' does not exist.")

    # Prepare XMP tag setup.
    # We avoid writing the language tag if it is not needed.
    calls = []
    language_add = False
    for entry in entries:
        if entry not in metadata: continue
        if entry == "language": continue

        tag_name = "Xmp." + ".".join(entries[entry]["tag"])
        # Delete the tag first.
        calls.append(f"del {tag_name}")

        # Only then set the values (if not None).
        if metadata[entry] is None: continue
        for value in metadata[entry]:
            tag_value = entries[entry]["callback"](value) if "callback" in entries[entry] else value
            if entries[entry]["type"] == "bag" and ("language" in entries[entry] and entries[entry]["language"]):
                param = f"set {tag_name} lang={language} {tag_value}"
                language_add = False
            else:
                param = f"set {tag_name} {tag_value}"
            calls.append(param)

    # The language tag is always removed.
    entry = "language"
    tag_name = "Xmp." + ".".join(entries[entry]["tag"])
    calls.append(f"del {tag_name}")
    if language_add:
        value = metadata[entry][0]
        tag_value = entries[entry]["callback"](value) if "callback" in entries[entry] else value
        param = f"set {tag_name} {tag_value}"
        calls.append(param)

    # Remove all XMP data from the file.
    #Popen(["exiv2", "-k", "-dx", "rm", file_name], stdout=PIPE, stderr=PIPE).communicate()

    # Prepare the call for adding the metadata.
    call = ["exiv2", "-k"]
    for c in calls:
        call.append("-M")
        call.append(c)
    call.append(file_name)

    # Perform the call.
    result = Popen(call, stdout=PIPE, stderr=PIPE).communicate()
    if len(result[1]) > 0 and not ignore_errors:
        raise XMPWriteError(file_name, result[1].decode("utf-8"))

def load_exif_from_file(file_name, tags, ignore_errors=False):
    """Load the specified EXIF tags from the specified file. The output is a
    dictionary with the tags as keys and the corresponding values as strings.
    If a specified tag is not a key, then the EXIF tag does not exist."""

    tags = [t.lower() for t in tags]

    if not os.path.exists(file_name):
        raise IOError(f"File '{file_name}' does not exist.")

    result = Popen(["exiv2", "-pe", "pr", file_name], stdout=PIPE, stderr=PIPE).communicate()
    if len(result[1]) > 0 and not ignore_errors:
        raise EXIFReadError(file_name, result[1].decode("utf-8"))

    out = {}
    for line in result[0].splitlines():
        line = line.decode("utf-8")
        pcs = line.split(" ")
        parts = []
        i = -1
        for i, p in enumerate(pcs):
            if len(p) > 0:
                parts.append(p)
            if len(parts) >= 3: break

        parts.append(" ".join(pcs[i+1:])[1:])

        if parts[0].lower() in tags:
            out[parts[0]] = parts[-1]

    return out

def write_exif_to_file(file_name, tags):
    """Sets the EXIF tags of the specified file according to the given
    dictionary (tag-value pairs)."""

    if not os.path.exists(file_name):
        raise IOError(f"File '{file_name}' does not exist.")

    # Prepare the EXIF tag setup.
    call = ["exiv2", "-k"]
    for tag, value in tags.items():
        call.append("-M")
        if value is not None:
            param = f"set {tag} {value}"
        else:
            param = f"del {tag}"
        call.append(param)
    call.append(file_name)

    # Perform the call.
    result = Popen(call, stdout=PIPE, stderr=PIPE).communicate()
    if len(result[1]) > 0:
        raise EXIFWriteError(file_name, result[1].decode("utf-8"))

def exif_timestamp_to_datetime(timestamp, time_zone=None):
    """Converts an EXIF timestamp of the format 'YYYY:MM:DD HH:MM:SS' to a
    datetime object. Since an EXIF timestamp does not contain timezone
    information, the specified timezone is used (default is None, which is
    treated as UTC+0)."""

    timestamp = timestamp.strip()
    try:
        hour = int(timestamp[11:13])
        if hour == 24: hour = 0
        dt = datetime(
            year=int(timestamp[:4]),
            month=int(timestamp[5:7]),
            day=int(timestamp[8:10]),
            hour=hour,
            minute=int(timestamp[14:16]),
            second=int(timestamp[17:19]),
        )
    except IndexError as exc:
        raise ValueError(f"Invalid EXIF timestamp format '{timestamp}'.") from exc

    if time_zone is not None:
        dt = pytz.timezone(time_zone).localize(dt)

    return dt

