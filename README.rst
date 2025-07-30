.. role:: bash(code)
    :language: bash

.. role:: python(code)
    :language: python

.. image:: https://img.shields.io/pypi/v/tikzify
   :target: https://pypi.org/project/tikzify/
   :alt: PyPI - Version
   :align: center
.. image:: https://img.shields.io/badge/version_scheme-EffVer-0097a7
   :alt: EffVer Versioning
   :target: https://jacobtomlinson.dev/effver
.. image:: https://img.shields.io/pypi/pyversions/tikzify
   :alt: PyPI - Python Version
   :align: center

=======
Tikzify
=======

A set of utilities for programmatically generating Typst code.

Previously: Tikz/Latex code; now, Typst.  This is a work in progress.

Contribution guidelines
=======================

The implementation should be consistent with the surrounding style, be type annotated, and pass the
linters below.

There are a few tools to clean and check the source:

- :bash:`ruff check`
- :bash:`pyright`
- :bash:`mypy`
- :bash:`isort .`
- :bash:`pylint tikzify`

Running
=======

- The basal ganglia example can be run by doing :bash:`dm basal_ganglia` from the examples folder.  It should produce :bash:`examples/basal_ganglia.pdf`, which shows all of the output, as well as :bash:`examples/figures/basal_ganglia-*.pdf`, which are the individual diagrams to be included.

- A copy of the `pdf <examples/basal_ganglia.pdf>` is provided.  It shows three programmatically-generated diagrams, with various sections highlighted.

Whom do I talk to?
==================

- Neil Girdhar
