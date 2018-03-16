Fetchers - plugins
==================

The Fetcher class defines a common behavior to all fetchers in kiskadee. This is
useful to easly define targets to be monitored by kiskadee. A target is a
software repository monitored for new packages.  source code is downloaded for
analysis when necessary. When creating a new fetcher, you must inherit from
`kiskadee.fetchers.Fetcher` and implement the required abstract methods. Each of
the behaviors defined in `kiskadee.fetchers.Fetcher` can be implemented according
to the target that will be monitored by the new fetcher.

The class defines the following behaviors:

.. autoclass:: kiskadee.fetchers.Fetcher()
   :members: compare_versions, get_sources, watch

Fetcher example
-----------------------

A simple example of a kiskadee fetcher

.. code-block:: python

    """Example kiskadee fetcher implementation."""

        import kiskadee

        class Fetcher(kiskadee.fetchers.Fetcher):
            """Example kiskadee fetcher implementation."""

            def get_sources(self, source_data):
                """Use sources from test suite."""
                return 'kiskadee/tests/test_source/test_source.tar.gz'

            def watch(self, **kwargs):
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

List of kiskadee fetchers
----------------------------

Inside the `fetchers` package you can check all available fetchers and what
targets are monitored by each fetcher. This section is a brief overview of
the available fetchers.

    - *anitya.py*: A fetcher to monitor fedmsg events, published on the
      Anitya project. The Anitya project monitors upstream releases and
      broadcasts them on fedmsg. The fetcher will consume these events, and
      trigger analyses when possible.

    - *debian.py*: A fetcher to monitor the Debian ftp repository. This fetcher
      will  download Debian *Sources.gz* hourly, and load it in memory. This
      file is a representation of all the packages available in the repository.
      After kiskadee loads it in memory, all the package  versions are compared
      with the ones in the database, and if a new package is identified, its
      source code is downloaded, and a new analysis is triggered.

    - *juliet.py*: Juliet is a static analysis test suite provided by
      NIST's SAMATE team. It contains injected, known CWE's in specific
      points and similar code snippets with the injected flaws fixed. This
      fetcher downloads the source code of this test suite, and run static
      analyzers on it.

    - *example.py*: A simple example of a kiskadee fetcher. Can be used as
      start point for new fetchers.

