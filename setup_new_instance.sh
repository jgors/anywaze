#----------------------------------------------------------------
# Author: Jason Gors <jasonDOTgorsATgmail>
# Creation Date: 01-26-2016
# Purpose: ON A FRESH INSTALL (eg. on master instance) install useful stuff.
#----------------------------------------------------------------

#######################################################
sudo apt-get update
sudo apt-get install git htop zsh tmux python-pip vim vim-gnome
pip install ipython --user --upgrade

cd ~
git clone https://github.com/jgors/configs.git ~/.configs
cd ~/.configs
sh ./new_repo.sh
echo "source ~/.zsh/zsh_cmds_under_version_control.zsh" >> ~/.zshrc

# need this b/c peagsus using .profile as default
echo "source ~/.profile" >> ~/.zshrc


#sudo apt-get install maven
#cd /usr/local/
#sudo git clone https://github.com/linkedin/camus.git
#sudo chown -R ubuntu camus
#cd ./camus/
#mvn clean package

