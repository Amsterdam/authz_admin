Datapunt Permission Management and OAuth2 Authorization Services
================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/oauth2_service
   api/admin_service
   api/shared
   todo_list


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Sphinx 101
==========


ReST formatting
---------------

For details on basic rST foramtting, see `Sphinx’ reStructuredText Primer <sphinx:rst-primer>`_. or :sphinx:`rst-primer`. `collections.namedtuple`

::

    * *emphasis*, **strong empasis**, ``code``
    * *``nesting``* ``*won’t*`` ````work````
    * *roles* are formatted as ``:rolename:`some text```. RST predefines
        :emphasis:`emphasis`, :strong:`strong`, :literal:`literal`,
        :subscript:`subscript`, :superscript:`superscript`, and
        :title-reference:`title-reference`.

        #. Numbered lists look like this

            #. and can be nested, as long as there is

        #. an empty line between the lists.

    Definition lists
        have one line for the *term*, followed by one or more indented
        multiline paragraphs.

        Like this.

* *emphasis*, **strong empasis**, ``code``
* *``nesting``* ``*won’t*`` ````work````
* *roles* are formatted as ``:rolename:`some text```. RST predefines
    :emphasis:`emphasis`, :strong:`strong`, :literal:`literal`,
    :subscript:`subscript`, :superscript:`superscript`, and
    :title-reference:`title-reference`.

    #. Numbered lists look like this

        #. and can be nested, as long as there is

    #. an empty line between the lists.

Definition lists
    have one line for the *term*, followed by one or more indented
    multiline paragraphs.

    Like this.

`intersphinx link <sphinx:rest>`_

Directives
----------

**Syntax**::

    .. directive:: thing1

.. rst:directive:: automodule
                   autoclass
                   autoexception

    Document a module, class or exception.

    **Options**

    * ``:members:``
