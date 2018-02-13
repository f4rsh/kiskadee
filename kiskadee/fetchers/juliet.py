"""Fetcher to analyze Juliet test cases.

Juliet is a static analysis test suite provided by NIST's SAMATE team. It
contains injected, known CWE's in specific points and similar code snippets
with the injected flaws fixed.
"""

import tempfile
import kiskadee.queue


class Fetcher(kiskadee.fetchers.Fetcher):
    """Fetcher to analyze Juliet test cases."""

    def get_sources(self, source_data):
        """Download Juliet 1.2 from SARD's website."""
        juliet_url = 'https://samate.nist.gov/SRD/testsuites/juliet/'
        juliet_filename = 'Juliet_Test_Suite_v1.2_for_C_Cpp.zip'
        tmp_path = tempfile.gettempdir()

        return self.download(
            tempfile.mkdtemp(dir=tmp_path),
            juliet_url + juliet_filename,
            juliet_filename
            )

    def watch(self):
        """SAMATE does not provide a proper API to inspect new Juliet versions.

        It should not matter, since Juliet does not receive updates frequently.
        """
        juliet = {}
        juliet['fetcher'] = __name__
        juliet['version'] = '1.2'
        juliet['name'] = 'juliet'
        super().watch(**juliet)

    def compare_versions(self, new, old):
        """Juliet has only one version.

        This method does not matter here, let's just pass
        """
        return 0
