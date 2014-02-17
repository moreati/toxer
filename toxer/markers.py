import os
import pytest

in_docker = pytest.mark.skipif(not os.environ.get('TOX_DOCKER') == '1', reason="Run only inside docker container")

def need_os(os_needed):
    return pytest.mark.skipif(not os.environ.get('TOX_DISTRO') == os_needed, reason="Run only on %s" % os)

need_package = pytest.importorskip

global_only = pytest.mark.skipif(not os.environ.get('TOX_SITEPACKAGES') == '1',
                                       reason="Run only when sitepackages are enabled")

slow = pytest.mark.slow