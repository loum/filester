"""Generic, file-based utilities and helpers.

"""
import os
import re
import string
import shutil
import hashlib
import fnmatch
import fcntl
import tempfile
import time
import logging
from typing import AnyStr, IO, Iterator, Optional


def create_dir(directory: str) -> str:
    """Helper method to manage the creation of a directory.

    **Args:**
        ``directory``: the name of the directory structure to create.

    **Returns:**
        boolean ``True`` if directory exists.

        boolean ``False`` if the directory does not exist and the attempt to create it fails.

    """
    status = True

    if directory is not None:
        if not os.path.exists(directory):
            logging.info('Creating directory "%s"', directory)
            try:
                os.makedirs(directory)
            except OSError as err:
                status = False
                logging.error('Directory create error: %s', err)
    else:
        logging.error('Create directory failed - invalid name "%s"', directory)

    return status


def get_directory_files(file_path: str, file_filter: str = None):
    """Generator that returns the files in the directory given by ``file_path``.

    Does not include the special entries '.' and '..' even if they are
    present in the directory.

    If ``file_filter`` is provided, will perform a regular expression match
    against the files within ``file_path``.

    **Args:**
        ``file_path``: absolute path name to the directory

    **Kwargs:**
        ``file_filter``: :mod:`re` type pattern that can be input directly
        into the :func:`re.search` function

    **Returns:**
        each file in the directory as a generator

    """
    directory_files = []
    try:
        directory_files = os.listdir(file_path)
    except (TypeError, OSError) as err:
        logging.error('Directory listing error for %s: %s', file_path, err)

    for this_file in directory_files:
        this_file = os.path.join(file_path, this_file)
        if not os.path.isfile(this_file):
            continue

        if file_filter is None:
            yield this_file
        else:
            if fnmatch.fnmatch(os.path.basename(this_file), file_filter):
                yield this_file


def get_directory_files_list(file_path: str, file_filter: str = None) -> Iterator[Optional[str]]:
    """Wrapper around the :func:`get_directory_files` function that
    returns a list of files in the directory denoted by ``file_path``.

    """
    return list(get_directory_files(file_path, file_filter))


def move_file(source: str, target: str, dry: bool = False) -> bool:
    """Attempts to move ``source`` to ``target``.

    Checks if the ``target`` directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        ``source``: name of file to move

        ``target``: filename of where to move ``source`` to

    **Kwargs:**
        ``dry``: only report, do not execute (but will create the target
        directory if it is missing)

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    logging.info('Moving "%s" to "%s"', source, target)
    status = True

    if not os.path.exists(source):
        logging.warning('Source file "%s" does not exist', str(source))
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
                logging.error('%s move to %s failed: "%s"',
                          source, target, error)

    return status


def copy_file(source: str, target: str) -> bool:
    """Attempts to copy ``source`` to ``target``.

    Guarantees an atomic copy.  In other word, ``target`` will not present
    on the filesystem until the copy is complete.

    Checks if the ``target`` directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        ``source``: name of file to move

        ``target``: filename of where to copy ``source`` to

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    logging.info('Copying "%s" to "%s"', source, target)
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
                logging.error('%s copy to %s failed: "%s"', source, target, err)
    else:
        logging.warning('Source file "%s" does not exist', str(source))

    return status


def remove_files(files: Iterator[str]) -> Iterator[Optional[str]]:
    """Attempts to remove ``files``.

    **Args:**
        ``files``: either a list of file to remove or a single filename.
        string

    **Returns:**
        list of files successfully removed from filesystem

    """
    if not isinstance(files, list):
        files = [files]

    files_removed = []
    for file_to_remove in files:
        try:
            logging.info('Removing file "%s"', file_to_remove)
            os.remove(file_to_remove)
            files_removed.append(file_to_remove)
        except OSError as err:
            logging.error('"%s" remove failed: %s', file_to_remove, err)

    return files_removed


def check_filename(filename: str, re_format: str) -> bool:
    """Parse filename string supplied by ``file`` and check that it
    conforms to ``re_format``.

    **Args:**
        ``filename``: the filename string

        ``re_format``: the :mod:`re` format string to match against

    **Returns:**
        boolean ``True`` if filename string conforms to ``re_format``

        boolean ``False`` otherwise

    """
    status = False

    reg_c = re.compile(re_format)
    reg_match = reg_c.match(os.path.basename(filename))
    if reg_match:
        status = True
        logging.debug('File "%s" matches filter "%s"', filename, re_format)
    else:
        logging.debug('File "%s" did not match filter "%s"', filename, re_format)

    return status


