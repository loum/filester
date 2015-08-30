"""Generic file-based utilities and helpers.

"""
__all__ = [
    'create_dir',
    'get_directory_files',
    'get_directory_files_list',
    'remove_files',
    'move_file',
    'copy_file',
    'check_filename',
    'gen_digest',
    'gen_digest_path',
    'lock_file',
    'get_file_time_in_utc',
]
import os
import re
import string
import shutil
import hashlib
import fcntl
import tempfile
import time

from logga.log import log


def create_dir(directory):
    """Helper method to manage the creation of a directory.

    **Args:**
        directory: the name of the directory structure to create.

    **Returns:**
        boolean ``True`` if directory exists.

        boolean ``False`` if the directory does not exist and the
        attempt to create it fails.

    """
    status = True

    if directory is not None:
        if not os.path.exists(directory):
            log.info('Creating directory "%s"', directory)
            try:
                os.makedirs(directory)
            except OSError, err:
                status = False
                log.error('Directory create error: %s', err)
    else:
        log.error('Create directory failed - invalid name "%s"', directory)

    return status


def get_directory_files(path, file_filter=None):
    """Generator that returns the files in the directory given by *path*.

    Does not include the special entries '.' and '..' even if they are
    present in the directory.

    If *file_filter* is provided, will perform a regular expression match
    against the files within *path*.

    **Args:**
        *path*: absolute path name to the directory

    **Kwargs:**
        *file_filter*: :mod:`re` type pattern that can be input directly
        into the :func:`re.search` function

    **Returns:**
        each file in the directory as a generator

    """
    directory_files = []
    try:
        directory_files = os.listdir(path)
    except (TypeError, OSError), err:
        log.error('Directory listing error for %s: %s', path, err)

    for this_file in directory_files:
        this_file = os.path.join(path, this_file)
        if not os.path.isfile(this_file):
            continue

        if file_filter is None:
            yield this_file
        else:
            reg_c = re.compile(file_filter)
            reg_match = reg_c.match(os.path.basename(this_file))
            if reg_match:
                yield this_file


def get_directory_files_list(path, file_filter=None):
    """Wrapper around the :func:`get_directory_files` function that
    returns a list of files in the directory denoted by *path*.

    """
    return list(get_directory_files(path, file_filter))


def move_file(source, target, dry=False):
    """Attempts to move *source* to *target*.

    Checks if the *target* directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        *source*: name of file to move

        *target*: filename of where to move *source* to

    **Kwargs:**
        *dry*: only report, do not execute (but will create the target
        directory if it is missing)

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    log.info('Moving "%s" to "%s"', source, target)
    status = True

    if not os.path.exists(source):
        log.warn('Source file "%s" does not exist', str(source))
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
                log.error('%s move to %s failed: "%s"',
                          source, target, error)

    return status


def copy_file(source, target):
    """Attempts to copy *source* to *target*.

    Guarantees an atomic copy.  In other word, *target* will not present
    on the filesystem until the copy is complete.

    Checks if the *target* directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        *source*: name of file to move

        *target*: filename of where to copy *source* to

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    log.info('Copying "%s" to "%s"', source, target)
    status = False

    if os.path.exists(source):
        if create_dir(os.path.dirname(target)):
            try:
                tmp_dir = os.path.dirname(target)
                tmp_target_fh = tempfile.NamedTemporaryFile(dir=tmp_dir)
                tmp_target = tmp_target_fh.name
                tmp_target_fh.close()
                shutil.copyfile(source, tmp_target)
                os.rename(tmp_target, target)
                status = True
            except (OSError, IOError), err:
                log.error('%s copy to %s failed: "%s"',
                          source, target, err)
    else:
        log.warn('Source file "%s" does not exist', str(source))

    return status


