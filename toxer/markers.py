import os
import pytest

in_docker = pytest.mark.skipif(not os.environ.get('TOX_DOCKER') == '1', reason="Run only inside docker container")

def need_os(os):
    return pytest.mark.skipif(not os.environ.get('TOX_DISTRO') == os, reason="Run only on %s" % os)

need_package = pytest.importorskip

global_only = pytest.mark.skipif(not os.environ.get('TOX_SITEPACKAGES') == '1',
                                       reason="Run only when sitepackages are enabled")

small_test = pytest.mark.skipif(os.environ.get('TOX_SKIP_SMALL') == '1', reason="Test size: small - disabled")
medium_test = pytest.mark.skipif(os.environ.get('TOX_SKIP_MEDIUM') == '1', reason="Test size: medium - disabled")
large_test = pytest.mark.skipif(os.environ.get('TOX_SKIP_LARGE') == '1', reason="Test size: large - disabled")