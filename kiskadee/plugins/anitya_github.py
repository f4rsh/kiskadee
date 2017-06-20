import urllib.request
import kiskadee.helpers

def download_source(source_data, path):
    source_version = ''.join([source_data.get('version'), '.tar.gz'])
    homepage = source_data.get('meta').get('homepage')

    if homepage.find("github") != -1:
        with kiskadee.helpers.chdir(path):
            url = source_url(pkg_version, homepage)
            in_file = urllib.request.urlopen(url)
            data = in_file.read()
            with open(pkg_version, 'wb') as info:
                info.write(data)
        return ''.join([path, '/', pkg_version])
    else:
        return {}

def source_url(version, homepage):
    return ''.join([homepage, '/archive/', version])
