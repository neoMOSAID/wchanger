#!/bin/bash
#
# this script downloads a single wallpaper
# by its id from wallhaven
# it requires the id (get it from wallhaven) as first argument
# example id : 5w6319

SCRIPTPATH="${HOME}/.config/wchanger"
wallhavenP="$SCRIPTPATH/wchangerDB.py"
wAPI="https://wallhaven.cc/api/v1"
wallhavenDIR="${HOME}/Pictures/wallhaven"

tmpfile="/tmp/getwallhaven_tmpfile"
logfile="/tmp/wchanger_wlog"
newFilePath="/tmp/wchanger_filePath"

rm -f "$newFilePath" 2>/dev/null


scriptname=$( basename "$0" )
is_running=$( pgrep  -f -c "$scriptname" )
if (( $is_running > 2 )) ; then
    >&2 echo $scriptname is running $is_running.
    exit 0
fi

ITERATION=$( cat "$SCRIPTPATH/iter" || echo 111)
APIKEY="$(cat "$SCRIPTPATH/apikey" )"
httpHeader="X-API-Key: $APIKEY"

[[ "$2" == "v" ]] && >&2 echo "fetching $1"
rm -f "$tmpfile" 2>/dev/null
wget -c -q -O "$tmpfile" --header="$httpHeader" "$wAPI/w/$1"

imgURL=$(jq -r ".data.path" "$tmpfile" )
imgNAME="$(basename "$imgURL")"
imgID=$(jq -r ".data.id" "$tmpfile" )
purity=$(jq -r ".data.purity" "$tmpfile" )

LOCATION="$wallhavenDIR/.ind/s-$ITERATION/fetched"

case "$purity" in
    sfw) mycategory=d
         LOCATION="$wallhavenDIR/d-$ITERATION/fetched/" ;;
    nsfw) mycategory=s ;;
    sketchy) mycategory=m ;;
esac

[[ ! -d "$LOCATION" ]] && mkdir -p "$LOCATION"
cd "$LOCATION" || exit

downloaded="$(python "$wallhavenP" downloaded "$imgID" )"
if (( $downloaded == 1 ))
    then
        FILE="$(python "$wallhavenP" get "$imgID" )"
        >&2 echo "::$FILE"
    else
        wget -c -q "$imgURL"
        if ! [[ -f "$PWD/$imgNAME" ]] ; then exit ; fi
        touch "$PWD/$imgNAME"
        echo "new" >| "$logfile"
        [[ "$2" == "v" ]] && >&2 echo "$imgNAME: new"
        python "$wallhavenP" add "$imgID" "${PWD##*/}" "$PWD/$imgNAME"
        python "$wallhavenP" fixcategory "$imgID" "$mycategory"
        FILE="$PWD/$imgNAME"
fi

dim=$( identify -format '%w  %h' "$FILE"  )
dim=( $dim )
python "$wallhavenP" adddim "$imgID" "${dim[0]}" "${dim[1]}"

echo "$FILE" > "$newFilePath"

[[ "$2" == "v" ]] && >&2 printf "\033[1;31mgetting tags...\033[0m\n"
l=$(jq -r ".data.tags|length" "$tmpfile")

[[ -z "$l" ]] && exit

for (( i=0 ; i< $l ; i++ )) ; do
    id=$(jq -r ".data.tags[$i].id" "$tmpfile")
    name=$(jq -r ".data.tags[$i].name" "$tmpfile" )
    alias=$(jq -r ".data.tags[$i].alias" "$tmpfile" )
    purity=$(jq -r ".data.tags[$i].purity" "$tmpfile" )
    case "$purity" in
        sfw) mycategory=d ;;
        nsfw) mycategory=s ;;
        sketchy) mycategory=m ;;
    esac
    [[ "$arg_4" == "verbose" ]] && >&2 echo "$name"
    python "$wallhavenP" createtag "$id" "$name" "$alias" "$mycategory"
    python "$wallhavenP" addwtag "$id" "$1"
    [[ "$2" == "v" ]] && >&2 echo "$name"
done
exit

