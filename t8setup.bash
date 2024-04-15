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
#       . "$T8_PROJDIR"/$t8dir/t8setup.bash
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

warn() { echo 1>&2 "WARNNG:" "$@"; }

submodules_list() {
    #   Return a list of all submodule paths relative to $T8_PROJDIR.
    #   XXX This should set an array so we can handle spaces in the paths.
    git config -f "$T8_PROJDIR"/.gitmodules -l \
        | sed -n -e 's/^submodule\.//' -e 's/.*\.path=//p'
}

submodules_warn_modified() {
    #   If any submodules are modified, warn about this. Usually this is
    #   because the developer is working on submodule code (and needs to
    #   commit it before commiting her project) or the developer is testing
    #   an update to new versions of submodules.
    local sms="$(submodules_list)"
    git -C "$T8_PROJDIR" diff-index --quiet @ $sms || {
        echo '----- WARNING: submodules are modified:' \
            "$(git -C "$T8_PROJDIR" status -s $sms | tr -d '\n')"
    }
}

submodules_init_empty() {
    #   Check out any "empty" submodules in the parent project, i.e., those
    #   that appear not to be initialised because they do not have a file
    #   or directory named `.git` in their submodule directory.
    local sm
    for sm in $(submodules_list); do
        dir="$T8_PROJDIR/$sm"
        [[ -e $dir/.git ]] && continue
        echo "----- Initializing empty submodule $sm"
        (cd $T8_PROJDIR && git submodule update --init "$sm")
    done
}

submodules_pip_install_e() {
    #   If the parent project has any submodules that have a `pyproject.toml`
    #   at the top level, we assume that those are Python dependencies that
    #   should be installed and, further, they should be installed as
    #   editable because that's why they're submodules instead of just in
    #   requirements.txt.
    local sm
    for sm in $(submodules_list); do
        dir="$T8_PROJDIR/$sm"
        [[ -r $dir/pyproject.toml ]] || continue
        #   XXX The `pip inspect` is slowish (almost a second), but not as slow
        #   as doing the `pip install -e` when it's already been done. Can we
        #   somehow do this check faster?
        #   See: https://stackoverflow.com/q/77875816/107294
        #   Also, note that we do not use `grep -q` as this stops reading
        #   on the first match and can thus produce Errno 32 Broken pipe.
        if ! pip inspect | grep >/dev/null ".url.: .file://$dir"; then
            echo "----- Installing submodule $sm" \
                'as editable into virtual environment.'
            pip install -q -e "$dir"
        fi
    done
}

t8_check_r8format_dependency() {
    #   Ensure that we can import the `binary` package from r8format,
    #   as we depend on several modules from that package.
    #   XXX This should use `binary.__version__ or something like that
    #   when that becomes available.
    local pyprg='
import sys
try:
    import binary.memimage
except ModuleNotFoundError as ex:
    print("{}: {}".format(ex.__class__.__name__, ex.msg), file=sys.stderr)
    sys.exit(1)
'
    python -c "$pyprg" || {
        echo 1>&2 \
            'ERROR: r8format package not available. Install or add submodule.'
        exit 8
    }
}

####################################################################
#   Main

[[ -n ${T8_PROJDIR:-} ]] || { echo 2>&1 'ERROR: T8_PROJDIR not set'; return 2; }
[[ -z ${BUILDDIR:-} ]] && BUILDDIR="$T8_PROJDIR/.build"

#   Exports are separate from setting to ensure that variables set
#   by the caller are exported by us, if the caller didn't export.
export T8_PROJDIR BUILDDIR

#   Bring in directory for tools local to this project, if not already present.
#   XXX We should probably also be bringing in the paths for discovered
#   tools external to the project, but it's not clear how to do that here,
#   since at this point the tools might not yet have been built.
[[ :$PATH: = *:$BUILDDIR/tool/bin:* ]] || PATH="$BUILDDIR/tool/bin:$PATH"

#   If the project has its own local bin/ directory, include that in
#   the path as well.
[[ -d "$T8_PROJDIR/bin" && :$PATH: != *:$T8_PROJDIR/bin:* ]] \
    && PATH="$T8_PROJDIR/bin:$PATH"

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

. "$(dirname ${BASH_SOURCE[0]})"/pactivate -B "$T8_PROJDIR" -q
submodules_init_empty
submodules_warn_modified
submodules_pip_install_e
t8_check_r8format_dependency
