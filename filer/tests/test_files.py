import unittest2
import tempfile
import os

from filer.files import (get_directory_files,
                         get_directory_files_list,
                         remove_files,
                         move_file,
                         check_filename,
                         gen_digest,
                         copy_file,
                         gen_digest_path,
                         lock_file,
                         unlock_file,
                         get_file_time_in_utc)


class TestFiles(unittest2.TestCase):
    """:class:`filer.Files`
    """
    def test_get_directory_files_no_directory(self):
        """Get directory file -- no directory.
        """
        directory = tempfile.mkdtemp()
        os.removedirs(directory)

        received = []
        for filename in get_directory_files(directory):
            received.append(filename)
        expected = []
        msg = 'Missing directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(directory)
        expected = []
        msg = 'Missing directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

    def test_get_directory_files_no_files(self):
        """Get directory file -- no files.
        """
        directory = tempfile.mkdtemp()

        received = []
        for filename in get_directory_files(directory):
            received.append(filename)
        expected = []
        msg = 'Empty directory listing error'
        self.assertListEqual(received, expected, msg)

        received = get_directory_files_list(directory)
        expected = []
        msg = 'Empty directory listing error (list variant)'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        os.removedirs(directory)

    def test_get_directory_files(self):
        """Get directory files.
        """
        directory = tempfile.mkdtemp()
        file_obj = tempfile.NamedTemporaryFile(dir=directory)
        filename = file_obj.name

        received = get_directory_files_list(directory)
        expected = [filename]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        file_obj.close()
        os.removedirs(directory)

    def test_get_directory_files_filtered(self):
        """Get directory files.
        """
        file_obj = tempfile.NamedTemporaryFile()
        directory = os.path.dirname(file_obj.name)
        filename = file_obj.name

        filter_file = 'TCD_Deliveries_20140207111019.DAT'
        file_h = open(os.path.join(directory, filter_file), 'w')
        file_h.close()

        file_filter = r'TCD_Deliveries_\d{14}\.DAT'
        received = get_directory_files_list(os.path.dirname(filename),
                                            file_filter=file_filter)
        expected = [os.path.join(directory, filter_file)]
        msg = 'Directory listing error'
        self.assertListEqual(received, expected, msg)

        # Clean up.
        remove_files(os.path.join(directory, filter_file))

    def test_check_filename(self):
        """Check T1250 filename format.
        """
        re_format = r'T1250_TOL.*\.txt'
        # Priority.
        received = check_filename('T1250_TOLP_20130904061851.txt',
                                  re_format)
        msg = 'Priority T1250 filename should validate True'
        self.assertTrue(received, msg)

        # Fast.
        received = check_filename('T1250_TOLF_VIC_20130904061851.txt',
                                  re_format)
        msg = 'Fast VIC T1250 filename should validate True'
        self.assertTrue(received, msg)

        # Dodgy.
        received = check_filename('T1250_dodgy_20130904061851.txt',
                                  re_format)
        msg = 'Dodgy filename should validate False'
        self.assertFalse(received, msg)

    def test_gen_digest_invalids(self):
        """Generate digest -- invalid value.
        """
        received = gen_digest(None)
        msg = 'Digest generation error -- None value'
        self.assertIsNone(received, msg)

        received = gen_digest(1234)
        msg = 'Digest generation error -- non-string value'
        self.assertIsNone(received, msg)

    def test_gen_digest(self):
        """Generate digest -- valid values.
        """
        received = gen_digest('193433')
        expected = '73b0b66e'
        msg = 'Digest generation error -- valid value'
        self.assertEqual(received, expected, msg)

    def test_create_digest_dir(self):
        """Create a digest-based directory.
        """
        received = gen_digest_path('193433')
        expected = ['73', '73b0', '73b0b6', '73b0b66e']
        msg = 'Digest directory path list error'
        self.assertListEqual(received, expected, msg)

    def test_copy_file(self):
        """Copy a file.
        """
        source_fh = tempfile.NamedTemporaryFile()
        fh = tempfile.NamedTemporaryFile()
        target = fh.name
        fh.close()

        # Check that the target does not exist.
        msg = 'Target file should not exist yet'
        self.assertFalse(os.path.exists(target))

        copy_file(source_fh.name, target)

        # Check that the target does exist.
        msg = 'Target file should exist '
        self.assertTrue(os.path.exists(target), msg)

        # Clean up.
        remove_files(target)
        source_fh.close()

    def test_move_file_to_current_directory(self):
        """Move a file into the current directory.
        """
        file_fh = tempfile.NamedTemporaryFile(delete=False)
        filename = file_fh.name

        received = move_file(filename, os.path.basename(filename))
        msg = 'Move file from current directory failed'
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(os.path.basename(filename))

    def test_move_file_to_directory(self):
        """Move a file into a new directory.
        """
        target_dir = 'banana'
        file_fh = tempfile.NamedTemporaryFile(delete=False)
        filename = file_fh.name

        received = move_file(filename,
                             os.path.join(target_dir,
                                          os.path.basename(filename)))
        msg = 'Move file from current directory failed'
        self.assertTrue(received, msg)

        # Clean up.
        remove_files(get_directory_files_list('banana'))
        os.removedirs('banana')

    def test_lock_file(self):
        """Lock a file.
        """
        file_fh = tempfile.NamedTemporaryFile(delete=False)
        filename = file_fh.name
        file_fh.close()

        file_desc = lock_file(filename)
        received = file_desc.read()
        expected = str()
        msg = 'Lock did not return a valid file descriptor'
        self.assertEqual(received, expected, msg)

        unlock_file(file_desc)
        self.assertRaises(ValueError, file_desc.read)

        # Clean up.
        remove_files(filename)

    def test_get_file_time_in_utc(self):
        """Get file UTC time.
        """
        # Given a file
        file_obj = tempfile.NamedTemporaryFile(delete=False)
        filename = file_obj.name
        file_obj.close()

        # with a set modified time
        os.utime(filename, (1440901349, 1440901349))

        # when I source the file's modfied time stamp
        received = get_file_time_in_utc(filename)

        # then the time should be a RFC 3339 UTC string
        expected = '2015-08-30T02:22:29Z'
        msg = 'File UTC time stamp error'
        self.assertEqual(received, expected, msg)

        # Clean up.
        remove_files(filename)

    def test_get_file_time_in_utc_missing_file(self):
        """Get file UTC time: missing file..
        """
        # Given a missing file
        file_obj = tempfile.NamedTemporaryFile()
        filename = file_obj.name
        file_obj.close()

        # when I source the missing file's modfied time stamp
        received = get_file_time_in_utc(filename)

        # then should receive None
        msg = 'Missing file UTC time stamp error'
        self.assertIsNone(received, msg)
