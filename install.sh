#!/bin/bash

DESTDIR="${HOME}/.config/wchanger"
echo "making $DESTDIR"
mkdir -p "$DESTDIR" 2>/dev/null
echo "coping files..."
chmod +x wchanger.sh
chmod +x wchanger-engine.sh
cp fetchOne.sh "$DESTDIR"
cp getW.sh "$DESTDIR"
cp wchangerDB.db "$DESTDIR"
cp wchangerDB.py "$DESTDIR"
cp wchanger-engine.sh "$DESTDIR"
cp wchanger.sh "$DESTDIR"
cp iter "$DESTDIR"
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
echo "downloading one wallpaper by id"
bash "$DESTDIR/wchanger.sh" d r25kqj >/dev/null 2>&1
echo "downloading one random wallpaper"
bash "$DESTDIR/wchanger.sh" dr >/dev/null 2>&1

echo "creating alias"
str="alias wchanger='"${HOME}"/.config/wchanger/wchanger.sh'"
[[ -f "${HOME}/.bashrc" ]] && echo "$str" >> "${HOME}/.bashrc"
[[ -f "${HOME}/.zshrc" ]] && echo "$str" >> "${HOME}/.zshrc"

$str

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


