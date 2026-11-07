# Load the user's usual interactive Bash configuration, then select this
# project's learning environment. Bash reads this file via --rcfile.
if [[ -r "$HOME/.bashrc" ]]; then
    source "$HOME/.bashrc"
fi

source /home/m/miniconda3/etc/profile.d/conda.sh
conda activate /home/m/miniconda3/envs/embodied-learn
