"""Global fixture arrangement."""

import shutil
import tempfile

import _pytest.fixtures
import pytest

from filester.logging_config import log


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