def remove_files(files):
    """Attempts to remove *files*

    **Args:**
        *files*: either a list of file to remove or a single filename
        string

    **Returns:**
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
        except OSError, err:
            log.error('"%s" remove failed: %s', file_to_remove, err)

    return files_removed


def check_filename(filename, re_format):
    """Parse filename string supplied by *file* and check that it
    conforms to *re_format*.

    **Args:**
        *filename*: the filename string

        *re_format*: the :mod:`re` format string to match against

    **Returns:**
        boolean ``True`` if filename string conforms to *re_format*

        boolean ``False`` otherwise

    """
    status = False

    reg_c = re.compile(re_format)
    reg_match = reg_c.match(os.path.basename(filename))
    if reg_match:
        status = True
        log.debug('File "%s" matches filter "%s"', filename, re_format)
    else:
        log.debug('File "%s" did not match filter "%s"',
                  filename, re_format)

    return status


def gen_digest(value):
    """Generates a 64-bit checksum against *str*

    .. note::

        The digest is actually the first 8-bytes of the
        :func:`hashlib.hexdigest` function.

    **Args:**
        *value*: the string value to generate digest against

    **Returns:**
        8 byte digest containing only hexadecimal digits

    """
    digest = None

    if value is not None and isinstance(value, basestring):
        md5 = hashlib.md5()
        md5.update(value)
        digest = md5.hexdigest()[0:8]
    else:
        log.error('Cannot generate digest against value: %s', str(value))

    return digest


def gen_digest_path(value):
    """Helper function that handles the creation of digest-based
    directory path.  The digest is calculated from *value*.

    For example, the *value* ``193433`` will generate the directory path
    list::

        ['73', '73b0', '73b0b6', '73b0b66e']

    **Args:**
        *value*: the string value to generate digest against

    **Returns:**
        list of 8-byte segments that constitite the original 32-byte
        digest

    """
    digest = gen_digest(value)

    dirs = []
    if digest is not None:
        num = 2
        dirs = [digest[0:2 + (i * 2)] for i in range(0,
                                                     len(digest) / num)]

    return dirs


def templater(template_file, **kwargs):
    """Attemptes to parse *template* file and substitute template
    parameters with *kwargs* construct.

    **Args**:
        *template_file*: full path to the template file

        *kwargs*: dictionary structure of items to expected by the HTML
         email templates::

            {'name': 'Auburn Newsagency',
             'address': '119 Auburn Road',
             'suburb': 'HAWTHORN EAST',
             'postcode': '3123',
             'barcode': '218501217863-barcode',
             'item_nbr': '3456789012-item_nbr'}

    **Returns**:
        string representation of the template with parameters substition
        or ``None`` if the process fails

    **Raises**:
        ``IOError`` if the template_file cannot be opened

        ``KeyError`` if the template substitution fails

    """
    log.debug('Processing template: "%s"', template_file)

    template_src = None
    try:
        file_h = open(template_file)
        template_src = file_h.read()
        file_h.close()
    except IOError, err:
        log.error('Unable to source template file "%s"', template_file)

    template_sub = None
    if template_src is not None:
        template = string.Template(template_src)
        try:
            template_sub = template.substitute(kwargs)
        except KeyError as err:
            log.error('Template "%s" substitute failed: %s',
                      template_file, err)

    if template_sub is not None:
        template_sub = template_sub.rstrip('\n')

    log.debug('Template substitution (%s|%s) produced: "%s"',
              template_file, str(kwargs), template_sub)

    return template_sub


def lock_file(file_to_lock):
    """Creates a file descriptor for read/write against *file_to_lock*
    and produces an exclusive lock against the file descriptor.

    **Args:**
        *file_to_lock*: path to the file to lock.  File must exist before
        the lock is set (simulates a read lock).

    **Returns:**
        File descriptor as represented by the :class:`file` object
        to the *file_to_lock* if lock is successful.  ``None`` otherwise

    """
    file_desc = None
    if not os.path.exists(file_to_lock):
        log.warn('File to lock "%s" does not exist', file_to_lock)
    else:
        file_desc = open(file_to_lock, 'r+')
        try:
            fcntl.lockf(file_desc, fcntl.LOCK_EX|fcntl.LOCK_NB)
            log.debug('Obtained exclusive lock on file "%s"',
                      file_desc.name)
        except IOError:
            file_desc.close()
            file_desc = None
            log.warn('Unable to obtain exclusive lock on file "%s"',
                     file_desc.name)

    return file_desc


def unlock_file(file_desc):
    """Release file lock on *file_desc*.

    """
    log.debug('Releasing lock on file "%s"', file_desc.name)
    fcntl.lockf(file_desc, fcntl.LOCK_UN)
    file_desc.close()


def get_file_time_in_utc(filename):
    """Will attempt to read *filename* modified time stamp and return
    a RFC 3339-compliant string in UTC.

    If time can not be obtained then ``None`` is returned

    """
    utc_time_str = None

    if os.path.isfile(filename):
        sec_since_epoch = os.stat(filename)[8]
        utc_time_str = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                                     time.gmtime(sec_since_epoch))

    return utc_time_str
