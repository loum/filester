"""Unit tests for :module:`filer`.

"""
import os
import tempfile

import filer


def test_get_directory_files_no_directory():
    """Get directory file -- no directory.
    """
    directory = tempfile.mkdtemp()
    os.removedirs(directory)

    received = []
    for filename in filer.get_directory_files(directory):
        received.append(filename)
    msg = 'Missing directory listing error'
    assert not received, msg

    received = filer.get_directory_files_list(directory)
    assert not received, 'Missing directory listing error (list variant)'


def test_get_directory_files_no_files(working_dir):
    """Get directory file: no files.
    """
    received = []
    for filename in filer.get_directory_files(working_dir):
        received.append(filename)
    msg = 'Empty directory listing error'
    assert not received, msg

    received = filer.get_directory_files_list(working_dir)
    assert not received, 'Empty directory listing error (list variant)'


def test_get_directory_files(working_dir):
    """Get directory files.
    """
    filename = None
    with tempfile.NamedTemporaryFile(dir=working_dir, delete=False) as file_obj:
        filename = file_obj.name

    received = filer.get_directory_files_list(working_dir)
    expected = [filename]
    assert received == expected, 'Directory listing error'


def test_get_directory_files_filtered(working_dir):
    """Get directory files: filtered.
    """
    filename = None
    with tempfile.NamedTemporaryFile(dir=working_dir) as file_obj:
        filename = file_obj.name

    filter_file = 'TCD_Deliveries_20140207111019.DAT'
    with open(os.path.join(working_dir, filter_file), mode='w', encoding='utf-8') as _fh:
        _fh.close()

    file_filter = r'TCD_Deliveries_*.DAT'
    received = filer.get_directory_files_list(os.path.dirname(filename), file_filter=file_filter)
    expected = [os.path.join(working_dir, filter_file)]
    assert received == expected, 'Directory listing error'


def test_check_filename():
    """Test file name validator.
    """
    # Given a file name "T1250_TOLP_20130904061851.txt"
    filename = 'T1250_TOLP_20130904061851.txt'

    # and a matching regular expression
    re_format = r'T1250_TOL.*\.txt'

    # when the file name is validated
    received = filer.check_filename(filename, re_format)

    # then there should be a successful match
    assert received, 'File name should validate True'


def test_check_filename_that_does_not_match():
    """Test file name validator: failed match.
    """
    # Given a file name "XXX_20130904061851.txt"
    filename = 'XXX_20130904061851.txt'

    # and a unmatching regular expression
    re_format = r'T1250_TOL.*\.txt'

    # when the file name is validated
    received = filer.check_filename(filename, re_format)

    # then there should be a successful match
    assert not received, 'File name should validate False'


def test_gen_digest_undefined_value():
    """Test digest generator: undefined value.
    """
    # Given an undefined value
    value = None

    # when I attempt to generate an digest
    received = filer.gen_digest(value)

    # the digest create engine should return None
    assert not received, 'Digest generation error: None value'


def test_gen_digest_non_string_value():
    """Test digest generator: non-string value.
    """
    # Given an numeric value
    value = 1234

    # when I attempt to generate an digest
    received = filer.gen_digest(value)

    # the digest create engine should return None
    assert not received, 'Digest generation error: None value'


def test_gen_digest():
    """Test digest generate.
    """
    # Given an numeric value
    value = '193433'

    # when I attempt to generate an digest
    received = filer.gen_digest(value)

    # the digest create engine should return a new digest value
    assert received == '73b0b66e', 'Digest generation error'


def test_gen_digest_long():
    """Test digest generate: long digest.
    """
    # Given an numeric value
    value = '193433'

    # and a digest length
    digest_length = 16

    # when I attempt to generate an digest
    received = filer.gen_digest(value, digest_len=digest_length)

    # then the digest create engine should return a new digest value
    assert received == '73b0b66e5dfe3567', 'Digest generation error'


def test_create_digest_dir():
    """Create a digest-based directory.
    """
    # Given an numeric value
    value = '193433'

    # when I attempt to generate a digest path
    received = filer.gen_digest_path(value)

    # then the digest create engine should return a list of digests
    expected = ['73', '73b0', '73b0b6', '73b0b66e']
    assert received == expected, 'Digest directory path list error'


def test_create_digest_dir_shorten_path():
    """Create a digest-based directory: shortened path.
    """
    # Given an numeric value
    value = '193433'

    # when I attempt to generate a digest path
    received = filer.gen_digest_path(value)

    # then the digest create engine should return a list of digests
    expected = ['73', '73b0', '73b0b6', '73b0b66e']
    assert received == expected, 'Digest directory path list error'


def test_copy_file(working_dir):
    """Copy a file.
    """
    with tempfile.NamedTemporaryFile() as source_fh:
        # Check that the target does not exist.
        target = os.path.join(working_dir, os.path.basename(source_fh.name))
        assert not os.path.exists(target), 'Target file should not exist yet'
        filer.copy_file(source_fh.name, target)

    # Check that the target does exist.
    assert os.path.exists(target), 'Target file should exist'


def test_move_file_to_directory(working_dir):
    """Move a file into the current directory.
    """
    # Given an existing file
    with tempfile.NamedTemporaryFile(delete=False) as file_obj:
        filename = file_obj.name

        # and a target directory
        # working_dir

        # when I attempt to move the file to the target directory
        received = filer.move_file(filename, os.path.join(working_dir, os.path.basename(filename)))

        # then the response should be the fully qualified path to the new file
        assert received, 'Move file from current directory failed'

    # Clean up.
    try:
        os.removedirs(os.path.dirname(filename))
    except PermissionError:
        pass


def test_lock_file():
    """Lock a file.
    """
    # Given a file name
    with tempfile.NamedTemporaryFile(delete=False) as file_fh:
        filename = file_fh.name

    # when I lock the file
    received = filer.lock_file(filename)

    # then a subsequent read should raise a ValueError
    assert received.read() == '', 'Unable to read from file with exclusive lock'

    # Clean up.
    filer.unlock_file(received)
    filer.remove_files(filename)
    try:
        os.removedirs(os.path.dirname(filename))
    except PermissionError:
        pass


def test_get_file_time_in_utc():
    """Get file UTC time.
    """
    # Given a file
    with tempfile.NamedTemporaryFile() as file_obj:
        filename = file_obj.name

        # with a set modified time
        os.utime(filename, (1440901349, 1440901349))

        # when I source the file's modfied time stamp
        received = filer.get_file_time_in_utc(filename)

        # then the time should be a RFC 3339 UTC string
        expected = '2015-08-30T02:22:29Z'
        assert received == expected, 'File UTC time stamp error'


def test_get_file_time_in_utc_missing_file():
    """Get file UTC time: missing file..
    """
    # Given a missing file
    with tempfile.NamedTemporaryFile() as file_obj:
        filename = file_obj.name

    # when I source the missing file's modfied time stamp
    received = filer.get_file_time_in_utc(filename)

    # then should receive None
    assert not received, 'Missing file UTC time stamp error'
