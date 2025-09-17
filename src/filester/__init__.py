"""Generic, file-based utilities and helpers."""

import fnmatch
import hashlib
import re
import shutil
import string
import tempfile
import time
from pathlib import Path
from typing import Iterator, Optional, Union

from filester.logging_config import log


def create_dir(directory: str | None) -> bool:
    """Create directory given by `directory`.

    Parameters:
        directory: Name of the directory structure to create.

    Returns:
        Boolean `True` if directory is created or already exists. Boolean `False` otherwise.

    """
    status = True

    if directory is not None:
        path = Path(directory)
        if not path.exists():
            log.info('Creating directory "%s"', directory)
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as err:
                status = False
                log.error("Directory create error: %s", err)
    else:
        status = False
        log.error('Create directory failed - invalid name "%s"', directory)

    return status


def get_directory_files(
    file_path: str, file_filter: Optional[str] = None
) -> Iterator[str]:
    """Get files in the directory given by `file_path`.

    Does not include the special entries `.` and `..` even if they are
    present in the directory.

    If `file_filter` is provided, will perform a shell-style pattern match
    (e.g., '*.txt') against the filenames. Uses `fnmatch` for compatibility.

    Parameters:
        file_path: Absolute path name to the directory.
        file_filter: Shell-style pattern (e.g., '*.log') to filter files.
                     If None, all files are returned.

    Returns:
        Each file in the directory as a generator object (yielding full paths as strings).

    """
    path = Path(file_path)

    if not path.exists():
        log.error("Directory does not exist: %s", file_path)
        return
    if not path.is_dir():
        log.error("Path is not a directory: %s", file_path)
        return

    try:
        for item in path.iterdir():
            if not item.is_file():
                continue
            if file_filter is None or fnmatch.fnmatch(item.name, file_filter):
                yield str(item)
    except (OSError, PermissionError) as err:
        log.error("Directory listing error for %s: %s", file_path, err)


def get_directory_files_list(
    file_path: str, file_filter: Optional[str] = None
) -> list[Optional[str]]:
    """Get a list of files in the directory denoted by `file_path`.

    Parameters:
        file_path: Absolute path name to the directory.
        file_filter: Regular expression type pattern that can be input directly
            into the `re.search` function

    Returns:
        List of files in the directory.

    """
    return list(get_directory_files(file_path, file_filter))


def move_file(source: str, target: str, dry: bool = False) -> bool:
    """Move `source` to `target`.

    Checks if the `target` directory exists. If not, will attempt to
    create it before attempting the file move.

    Parameters:
        source: Name of file to move.
        target: Name of file where to move `source` to.
        dry: Only report, do not execute (but will create the target directory if missing).

    Returns:
        Boolean `True` if move was successful. Otherwise boolean `False`.

    """
    source_path = Path(source)
    target_path = Path(target)

    log.info('Moving "%s" to "%s"', source, target)
    status = True

    if not source_path.exists():
        log.warning('Source file "%s" does not exist', source)
        return False

    # Ensure target directory exists
    target_dir = target_path.parent
    dir_status = True
    if target_dir:  # Check if parent directory is non-empty (i.e., not root)
        dir_status = create_dir(str(target_dir))  # Reuse your create_dir function

    if not dry and dir_status:
        try:
            source_path.rename(target_path)
        except OSError as error:
            status = False
            log.error('%s move to %s failed: "%s"', source, target, error)

    return status


def copy_file(source: str, target: str) -> bool:
    """Copy `source` to `target`.

    Guarantees an atomic copy. In other words, `target` will not appear
    on the filesystem until the copy is complete.

    Checks if the `target` directory exists. If not, will attempt to
    create it before copying.

    Parameters:
        source: Name of file to copy.
        target: Name of file where to copy `source` to.

    Returns:
        Boolean `True` if copy was successful. Otherwise `False`.

    """
    source_path = Path(source)
    target_path = Path(target)
    log.info('Copying "%s" to "%s"', source, target)
    status = False

    if not source_path.exists():
        log.warning('Source file "%s" does not exist', source)
        return False

    # Ensure target directory exists
    target_dir = target_path.parent
    if target_dir and not create_dir(str(target_dir)):
        return False  # create_dir logs its own error

    try:
        # Create temporary file in the same directory for atomic move
        with tempfile.NamedTemporaryFile(dir=str(target_dir), delete=True) as tmp_fh:
            tmp_target = Path(tmp_fh.name)
            tmp_fh.close()

        # Copy data to temporary file
        shutil.copyfile(str(source_path), str(tmp_target))

        # Atomically move temporary file to final destination
        tmp_target.rename(target_path)
        status = True
    except Exception as err:
        log.error("Unexpected error during copy: %s", err)
        status = False

    return status


