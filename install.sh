#!/bin/sh

set -e  # Stop on error

# if [ $(uname) == "Linux" ]; then
    # echo "Detected Linux operating system!"
echo "Note: Currently this script only works Linux."
echo ''
echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED APPLICATIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ''
echo "debian or arch:"
read distro
if [ $distro = "debian" ]; then
    sudo apt install -y python3 python3-pip qbittorrent mpv vlc fzf
elif [ $distro = "arch" ]; then
    sudo pacman -Sy python3 python3-pip qbittorrent mpv vlc fzf
else
    echo "Invalid choice!"
    echo "Only debian and arch are implemented right now."
    echo "Assuming debian..."
    sudo apt install -y python3 python3-pip qbittorrent mpv vlc fzf
fi

echo ''
echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED PYTHON MODULES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ''
echo "Creating virtual environment /cine_env"
python3 -m venv cine_env
echo "Installing requirements..."
cine_env/bin/pip3 install -r requirements.txt
echo "Installing the cineterm module..."
cd .. && CineTerm/cine_env/bin/pip3 install -e CineTerm && cd CineTerm
echo ''
echo ">>>>>>>>>>>>>>>>> MAKING EXECUTABLE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ''
echo "Giving executable permissions..."
chmod +x $PWD/bin/cineterm
echo ''
echo "Shell currently in use:"
echo "Options: 'zsh', 'bash', 'fish'"
echo ''
read shell
if [ $shell = "zsh" ]; then
    echo "export PATH=$PWD/bin/:$PATH" >> ~/.zshrc
elif [ $shell = "bash" ]; then
    echo "export PATH=$PWD/bin/:$PATH" >> ~/.bashrc
elif [ $shell == "fish" ]; then
    echo "fish_add_path export PATH=$PWD/bin/:$PATH" >> ~/.config/fish/config.fish

else
    echo "Invalid option!"
fi

echo ">>>>>>>>>>>>>>>>>>>>>> DONE! >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo ''