def gen_digest(value: str, digest_len: int = 8) -> str:
    """Generates a 64-bit checksum against ``value``

    .. note::

        The digest is actually the first 8-bytes of the
        :func:`hashlib.hexdigest` function.

    **Args:**
        ``value``: the string value to generate digest against

    **Returns:**
        8 byte digest containing only hexadecimal digits

    """
    digest = None

    if value is not None and isinstance(value, str):
        md5 = hashlib.md5()
        md5.update(bytes(value, encoding='utf-8'))
        digest = md5.hexdigest()[0:digest_len]
    else:
        logging.error('Cannot generate digest against value: %s', str(value))

    return digest


def gen_digest_path(value: int, dir_depth: int = 4) -> Iterator[str]:
    """Helper function that handles the creation of digest-based
    directory path.  The digest is calculated from ``value``.
    For example, the ``value`` ``193433`` will generate the directory path list::

        ['73', '73b0', '73b0b6', '73b0b66e']

    Depth of directories created can be controlled by ``dir_depth``.

    **Args:**
        ``value``: the string value to generate digest against

    **Kwargs:**
        ``dir_depth``: number of directory levels (default 4).  For example,
        depth of 2 would produce::

            ['73', 73b0']

    **Returns:**
        list of 8-byte segments that constitite the original 32-byte digest

    """
    digest = gen_digest(value)

    dirs = []
    if digest is not None:
        dirs = [digest[0:2 + (i * 2)] for i in range(0, dir_depth)]

    return dirs


def templater(template_file: str, **kwargs) -> str:
    """Attemptes to parse ``template`` file and substitute template
    parameters with ``kwargs`` construct.

    **Args**:
        ``template_file``: full path to the template file

        ``kwargs``: dictionary structure of items to expected by the HTML email templates::

            {
                'name': 'Anywhere',
                'address': '1234 Anywhere Road',
                'suburb': 'ANYWHERE',
                'postcode': '9999',
                'barcode': '0123456789-barcode',
                'item_nbr': '0123456789-item_nbr'
            }

    **Returns**:
        string representation of the template with parameters substition
        or ``None`` if the process fails

    **Raises**:
        ``IOError`` if the template_file cannot be opened

        ``KeyError`` if the template substitution fails

    """
    logging.debug('Processing template: "%s"', template_file)

    template_src = None
    try:
        with open(template_file, encoding='utf-8') as _fh:
            template_src = _fh.read()
    except IOError as err:
        logging.error('Unable to source template file "%s": %s', template_file, err)

    template_sub = None
    if template_src is not None:
        template = string.Template(template_src)
        try:
            template_sub = template.substitute(kwargs)
        except KeyError as err:
            logging.error('Template "%s" substitute failed: %s',
                      template_file, err)

    if template_sub is not None:
        template_sub = template_sub.rstrip('\n')

    logging.debug('Template substitution (%s|%s) produced: "%s"',
              template_file, str(kwargs), template_sub)

    return template_sub


def lock_file(file_to_lock: str) -> IO[AnyStr]:
    """Creates a file descriptor for read/write against ``file_to_lock``
    and produces an exclusive lock against the file descriptor.

    **Args:**
        ``file_to_lock``: path to the file to lock.  File must exist before
        the lock is set (simulates a read lock).

    **Returns:**
        File descriptor as represented by the :class:`file` object
        to the ``file_to_lock`` if lock is successful.  ``None`` otherwise

    """
    file_desc = None
    if not os.path.exists(file_to_lock):
        logging.warning('File to lock "%s" does not exist', file_to_lock)
    else:
        file_desc = open(file_to_lock, 'r+', encoding='utf-8') # pylint: disable=consider-using-with
        try:
            fcntl.lockf(file_desc, fcntl.LOCK_EX|fcntl.LOCK_NB)
            logging.debug('Obtained exclusive lock on file "%s"', file_desc.name)
        except IOError as err:
            file_desc.close()
            file_desc = None
            logging.error('Exclusive lock on file "%s" failed: %s', file_desc.name, err)

    return file_desc


def unlock_file(file_desc: IO[AnyStr]) -> IO[AnyStr]:
    """Release file lock on ``file_desc``.

    """
    logging.debug('Releasing lock on file "%s"', file_desc.name)
    fcntl.lockf(file_desc, fcntl.LOCK_UN)
    file_desc.close()


def get_file_time_in_utc(filename: str) -> str:
    """Will attempt to read ``filename`` modified time stamp and return
    a RFC 3339-compliant string in UTC.

    If time can not be obtained then ``None`` is returned

    """
    utc_time_str = None

    if os.path.isfile(filename):
        sec_since_epoch = os.stat(filename)[8]
        utc_time_str = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                     time.gmtime(sec_since_epoch))

    return utc_time_str
