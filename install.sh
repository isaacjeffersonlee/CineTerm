#!/bin/sh

if [ $(uname) != "Linux" ] 
then
    echo "Error: Operating System is not Linux!"
else
    echo "Detected Linux operating system!"
    echo "Note: Currently this script only works with debian based distros."
    echo ''
    echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED APPLICATIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo ''
    sudo apt install -y python python3-pip qbittorrent mpv vlc
    echo ''
    echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED PYTHON MODULES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo ''




fi

