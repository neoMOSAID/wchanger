# wchanger

Wallpaper changer for i3

# dependencies

feh : image viewer and backgrounder<br>
dunst: notification manager<br>
python<br>
the usual :awk,sed,grep,curl,wget...

# install

1 - run install.sh

    $./install.sh

2- to make a systemd service:

    sudo cp wchanger.service /usr/lib/systemd/user/wchanger.service

3- to enable wchanger service:

    systemctl --user enable wchanger

4- to start wchanger service:

    systemctl --user start wchanger

# help

multi layred wallpaper changer for i3wm
each workspace can have up to 9 states,
with two modes ( default and password protected mode)
features include (for each workspace ):

-   a single wallpaper<br>
-   a directory of wallpapers<br>
-   a list of favorites wallpapers<br>
-   wallpaper changing paused/unpaused<br>
-   list montage - ...<br>

          af|addfav              	add CW to favs
          al|addlist [name] [c]  	add list
          addld [title] [path]   	add local directory
          atw                    	add tag to CW
          c                      	CW path
          cl                     	CWs list
          cm                     	current mode
          cwt                    	CW tags
          chl [id] [name] [c]    	edit list name/category
          d|download [id]        	download image by wallhaven id
          dim                    	wallpaper dimensions
          dir                    	set local wallpapers directory
          fav                    	change favsList
          f|fix                  	change CW's category
          freeze                 	freeze on CW for all workspaces
          g [number]             	jump to wallpaper
          get                    	get
          h,help                 	print this help
          i|id                   	CW's wallhaven id
          info                   	info about current workspace states
          infoall                	info about all workspaces
          keys                   	i3 keyboard shortcuts
          l|list [o,l,number]    	a montage of the next 50 wallpapers
          lm                     	list of available modes
          o                      	open CW in feh
          ow                     	open CW in browser
          p                      	enable/disable wallpaper changing
          r|rf                   	remove from favs
          rwt                    	remove tag from CW
          rtt                    	remove tag from workspace tags list
          sdd                    	set wallhaven directory
          sdc                    	set directory category
          soc                    	set ordered category
          swc                    	set web category
          swi                    	set web search tag
          stt                    	add tag to workspace tags list
          stc                    	set workspace tags list category
          ssp                    	set CW as second Monitor wallpaper
          sp|setpause [number]   	set CW as pause
          sm|setmode [number]    	set mode for current workspace
          t|tags                 	list web search tags
          up|unsetpause          	unset pause wallpaper
          u|unexpire             	enable password mode
          url                    	wallhaven search url
          updatedb [scan]        	update database
          +,-,number             	next/prev wallpaper
          wlist [sdm]            	print favsLists names
          x                      	delete CW
          zoom                   	experimental not working
