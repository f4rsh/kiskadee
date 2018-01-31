"""Example kiskadee fetcher implementation."""

import kiskadee

class Fetcher(kiskadee.fetchers.Fetcher):
    """Example kiskadee fetcher implementation."""

    def get_sources(self, source_data):
        """Use sources from test suite."""
        return 'kiskadee/tests/test_source/test_source.tar.gz'

    @kiskadee.queue.enqueue_project
    def watch(self):
        """There is no proper API to inspect new example versions.
        It should not matter, since example will not receive updates.
        """
        example = {}
        example['fetcher'] = __name__
        example['version'] = '0.1'
        example['name'] = 'example'
        super().watch(**example)

    def compare_versions(self, new, old):
        """Compare package versions.

        Example has only one version. This method does not matter here, let's
        just pass.
        """
        return 0
