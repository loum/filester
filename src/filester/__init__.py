"""Generic, file-based utilities and helpers.

"""
from typing import AnyStr, Iterator, Optional, Union
import fcntl
import fnmatch
import hashlib
import io
import os
import re
import shutil
import string
import tempfile
import time

from logga import log


def create_dir(directory: str) -> bool:
    """Helper method to manage the creation of a directory.

    Parameters:
        directory: Name of the directory structure to create.

    Returns:
        Boolean `True` if directory is created or already exists. Boolean `False` otherwise.

    """
    status = True

    if directory is not None:
        if not os.path.exists(directory):
            log.info('Creating directory "%s"', directory)
            try:
                os.makedirs(directory)
            except OSError as err:
                status = False
                log.error("Directory create error: %s", err)
    else:
        log.error('Create directory failed - invalid name "%s"', directory)

    return status


def get_directory_files(
    file_path: str, file_filter: Optional[str] = None
) -> Iterator[str]:
    """Generator that returns the files in the directory given by `file_path`.

    Does not include the special entries `.` and `..` even if they are
    present in the directory.

    If `file_filter` is provided, will perform a regular expression match
    against the files within `file_path`.

    Parameters:
        file_path: Absolute path name to the directory.
        file_filter: Regular expression type pattern that can be input directly
            into the `re.search` function

    Returns:
        Each file in the directory as a generator object.

    """
    directory_files = []
    try:
        directory_files = os.listdir(file_path)
    except (TypeError, OSError) as err:
        log.error("Directory listing error for %s: %s", file_path, err)

    for this_file in directory_files:
        this_file = os.path.join(file_path, this_file)
        if not os.path.isfile(this_file):
            continue

        if file_filter is None:
            yield this_file
        else:
            if fnmatch.fnmatch(os.path.basename(this_file), file_filter):
                yield this_file


def get_directory_files_list(
    file_path: str, file_filter: Optional[str] = None
) -> list[Optional[str]]:
    """Wrapper around the `get_directory_files` function that
    returns a list of files in the directory denoted by `file_path`.

    """
    return list(get_directory_files(file_path, file_filter))


def move_file(source: str, target: str, dry: bool = False) -> bool:
    """Attempts to move `source` to `target`.

    Checks if the `target` directory exists.  If not, will attempt to
    create before attempting the file move.

    Parameters:
        source: Name of file to move.
        target: Name of file where to move `source` to.
        dry: Only report, do not execute (but will create the target directory if it is missing).

    Returns:
        Boolean `True` if move was successful. Otherwise boolean `False`.

    """
    log.info('Moving "%s" to "%s"', source, target)
    status = True

    if not os.path.exists(source):
        log.warning('Source file "%s" does not exist', str(source))
        status = False
    else:
        dir_status = True
        directory = os.path.dirname(target)
        if len(directory):
            dir_status = create_dir(directory)

        if not dry and dir_status:
            try:
                os.rename(source, target)
            except OSError as error:
                status = False
                log.error('%s move to %s failed: "%s"', source, target, error)

    return status


def copy_file(source: str, target: str) -> bool:
    """Attempts to copy `source` to `target`.

    Guarantees an atomic copy.  In other word, `target` will not present
    on the filesystem until the copy is complete.

    Checks if the `target` directory exists.  If not, will attempt to
    create before attempting the file move.

    Parameters:
        source: Name of file to move.
        target: Name of file where to move `source` to.

    Returns:
        Boolean `True` if move was successful. Otherwise `False`.

    """
    log.info('Copying "%s" to "%s"', source, target)
    status = False

    if os.path.exists(source):
        if create_dir(os.path.dirname(target)):
            try:
                tmp_dir = os.path.dirname(target)
                with tempfile.NamedTemporaryFile(dir=tmp_dir) as _fh:
                    tmp_target = _fh.name
                    _fh.close()
                    shutil.copyfile(source, tmp_target)
                    os.rename(tmp_target, target)
                    status = True
            except (OSError, IOError) as err:
                log.error('%s copy to %s failed: "%s"', source, target, err)
    else:
        log.warning('Source file "%s" does not exist', str(source))

    return status


def remove_files(files: Union[str, list[str]]) -> list[str]:
    """Attempts to remove `files`.

    Parameters:
        files: Either a list of files to remove or a single filename.

    Returns:
        list of files successfully removed from filesystem

    """
    if not isinstance(files, list):
        files = [files]

    files_removed = []
    for file_to_remove in files:
        try:
            log.info('Removing file "%s"', file_to_remove)
            os.remove(file_to_remove)
            files_removed.append(file_to_remove)
        except OSError as err:
            log.error('"%s" remove failed: %s', file_to_remove, err)

    return files_removed


def check_filename(filename: str, re_format: str) -> bool:
    """Parse filename string supplied by `file` and check that it conforms to `re_format`.

    Parameters:
        filename: The filename string.
        re_format: The regular expression format string to match against.

    Returns:
        Boolean `True` if filename string conforms to `re_format`. Otherwise `False`.

    """
    status = False

    reg_c = re.compile(re_format)
    reg_match = reg_c.match(os.path.basename(filename))
    if reg_match:
        status = True
        log.debug('File "%s" matches filter "%s"', filename, re_format)
    else:
        log.debug('File "%s" did not match filter "%s"', filename, re_format)

    return status


def gen_digest(value: Optional[Union[str, int]], digest_len: int = 8) -> Optional[str]:
    """Generates a 64-bit checksum against `value`.

    The digest is the first 8-bytes of the `hashlib.hexdigest` function.

    Parameters:
        value: The string value to generate digest against.

    Returns:
        An 8 byte digest containing only hexadecimal digits.

    """
    digest = None

    if value is not None and isinstance(value, str):
        md5 = hashlib.md5()
        md5.update(bytes(value, encoding="utf-8"))
        digest = md5.hexdigest()[0:digest_len]
    else:
        log.error("Cannot generate digest against value: %s", str(value))

    return digest


def gen_digest_path(value: str, dir_depth: int = 4) -> list[str]:
    """Helper function that handles the creation of digest-based
    directory path.  The digest is calculated from `value`.
    For example, the `value` `193433` will generate the directory path list:
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
    """Attemptes to parse `template` file and substitute template parameters
    with `kwargs` construct.

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
    except IOError as err:
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
    """Will attempt to read `filename` modified time stamp and return
    a RFC 3339-compliant string in UTC.

    If time can not be obtained then `None` is returned

    """
    utc_time_str = None

    if os.path.isfile(filename):
        sec_since_epoch = os.stat(filename)[8]
        utc_time_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(sec_since_epoch))

    return utc_time_str
