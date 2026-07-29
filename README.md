# local-RED-dev
This project is the local development mono repository for RED


# how to clone this repo (with submodules)
git clone --recurse-submodules git@github.com:EhrenDavis12/local-RED-dev.git

If you already cloned without `--recurse-submodules`:
git submodule update --init --recursive

# how to create sub modules
git submodule add git@github.com:EhrenDavis12/Tic-Tac-Toe-Extreme.git src/Tic-Tac-Toe-Extreme