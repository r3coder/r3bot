

/bin/sleep 5

source $HOME/.bashrc
source $HOME/.profile


tmux kill-session -t lostarkbot
/usr/bin/tmux new-session -d -s lostarkbot 

cd $HOME/lostarkbot

backup_dir=$(date +'%Y%m%d')
cp data/kakul/latest.save data/kakul/$backup_dir.save

#/usr/bin/tmux send-keys -t neos "docker container stop $(docker container ls -aq)" C-m
/usr/bin/tmux send-keys -t lostarkbot "cd ./lostarkbot" C-m
/usr/bin/tmux send-keys -t lostarkbot "docker container stop r3bot" C-m
/usr/bin/tmux send-keys -t lostarkbot "docker container rm r3bot" C-m
/usr/bin/tmux send-keys -t lostarkbot "docker run -it --user "$(id -u):$(id -g)" --name r3bot --workdir /app -v "$(pwd)":/app lb:latest python3 main.py" C-m
