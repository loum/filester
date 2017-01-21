#####
Filer
#####
Generic, file-based utilities and helpers!  Build and read the docs (as per below) for more info.

*************
Prerequisites
*************
Targeting Python 3 here on a Linux platform, namely CentOS 7.

On a vanilla CentOS 7, you will need to install Python 3 manually.  `IUS <https://ius.io/GettingStarted/>`_ can help you with this.  Then::

    $ sudo yum install -y python35u

Now, set ``python3`` to your Python 3 executable::

    $ sudo alternatives /usr/bin/python3 python3 /urs/bin/python3.5 20000

Note: ``python3`` must exist in order for the project ``Makefile`` to function correctly.

***************
Getting Started
***************
Get the code::

    $ git clone https://github.com/loum/filer.git
    
Build the virtual environment and download project dependencies::

    $ cd filer
    $ make init_wheel
    
Run the tests to make sure all is OK::

    $ source venv/bin/activate
    (venv) $ make tests

***********************
Build the Documentation
***********************
Project documentation is self contained under the ``doc/source`` directory.  To build the documentation locally::

    $ make docs

The project comes with a simple web server that allows you to present the docs from within your own environment::

    $ cd docs/build
    $ ./http_server.py
    
Note: The web server will block your CLI and all activity will be logged to the console.  To end serving pages, just ``Ctrl-C``.
    
To view pages, open up a web browser and navigate to ``http:<your_server_IP>:8888``

****
FAQs
****
**Why can't access the docs from my browser?**

Firewall?  Try::

    $ sudo firewall-cmd --zone=public --add-port=8888/tcp --permanent
    $ sudo firewall-cmd reload
