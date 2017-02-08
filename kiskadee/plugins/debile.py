import tempfile
import shutil
from subprocess import call
import os
import docker

DEBILE_DATA = '/srv/debile/incoming/UploadQueue/'

class Runner():

    def __init__(self):
        self.client = docker.from_env()
        self.slave = None
        self.master = None
        self.pg = None
        self.data = None
        self.http = None

    def watch(self):
        return  {'source': 'rofi', 'version': '1.3.1-2'}

    def callback(self):
        pass

    def container_id(self):
        call(['docker', 'ps -aqf "name=debile-pg"'], shell=True)

    def setup_container(self, container_name):
        try:
            container = self.containers().get('debile-%s' % container_name)
            setattr(self, container_name, container)
            self.start_container(container, container_name)
        except Exception:
            print("Something went wrong and " +
                  "container was not properly started")
            method_call = getattr(self, "run_%s" % container_name)
            method_call()

    def start_container(self, container, container_name):
        try:
            container.start()
            return container
        except Exception:
            print('Container %s already runnin' % container_name)
            return container

    def docker_setup(self):
        containers = ['data', 'pg', 'http',
                      'master', 'slave']
        for container in containers:
            self.setup_container(container)

    def run_master(self):
            print('Starting debile master')
            self.master = self.containers().run("debile-master-pkg",
                                                "tail -f /tmp/debile/debile_master_log",
                                                name='debile-master',
                                                links={'debile-pg': 'debile-pg'},
                                                volumes_from=['debile-data'],
                                                detach=True)
            self.master.exec_run(self.__init_db())
            self.master.exec_run(self.__init_master_loop(), detach=True, stream=True)

    def __init_master_loop(self):
        return "/bin/bash -c 'debile-master --config /etc/debile/master.yaml --auth simple &> /tmp/debile/debile_master_log'"

    def __init_db(self):
        return "/bin/bash -c 'debile-master-init --config /etc/debile/master.yaml /etc/debile/debile.yaml  &> /tmp/debile/debile_master_log'"

    def run_slave(self):
            print('Starting debile slave')
            self.slave = self.containers().run("debile-slave-pkg",
                                               "debile-slave --config " +
                                               "/etc/debile/slave.yaml " +
                                               "--auth simple",
                                               links={'debile-http': 'debile-http',
                                                      'debile-master': 'debile-master'},
                                               name='debile-slave',
                                               detach=True)

    def run_pg(self):
            self.pg = self.containers().run("clemux/debile-pg",
                                            name='debile-pg',
                                            ports={'5432': '5432'},
                                            detach=True)
    def run_data(self):
            self.pg = self.containers().run("clemux/debile-data",
                                            name='debile-data',
                                            detach=True)

    def run_http(self):
            self.http = self.containers().run("clemux/debile-http",
                                              "tail -f /dev/null",
                                              name='debile-http',
                                              volumes_from=['debile-data'],
                                              ports={'80': '80'},
                                              detach=True)

    def upload(self):
        data = self.watch()
        self.slave.exec_run("debile-upload --dist=unstable " +
                            " --source=%s" % data['source'] +
                            " --version=%s" % data['version'] +
                            " --group=default")
        self.__incoming()
        # self.__check_builded_job(data)

    def containers(self):
        return self.client.containers


    def __incoming(self):
        self.master.exec_run("debile-incoming --config " +
                             "/etc/debile/master.yaml --group default " +
                             "--no-dud /srv/debile/incoming/UploadQueue/",
                             detach=True)


    # TODO: Remove tempdir after retrieve firehose
    def get_firehose(self):
        tempdir = tempfile.mkdtemp()
        firehose_file = 'tmux_2.3-4_amd64.4.firehose.xml'
        abs_firehose_file = tempdir + '/' + 'tmux_2.3-4_amd64.4.firehose.xml'
        kiskadee_report = tempfile.NamedTemporaryFile(delete=False, prefix=tempdir)
        call(['docker', 'cp', 'debile-master:%s%s' % (DEBILE_DATA, firehose_file), tempdir])
        with open(abs_firehose_file, 'rw+') as f:
            line = f.readline()
            kiskadee_report.write(line)

        return kiskadee_report

    def __check_builded_job(self, data):
        while True:
            print("checking %s build" % data['source'])

if __name__ == "__main__":
    debile = Runner()
    debile.docker_setup()
    debile.upload()
