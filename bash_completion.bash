# This function allows tab completion on all the fragments in $PITZDIR.
_pitz_frags ()
{
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "`pitz-frags`" -- ${cur}) )
}

# Wire up a few scripts to use tab completion on fragments.
complete -o default -o nospace -F _pitz_frags pitz-show
complete -o default -o nospace -F _pitz_frags pitz-edit
complete -o default -o nospace -F _pitz_frags pitz-finish-task
complete -o default -o nospace -F _pitz_frags pitz-start-task
complete -o default -o nospace -F _pitz_frags pitz-abandon-task
complete -o default -o nospace -F _pitz_frags pitz-claim-task
complete -o default -o nospace -F _pitz_frags pitz-assign-task
complete -o default -o nospace -F _pitz_frags pitz-unassign-task
complete -o default -o nospace -F _pitz_frags pitz-prioritize-above
complete -o default -o nospace -F _pitz_frags pitz-prioritize-below
