Common interface to kiskadee plugins
====================================

The Plugin class defines a common behavior to all plugins in kiskadee. This is
useful to easly define targets to be monitored by kiskadee. A target is a
software repository monitored for new packages.  source code is downloaded for
analysis when necessary. When creating a new plugin, you must inherit from
`kiskadee.plugins.Plugin` and implement the required abstract methods. Each of
the behaviors defined in `kiskadee.plugins.Plugin` can be implemented according
to the target that will be monitored by the new plugin.

The class defines the following behaviors:

.. autoclass:: kiskadee.plugins.Plugin()
   :members: compare_versions, get_sources, watch

Plugin example
-----------------------

A simple example of a kiskadee plugin

.. code-block:: python

    import kiskadee
    import sys
    import kiskadee.queue
    class Plugin(kiskadee.plugins.Plugin):
        def get_sources(self, source_data):
            return 'kiskadee/tests/test_source/test_source.tar.gz'

        @kiskadee.queue.package_enqueuer
        def watch(self):
            """There is no proper API to inspect new example versions.
            It should not matter, since example will not receive updates.
            """
            example = {}
            example['plugin'] = sys.modules[__name__]
            example['version'] = '0.1'
            example['name'] = 'example'
            return example

        def compare_versions(self, new, old):
            """Example has only one version

            This method does not matter here, let's just pass
            """
            return 0

List of kiskadee plugins
----------------------------

Inside tha package `plugins` you can check which plugins kiskadee have,
and which targets are monitored with this plugins. This section is a brief
overview of this plugins.

    - *debian.py*: A plugin to monitor the Debian ftp repository. This plugin
      will  every hour downloads the *Sources.gz* file of the repository and
      loads it in memory. This file is a representation of all the packages
      present in the repository. After kiskadee loads it in memory, all the
      packages are compared with the database, and if a new package is
      identified, it source code is downloaded, and a analysis is made.

    - *anitya.py*: A plugin to monitor fedmsg events, published on the
      Anitya project. The Anitya project monitor upstream releases and
      broadcast them on fedmsg. The plugin will consume this events, and
      trigger analysis when it's possible.


    - *juliet.py*: Juliet is a static analysis test suite provided by
      NIST's SAMATE team. It contains injected, known CWE's in specific
      points and similar code snippets with the injected flaws fixed. This
      plugin downloads the source code of this test suite, and run static
      analyzers on it.

    - *example.py*: A simple example of a kiskadee plugin. Can be used as
      start point for new plugins.

