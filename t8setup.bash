#
#   t8setup.bash - common setup for projects using t8dev
#
#   This file should be sourced (`source` or `.`) by the top-level
#   `Test` script in projects using t8dev. Before sourcing it, the
#   T8_PROJDIR environment variable must be set with the path of
#   the project using t8dev. Further, it's helpful to initialise the
#   submodule if it's not yet been done. All this is typically done
#   with:
#
#       export T8_PROJDIR=$(cd "$(dirname "$0")" && pwd -P)
#       t8dir=tool/t8dev    # or whatever your submodule path is
#       [[ -r $T8_PROJDIR/$t8dir/t8setup.bash ]] \
#           || git submodule update --init "$T8_PROJDIR/$t8dir"
#
#   Note that as well as doing setup, this will do some command-line
#   argument processing for common arguments.
#

####################################################################
#   Confirm we are using Bash and that we're sourced, not called
#   as a subprocess. (The calling process needs the functions we
#   define and variables that we set.)

[ -n "$BASH_VERSION" ] || { echo 1>&2 "source (.) this with Bash."; exit 9; }
#   https://stackoverflow.com/a/28776166/107294
(return 0 2>/dev/null) \
    || { echo 1>&2 "source (.) project-setup.bash with Bash."; exit 9; }

####################################################################
#   Functions (used here and by the caller)

die() {
    local exitcode="$1"; shift
    [[ -z $1 ]] || echo 1>&2 "$@"
    exit $exitcode
}

warn() { echo 1>&2 "WARNNG:" "$@"; }

#   From: https://github.com/0cjs/sedoc, git/submodule.md
submodules_warn_modified() {
    count=$(git submodule status --recursive | sed -n -e '/^[^ ]/p' | wc -l)
    [ $count -eq 0 ] || warn "$count Git submodules are modified."
    #   XXX Can we figure out a way to look for submodules that have no
    #   working copy, and ask for a `git submodule update --init` on those?
    #   At the moment, the end user needs to figure it out himself.
}

submodules_pip_install_e() {
    #   If the parent project has any submodules that have a `pyproject.toml`
    #   at the top level, we assume that those are Python dependencies that
    #   should be installed and, further, they should be installed as
    #   editable because that's why they're submodules instead of just in
    #   requirements.txt.
    for submodule in $(git config -f .gitmodules -l \
        | sed -n -e 's/^submodule\.//' -e 's/.*\.path=//p')
    do
        dir="$T8_PROJDIR/$submodule"
        [[ -r $dir/pyproject.toml ]] || continue
        #   XXX The `pip inspect` is slowish (almost a second), but not as slow
        #   as doing the `pip install -e` when it's already been done. Can we
        #   somehow do this check faster?
        #   See: https://stackoverflow.com/q/77875816/107294
        if ! pip inspect | grep -q ".url.: .file://$dir"; then
            echo "----- Installing submodule $submodule" \
                'as editable into virtual environment.'
            pip install -q -e "$dir"
        fi
    done
}

####################################################################
#   Main

[[ -n ${T8_PROJDIR:-} ]] || die 2 "$0: T8_PROJDIR not set"
[[ -z ${BUILDDIR:-} ]] && BUILDDIR="$T8_PROJDIR/.build"

#   Exports are separate from setting to ensure that variables set
#   by the caller are exported by us, if the caller didn't export.
export T8_PROJDIR BUILDDIR

#   Leading command line args (these must be at the start):
#   • -C: clean rebuild of everything, including toolchains
#   • -c: clean rebuild of only this repo's source (test/toolchain output)
#   All args after these are left for the calling script.
while [[ ${#@} -gt 0 ]]; do case "$1" in
    --)     shift; break;;
    -C)     shift; rm -rf "$BUILDDIR" ${T8_CLEAN_C-};;
    -c)     shift;
            rm -rf "$BUILDDIR"/{obj,ptobj,pytest,virtualenv} ${T8_CLEAN_c-} ;;
    *)      break;;
esac; done

(cd "$T8_PROJDIR" && submodules_warn_modified)
. "$(dirname ${BASH_SOURCE[0]})"/pactivate -B "$T8_PROJDIR" -q
submodules_pip_install_e

#   XXX This can go away once we switch to `pip -e` installs of t8dev.
[[ $PATH =~ ^$T8_PROJDIR/bin:|:$T8_PROJDIR/bin:|:$T8_PROJDIR/bin$ ]] \
    || export PATH="$T8_PROJDIR/bin:$PATH"
