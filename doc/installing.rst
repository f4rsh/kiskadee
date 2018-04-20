Installing kiskadee
===================

Development
-----------
To quick setup kiskadee environment you can use our ansible playbook with
vagrant. The first thing to do is to create the virtual machines necessary to
run kiskadee. Kiskadee backend runs on the kiskadee-core vm, so lets create
it:

.. code-block:: bash

    vagrant up

This command will create all vagrant images. You can take a look on
Vagrantfile, to check which virtual machines are available. kiskadee uses libvirt
+ qemu to manage virtual machines. If you are using virtualbox as hypervisor, 
you will need to hack the Vagrantfile and adapt it to your needs (send us a PR :) ).

.. warning::

        If you are using libvirt to manage vms, and you see a error saying that
        a domain for kiskadee-core already exists, you can remove (with root) the old domain:

        .. code-block:: bash

           virsh undefine kiskadee_kiskadee-core

        Drop the old vm:

        .. code-block:: bash

           vagrant destroy kiskadee-core

        And run `vagrant up` again.


First, make sure that ansible will be able to login on the vm. ansible will
use the root user to do that, so you will have to add your public ssh
key inside the root **~/.ssh/authorized_keys** file. You can also create the host
user inside the vm, in order to be able to test the vm access with the ping
command. To add your ssh key run:

.. code-block:: bash

    vagrant ssh kiskadee-core
    sudo su
    ssh-keygen

Append your public key inside the **~/.ssh/authorized_keys** file and **logout** the vm.

Install the ansible package:

.. code-block:: bash

   sudo pip install ansible

To check if ansible can access the kiskadee-core virtual machine:

.. code-block:: bash

    ansible -i playbook/hosts.local kiskadee-core  -m ping

If you see a success message, we are good to go.

To deploy kiskadee locally:

.. code-block:: bash

    ansible-playbook  -c paramiko -i playbook/hosts.local playbook/local.yml

To test if kiskadee was installed correctly, log in the kiskadee-core vm and
inside the kiskadee folder call the command `kiskadee`. If the environment is
properly configured, kiskadee will run a simple analysis using the example
fetcher.

You can start kiskadee api running `kiskadeee_api`. 
You can access the list of analyzed packages on `localhost:5000/packages`.

Production
----------

We are still working on a rpm package to install kiskadee on production mode.
You can check the latest build `here <https://copr.fedorainfracloud.org/coprs/davidcarlos/kiskadee/>`_.