def remove_files(files: Union[str, list[str]]) -> list[str]:
    """Remove `files`.

    Parameters:
        files: Either a list of files to remove or a single filename.

    Returns:
        List of files successfully removed from the filesystem.
    """
    file_list = [files] if isinstance(files, str) else files

    files_removed = []
    for file_to_remove in file_list:
        file_path = Path(file_to_remove)
        try:
            log.info('Removing file "%s"', file_to_remove)
            file_path.unlink()
            files_removed.append(file_to_remove)
        except OSError as err:
            log.error('"%s" remove failed: %s', file_to_remove, err)
        except Exception as err:
            log.error('Unexpected error removing "%s": %s', file_to_remove, err)

    return files_removed


def check_filename(filename: str, re_format: str) -> bool:
    """Parse filename string supplied by `file` and check that it conforms to `re_format`.

    Parameters:
        filename: The filename string.
        re_format: The regular expression format string to match against.

    Returns:
        Boolean `True` if filename string conforms to `re_format`. Otherwise `False`.
    """
    basename = Path(filename).name

    try:
        reg_c = re.compile(re_format)
        reg_match = reg_c.match(basename)
    except re.error as err:
        log.error('Invalid regular expression "%s": %s', re_format, err)
        return False

    if reg_match:
        log.debug('File "%s" matches filter "%s"', filename, re_format)
        return True
    else:
        log.debug('File "%s" did not match filter "%s"', filename, re_format)
        return False


def gen_digest(value: Optional[Union[str, int]], digest_len: int = 8) -> Optional[str]:
    """Create a checksum against `value` using a secure hash function.

    The digest is the first `digest_len` hexadecimal digits of the `hashlib.hexdigest` function.

    Parameters:
        value: The string value to generate digest against.

    Returns:
        An 8 byte digest containing only hexadecimal digits.

    """
    digest = None

    if value is not None and isinstance(value, str):
        md5 = hashlib.md5(usedforsecurity=False)
        md5.update(bytes(value, encoding="utf-8"))
        digest = md5.hexdigest()[0:digest_len]
    else:
        log.error("Cannot generate digest against value: %s", str(value))

    return digest


def gen_digest_path(value: str, dir_depth: int = 4) -> list[str]:
    """Manage the creation of digest-based directory path.

    The digest is calculated from `value`. For example, the `value` `193433` will generate the
    directory path list:

        ```
        ['73', '73b0', '73b0b6', '73b0b66e']
        ```

    Depth of directories created can be controlled by `dir_depth`.

    Parameters:
        value: The string value to generate digest against.
        dir_depth: number of directory levels (default 4).  For example,
            depth of 2 would produce:

                ```
                ['73', 73b0']
                ```

    Returns:
        list of 8-byte segments that constitite the original 32-byte digest.

    """
    digest = gen_digest(value)

    dirs = []
    if digest is not None:
        dirs = [digest[0 : 2 + (i * 2)] for i in range(0, dir_depth)]

    return dirs


def templater(template_file: str, **kwargs: dict) -> Optional[str]:
    """Parse `template` file and substitute template parameters with `kwargs` construct.

    Parameters:
        template_file: Fully qualified path to the template file.
        kwargs: Dictionary structure of items to expected by the HTML email templates:
            ```
            {
                "name": "Anywhere",
                "address": "1234 Anywhere Road",
                "suburb": "ANYWHERE",
                "postcode": "9999",
                "barcode": "0123456789-barcode",
                "item_nbr": "0123456789-item_nbr",
            }
            ```

    Returns:
        String representation of the template with parameters substition
            or `None` if the process fails.

    Raises:
        IOError: If the template_file cannot be opened.
        KeyError: if the template substitution fails

    """
    log.debug('Processing template: "%s"', template_file)

    template_src = None
    try:
        with open(template_file, encoding="utf-8") as _fh:
            template_src = _fh.read()
    except OSError as err:
        log.error('Unable to source template file "%s": %s', template_file, err)

    template_sub = None
    if template_src is not None:
        template = string.Template(template_src)
        try:
            template_sub = template.substitute(kwargs)
        except KeyError as err:
            log.error('Template "%s" substitute failed: %s', template_file, err)

    if template_sub is not None:
        template_sub = template_sub.rstrip("\n")

    log.debug(
        'Template substitution (%s|%s) produced: "%s"',
        template_file,
        str(kwargs),
        template_sub,
    )

    return template_sub


def get_file_time_in_utc(filename: str) -> Optional[str]:
    """Get the last modified time of `filename` as a RFC 3339-compliant string in UTC.

    If the file does not exist or its timestamp cannot be read for any reason, this function
    returns `None`.

    Parameters:
        filename: The name of the file to retrieve the timestamp for.

    Returns:
        The last modified time of the file in RFC 3339 format (e.g., '2025-09-16T10:30:45Z'),
        or `None` if the timestamp cannot be obtained.

    """
    file_path = Path(filename)

    try:
        if not file_path.is_file():
            return None

        # Get last modification time (in seconds since epoch)
        sec_since_epoch = file_path.stat().st_mtime

        # Convert to UTC and format as RFC 3339 (basic 'Z' suffix format)
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(sec_since_epoch))

    except (OSError, ValueError, TypeError) as err:
        # Handle cases like permission errors, invalid paths, etc.
        log.debug("Could not retrieve timestamp for '%s': %s", filename, err)
        return None
