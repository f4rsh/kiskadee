from coverage import Coverage
import nose

sources = [
        'kiskadee.monitor',
        'kiskadee.queue',
        'kiskadee.runner',
        'kiskadee.model',
        'kiskadee.util',
        'kiskadee.api.app'
    ]

cov = Coverage(source=sources, omit="lib/*")
cov.start()
nose.run()
cov.stop()
cov.html_report(directory='covhtml')
