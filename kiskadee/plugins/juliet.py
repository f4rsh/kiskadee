import urllib.request
import shutil
import os.path
import tempfile
import sys
import kiskadee.queue


class Plugin(kiskadee.plugins.Plugin):
    def get_sources(self, source_data):
        juliet_url = 'https://samate.nist.gov/SRD/testsuites/juliet/'
        juliet_filename = 'Juliet_Test_Suite_v1.2_for_C_Cpp.zip'
        zipfile_path = os.path.join(tempfile.mkdtemp(), juliet_filename)

        with urllib.request.urlopen(juliet_url + juliet_filename) as response,\
                open(zipfile_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return zipfile_path

    @kiskadee.queue.package_enqueuer
    def watch(self):
        """SAMATE does not provide a proper API to inspect new Juliet versions.
        It should not matter, since Juliet does not receive updates frequently.
        """
        juliet = {}
        juliet['plugin'] = sys.modules[__name__]
        juliet['version'] = '1.2'
        juliet['name'] = 'juliet'
        return juliet

    def compare_versions(self, new, old):
        """Juliet has only one version

        This method does not matter here, let's just pass
        """
        return 0
