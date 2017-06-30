# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
"""Helper functions needing a new home."""

import os
import urllib.request
from contextlib import contextmanager

import kiskadee


@contextmanager
def chdir(path):
    """Context manager decorator for temporary directories."""
    initial_dir = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(initial_dir)


def download(path, url, file_name):
    """Download something from the internet.

    :path: The path where the file will be placed when downloaded.
    :url: Url of the file.
    :file_name: The name of the file that will be saved on the disc.
    :return: The absolute path to the downloaded file.
    """
    try:
        with chdir(path):
            in_file = urllib.request.urlopen(url)
            data = in_file.read()
            with open(file_name, 'wb') as info:
                info.write(data)
        return ''.join([path, '/', file_name])
    except Exception as err:
        kiskadee.logger.debug(
                "Cannot download {} "
                "source code".format(file_name)
        )
        kiskadee.logger.debug(err)
        return {}
