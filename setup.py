from setuptools import setup, find_packages
import re
import os


# Thanks to Pagure and SQLALchemy:
# https://pagure.io/pagure/blob/master/f/setup.py
# https://github.com/zzzeek/sqlalchemy/blob/master/setup.py
kiskadeefile = os.path.join(os.path.dirname(__file__),
                            'kiskadee', '__init__.py')

with open(kiskadeefile) as stream:
    regex = re.compile(r".*__version__ = '(.*?)'", re.S)
    __version__ = regex.match(stream.read()).group(1)


def get_requirements(requirements_file='requirements.txt'):
    with open(requirements_file) as f:
        return [
                line.rstrip().split('#')[0]
                for line in f.readlines()
                if not line.startswith('#')
                ]

setup(
    name='kiskadee',
    version=__version__,
    description='Continuous static analysis tool',
    long_description='Continuous static analysis tool \
            which writes the analyses \
            results into a Firehose database.',
    classifiers=[
            'Development Status :: 1 - Planning',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: '
            'GNU Affero General Public License v3 or later (AGPLv3+)',
            'Programming Language :: Python :: 3.5',
            'Topic :: Security',
                ],
    keywords='static analysis software assurance',
    author='Athos Ribeiro, David Carlos',
    author_email='athoscr@fedoraproject.org, ddavidcarlos1392@gmail.com',
    url='https://pagure.io/kiskadee',
    license='AGPLv3',
    packages=find_packages(),
    include_package_data=False,
    entry_points={'console_scripts': [
            'kiskadee = kiskadee.monitor:daemon',
            'kiskadee_api = kiskadee.api.app:main',],
            'moksha.consumer': (
                'anityaconsumer = kiskadee.fetchers.anitya:AnityaConsumer')},
    install_requires=get_requirements(),
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'flake8',
        'pydocstyle'
        ]
        )
