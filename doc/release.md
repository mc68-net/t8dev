Releasing r8format and t8dev
============================

This uses the procedure and script in [cynic-net/pypi-release], but
with a couple of changes in order to deal with two different packages
being released from one repo.

1. You will need to run `build-release` separately in the `r8format/`
   and `t8dev/` subdirectories.

2. When tagging the release, tag it not as `v0.0.0` but as `r8format-0.0.0`
   or `t8dev-0.0.0`. (For a simultaneous release, both tags will be on the
   same commit, and you'll need to remember to push both.)

#### Warnings and Errors

Since t8dev 0.0.5, pyproject-build has been saying:

    ERROR setuptools_scm._file_finders.git \
        listing git files failed - pretending there aren't any

But it does still seem to be including the git-committed non-Python files
under psrc. So it's not clear what's going on with this. This may be
related to [setuptools-scm#890]



<!-------------------------------------------------------------------->
[cynic-net/pypi-release]: https://github.com/cynic-net/pypi-release
[setuptools-scm#890]: https://github.com/pypa/setuptools-scm/issues/890
