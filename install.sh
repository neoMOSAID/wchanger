#!/bin/bash

if ! command -v feh >/dev/null 2>&1 ; then
    echo feh not installed. please install it
    exit
fi
if ! command -v jq >/dev/null 2>&1 ; then
    echo jq not installed. please install it
    exit
fi
if ! command -v dunst >/dev/null 2>&1 ; then
    echo dunst not installed. please install it
    exit
fi
if ! command -v zenity >/dev/null 2>&1 ; then
    echo zenity not installed. please install it
    exit
fi

pythonVersion=$(python -c 'import sys; print(sys.version_info.major)')
if (( $pythonVersion < 3 )) ; then
    echo please upgrade python to version 3 or above
    exit
fi

echo ">>> this will override existing files continue ?(y/n)"
IFS= read -rN 1 -p " : " c
[[ $c == "n" ]] && exit
echo

DESTDIR="${HOME}/.config/wchanger"
echo "making $DESTDIR"
mkdir -p "$DESTDIR" 2>/dev/null
echo "coping files..."
chmod +x wchanger.sh
chmod +x wchanger-engine.sh
cp -f fetchOne.sh "$DESTDIR" 2>/dev/null
cp -f getW.sh "$DESTDIR" 2>/dev/null
cp -f wchangerDB.db "$DESTDIR" 2>/dev/null
cp -f wchangerDB.py "$DESTDIR" 2>/dev/null
cp -f wchanger-engine.sh "$DESTDIR" 2>/dev/null
cp -f wchanger.sh "$DESTDIR" 2>/dev/null
cp -f iter "$DESTDIR" 2>/dev/null
while true ; do
echo "please enter a password to use for NSFW content"
read -rs -p "   > " pass
echo "
    user : wchanger
    pass : $pass

do you confirm ?(y/n)"
IFS= read -rN 1 -p " : " ans
[[ $ans == "y" ]] && break
done
echo
python "$DESTDIR/wchangerDB.py" addpass wchanger "$pass"
python "$DESTDIR/wchangerDB.py" wh_set expired 0

echo "downloading one wallpaper by id"
bash "$DESTDIR/wchanger.sh" d r25kqj >/dev/null 2>&1
echo "setting it to be second monitor background"
bash "$DESTDIR/wchanger.sh" ssp
python "$DESTDIR/wchangerDB.py" wh_set expired 0
echo "downloading one random wallpaper"
bash "$DESTDIR/wchanger.sh" dr >/dev/null 2>&1

echo "creating alias"
line="alias wchanger='"${HOME}"/.config/wchanger/wchanger.sh'"
file="${HOME}/.bashrc"
[[ -f "$file" ]] && {
    lno=$(\grep -nF "$line" "$file" | sed 's/:.*//' | tr '\n' ' ')
    [[ -z "$lno" ]] && echo "$line" >> "${HOME}/.bashrc"
}
file="${HOME}/.zshrc"
[[ -f "$file" ]] && {
    lno=$(\grep -nF "$line" "$file" | sed 's/:.*//' | tr '\n' ' ')
    [[ -z "$lno" ]] && echo "$line" >> "${HOME}/.bashrc"
}

$line

echo "======================================================"
echo "you're done. Enjoy!"
echo "you need to get an api key from wallhaven website"
echo "and save it in $DESTDIR/apikey"
echo "======================================================"

echo "[Unit]
Description=Wallpaper Changer for i3
Documentation=https://github.com/neoMOSAID/wchanger

[Service]
ExecStart=${HOME}/.config/wchanger/wchanger-engine.sh
PIDFile=/run/wchanger.pid
Restart=no

[Install]
WantedBy=default.target
" >| wchanger.service
printf '\033[1;32m'
echo "to make a systemd service:

    sudo cp wchanger.service /usr/lib/systemd/user/wchanger.service

to enable wchanger service:

    systemctl --user enable wchanger

to start wchanger service:
    systemctl --user start wchanger
"
