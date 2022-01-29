"""Global fixture arrangement.

"""
import tempfile
import shutil
import logging
import pytest


@pytest.fixture
def working_dir(request):
    """Temporary working directory.
    """
    def fin():
        """Tear down.
        """
        logging.info('Deleting temporary test directory: "%s"', dirpath)
        shutil.rmtree(dirpath)

    request.addfinalizer(fin)
    dirpath = tempfile.mkdtemp()
    logging.info('Created temporary test directory: "%s"', dirpath)

    return dirpath
