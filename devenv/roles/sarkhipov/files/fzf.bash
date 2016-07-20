# Setup fzf
# ---------
if [[ ! "$PATH" == */home/ubuntu/.fzf/bin* ]]; then
  export PATH="$PATH:/home/ubuntu/.fzf/bin"
fi

# Man path
# --------
if [[ ! "$MANPATH" == */home/ubuntu/.fzf/man* && -d "/home/ubuntu/.fzf/man" ]]; then
  export MANPATH="$MANPATH:/home/ubuntu/.fzf/man"
fi

# Auto-completion
# ---------------
[[ $- == *i* ]] && source "/home/ubuntu/.fzf/shell/completion.bash" 2> /dev/null

# Key bindings
# ------------
source "/home/ubuntu/.fzf/shell/key-bindings.bash"

