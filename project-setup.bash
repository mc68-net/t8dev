#
#   project-setup.bash - common setup for projects using t8dev
#
#   This file should be sourced (`source` or `.`) by the top-level
#   `Test` script in projects using t8dev. Before sourcing it, the
#   T8_PROJDIR environment variable must be set with the path of
#   the project using t8dev. This is typically done with:
#
#       export T8_PROJDIR=$(cd "$(dirname "$0")" && pwd -P)
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
check_submodules() {
    count=$(git submodule status --recursive | sed -n -e '/^[^ ]/p' | wc -l)
    [ $count -eq 0 ] || {
        warn "$count Git submodules are not up to date"
        warn 'Run `git submodule update --init`?'
    }
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

(cd "$T8_PROJDIR" && check_submodules)
. $T8_PROJDIR/t8dev/pactivate -B "$T8_PROJDIR" -q

#   XXX This can go away once we switch to `pip -e` installs of t8dev.
[[ $PATH =~ ^$T8_PROJDIR/bin:|:$T8_PROJDIR/bin:|:$T8_PROJDIR/bin$ ]] \
    || export PATH="$T8_PROJDIR/bin:$PATH"
