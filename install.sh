#!/bin/sh

# TODO: Make this cleaner and better input and error checking
# TODO: Add MacOS support

set -e  # Stop on error

if [ "$(uname)" != "Linux" ]; then
    echo "Currently only linux is supported!"
else
    echo "Note: Currently this script only works Linux."
    echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED APPLICATIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    DISTRO=""
    while [ "$DISTRO" != "debian" ] && [ "$DISTRO" != "arch" ]
    do
        read -p "debian or arch: " DISTRO 
        if [ "$DISTRO" = "debian" ]; then
            sudo apt install -y qbittorrent mpv vlc fzf youtube-dl espeak
        elif [ "$DISTRO" = "arch" ]; then
            sudo pacman -Sy qbittorrent mpv vlc fzf youtube-dl espeakup
        else
            echo "Invalid choice!"
            echo "Only 'debian' and 'arch' are implemented right now."
        fi
    done

    echo ''
    echo ">>>>>>>>>>>>>>>>> INSTALLING REQUIRED PYTHON MODULES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "Installing requirements..."
    pip install -r requirements.txt
    echo "Installing the cineterm module..."
    cd .. && pip install -e CineTerm && cd CineTerm
    echo ''
    echo ">>>>>>>>>>>>>>>>> GIVE PERMISSIONS TO VPN ACTIVATOR >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    sudo chmod +x activate_vpn.sh
    echo ''
    echo ">>>>>>>>>>>>>>>>> CREATING CONFIG FILE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    DOWNLOAD_DIR=""
    while [ -z "$DOWNLOAD_DIR" ]
    do
        read -p "Download directory path: " DOWNLOAD_DIR 
        if [ -z "$DOWNLOAD_DIR" ]; then
            echo "Please enter a download directory path!"
        else
            echo "Will download movies to: $DOWNLOAD_DIR"
        fi
    done
    QB_USER=""
    while [ -z "$QB_USER" ]
    do
        read -p "qbittorrent web api username: " QB_USER 
        if [ -z "$QB_USER" ]; then
            echo "Please enter a username!"
        else
            echo "Setting qbittorrent username as $QB_USER"
        fi
    done
    QB_PASS=""
    while [ -z "$QB_PASS" ]
    do
        read -p "qbittorrent web api password: " QB_PASS 
        if [ -z "$QB_PASS" ]; then
            echo "Please enter a passowrd!"
        else
            echo "Setting qbittorrent password as $QB_PASS"
        fi
    done
    if [ -f "config.json" ]; then
        echo "config.json detected!"
    else
        touch config.json
        echo '{' >> config.json
        echo '    "qb_username": "'"$QB_USER"'",'>> config.json
        echo '    "qb_password": "'"$QB_PASS"'",'>> config.json
        echo '    "download_dir": "'"$DOWNLOAD_DIR"'"'>> config.json
        echo '}' >> config.json
        echo "Generating config.json..."
    fi
    echo ">>>>>>>>>>>>>>>>>>>>>> DONE! >>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    echo "You should now be able to run with python -m cineterm.app --options"
    echo "Where --options are:"
    python -m cineterm.app -h
fi
