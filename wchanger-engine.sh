#!/bin/bash

scriptname=$( basename "$0" )
is_running=$( pgrep -cf "$scriptname" )
if (( $is_running > 1 )) ; then
  >&2 echo $scriptname is running.
  exit 0
fi

wallhavenP="${HOME}/.config/wchanger/wchangerDB.py"

function getws () {
    lastWS=$(cat /tmp/my_i3_ws 2>/dev/null )
    [[ -z "$lastWS" ]] && lastWS=0
    currWS=$(i3-msg -t get_workspaces \
                | jq -c '.[] |select(.focused)|.num' )
    if (( $lastWS != $currWS )) ; then
        echo "$currWS" > /tmp/my_i3_ws
        python "$wallhavenP" wh_set "expired" "0"
        return "$currWS"
    fi
    return 0  #same ws
}

ii=0
while true ; do
    getws
    index=$?
    if (( $currWS == 8 && $ii >= 7 )) \
       || (( $currWS == 10 && $ii >= 7 )) \
       || (( $currWS == 13 && $ii >= 7 )) \
       || (( $index != 0 )) \
       || (( $ii > 30 )) ; then
           bash "${HOME}/.config/wchanger/wchanger.sh" >/tmp/wchanger_wlog
           ii=0
    fi
    ii=$((ii+1))
    sleep 1
done

