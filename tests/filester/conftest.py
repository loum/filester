"""Global fixture arrangement.

"""
import shutil
import tempfile

from logga import log
import _pytest.fixtures
import pytest


@pytest.fixture
def working_dir(request: _pytest.fixtures.SubRequest) -> str:
    """Temporary working directory."""

    def fin() -> None:
        """Tear down."""
        log.info('Deleting temporary test directory: "%s"', dirpath)
        shutil.rmtree(dirpath)

    request.addfinalizer(fin)
    dirpath = tempfile.mkdtemp()
    log.info('Created temporary test directory: "%s"', dirpath)

    return dirpath
