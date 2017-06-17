import urllib.request
import kiskadee.helpers

def download_source(source_data, path):
    pkg_version = ''.join([source_data.get('version'), '.tar.gz'])
    with kiskadee.helpers.chdir(path):
        url = source_url(pkg_version)
        in_file = urllib.request.urlopen(url)
        data = in_file.read()
        with open(pkg_version, 'wb') as info:
            info.write(data)
    return ''.join([path, '/', pkg_version])

def source_url(version):
    github_url = 'https://github.com/firecat53/urlscan/archive/'
    source_url = ''.join([github_url, version])
    return source_url
