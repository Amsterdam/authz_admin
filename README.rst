.. reference this page as :ref:`index` (from which it's included)

Datapunt OAuth2 Services
========================

.. image:: https://img.shields.io/badge/python-3.6-blue.svg
   :target: https://www.python.org/

.. image:: https://img.shields.io/badge/license-MPLv2.0-blue.svg
   :target: https://www.mozilla.org/en-US/MPL/2.0/

The latest published documentation for this project can be found `here
<https://amsterdam.github.io/authz_admin/>`_.

.. todo::

   Publish the documentation somewhere (ReadTheDocs?) and insert a link in the
   sentence above.


Conventions
===========

*   The project top-level directory is also the source root.
*   We use PyTest for tests.
*   PyTest can be integrated with SetupTools (see
    https://docs.pytest.org/en/latest/goodpractices.html). We don’t do this.
*   Common commands for builds, distributing, packaging, documentation etcetera
    are in :file:`Makefile` and :file:`docs/Makefile`.
*   RST-files and -docstrings are indented with 4 spaces.
*   Globals must be immutable.
*   Docstrings are formatted like this:

    .. code-block:: python

        """This is a one-line docstring."""
        """One line description, terminated with a period.

        More info, with a trailing empty line.

        """


Getting Started
===============

.. code-block:: bash

    # Clone the repository:
    git clone git@github.com:Amsterdam/authz_admin.git
    cd authz_admin

    # Create and activate a virtual environment, for example with:
    python3.6 -m venv --copies --prompt authz_admin .venv
    source ./.venv/bin/activate

    pip install -e .[docs,test,dev]

    # Start a database server (required for all sub-services):
    docker-compose up -d database

    # To test the service:
    source env.sh && make test

    # To start the service:
    source env.sh && make run

    # To start a documentation server:
    make -C docs server

After starting the server, the API can be accessed through
http://localhost:8000/authz_admin/\. The Swagger UI front-end is available at
http://localhost:8000/authz_admin/swagger-ui/index.html\.


Starting the service
--------------------

The service can be started in at least 2 ways:

1.  Directly, like this:

    .. code-block:: shell

        PYTHONPATH=${PROJECT_HOME:-.}/src python -m authz_admin.main

2.  Through setuptools console script. This is functionally identical to the
    previous method, and only provided as a shortcut:

    .. code-block:: shell

        authz_admin


Database Schema Management
==========================

We use `alembic <http://alembic.zzzcomputing.com/en/latest/index.html>` for
database schema management. The configuration can be found in the
:file:`alembic` subdirectory.


About Scopes
============

.. todo:: write about the semantics of scopes in our implementation.
