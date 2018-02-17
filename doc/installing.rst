Installing kiskadee
===================

Development
-----------
To install locally run:

First, make shure that ansible will be able to login on the vm. ansible will
use the root user to do this, so you will have to add your public ssh
key inside the root ~/.ssh/authorized_keys file. You can also create the host
user inside the vm, in order to be able to test the vm access with the ping
command.

To check if ansible can access the machine:

.. code-block:: bash

    ansible -i playbook/hosts.local all  -m ping

To deploy kiskadee locally:

.. code-block:: bash

    ansible-playbook  -c paramiko -i playbook/hosts.local playbook/local.yml
