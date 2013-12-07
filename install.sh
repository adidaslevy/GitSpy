#!/bin/sh

# This script is used to install the client, and 3pps accompanied by it, as well as the config files

TMP=/tmp
LOG_LOC=/var/log/GitSpy/
CONF_LOC=~/

WORKING_DIR=`pwd`

ip=127.0.0.1
port=3006

########### MAIN ###########
#prepare dirs
[ -d $LOG_LOC ] || sudo mkdir -p $LOG_LOC
cp commitAggregations.xml $LOG_LOC

# install GitPython
which easy_install &>/dev/null

val=$?
if [ $val -ne 0 ]; then
    echo "easy_install is not installed, please refer to README.md, for client installation instructions"
    exit 1
fi

sudo easy_install -q GitPython &>/dev/null

val=$?
if [ $val -ne 0 ]; then
    echo "Failed to install GitPython"
    exit 1
fi

echo "Installing GitSpy Agent..."
# look for repository(ies) to inject GitSpy_agent

cd /
repos=`locate ".git" | grep -v "gitignore" | grep -v ".git/"`

cd $WORKING_DIR

for repo in $repos; do
	sudo cp GitSpy_client.py $repo/hooks
	sudo chmod 755 $repo/hooks/GitSpy_client.py

	# create agent config file
	repo_name=`echo $repo | sed -e s/.git//`
	echo "[repository]" 				> $repo/hooks/.GitSpy_agent.ini
	echo "repository_name=$repo_name" 	>> $repo/hooks/.GitSpy_agent.ini
	echo "" 							>> $repo/hooks/.GitSpy_agent.ini
	echo "[server]"						>> $repo/hooks/.GitSpy_agent.ini
	echo "ip=$ip"						>> $repo/hooks/.GitSpy_agent.ini
	echo "port=$port"					>> $repo/hooks/.GitSpy_agent.ini
	
	
	# prepare the post-commit hook
	[ -e $repo/hooks/post-commit ] || echo "#!/bin/sh" > $repo/hooks/post-commit
	grep "./GitSpy_client.py" $repo/hooks/post-commit
	val=$?
	if [ $val -ne 0 ]; then
		echo "./GitSpy_client.py" 		>> $repo/hooks/post-commit
		echo "exit 0" 					>> $repo/hooks/post-commit
	fi
	sudo chmod 755 $repo/hooks/post-commit

	# init the repo
	cd $repo/../
	sudo git init &>/dev/null
	cd $WORKING_DIR
done

echo "Finalizing installation..."


exit 0







