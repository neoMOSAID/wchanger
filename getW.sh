#!/bin/bash

SCRIPTPATH="${HOME}/.config/wchanger"
wallhavenP="$SCRIPTPATH/wchangerDB.py"
wAPI="https://wallhaven.cc/api/v1"
wallhavenDIR="${HOME}/Pictures/wallhaven"

tmpfile="/tmp/getwallhaven_tmpfile"
pageFile="/tmp/getwallhaven_tmpfile_page"
logfile="/tmp/wchanger_wlog"
newFilePath="/tmp/wchanger_filePath"

rm -f "$newFilePath" 2>/dev/null

scriptname=$( basename "$0" )
is_running=$( pgrep  -f -c "$scriptname" )
if (( $is_running > 2 )) ; then
    >&2 echo $scriptname is running $is_running.
    exit 0
fi

ITERATION=$( cat "$SCRIPTPATH/iter"||echo 111)
APIKEY="$(cat "$SCRIPTPATH/apikey" )"
httpHeader="X-API-Key: $APIKEY"

arg_1="$1"      #one,many
arg_2="$2"      #tag, squery
arg_3="$3"      #sdm
arg_4="$4"      #v for verbose
arg_5="$5"      #page

LOCATION="$wallhavenDIR/.ind/s-$ITERATION"
case "$arg_3" in
    d) FILTER=100
       LOCATION="$wallhavenDIR/d-$ITERATION" ;;
    m) FILTER=010 ;;
    s) FILTER=001 ;;
    sm|ms) FILTER=011 ;;
    sd|ds) FILTER=101 ;;
    dm|md) FILTER=110 ;;
    dsm|dms|mds|msd|smd|sdm) FILTER=111 ;;
esac

number='^[0-9]+$'
if [[ "$arg_2" =~ $number ]]
    then squery="id:$arg_2"
    else squery="$arg_2"
fi

LOCATION+="/$arg_2"
[[ ! -d "$LOCATION" ]] && mkdir -p "$LOCATION"
cd "$LOCATION" || exit

echo "downloading to $LOCATION"

function gettags(){
    rm -f "${tmpfile}_$1" 2>/dev/null
    wget -c -q -O "${tmpfile}_$1" --header="$httpHeader" "$wAPI/w/$1"

    [[ "$arg_4" == "v" ]] && >&2 printf "\033[1;31mgetting $1 tags...\033[0m\n"
    l=$(jq -r ".data.tags|length" "${tmpfile}_$1")

    [[ -z "$l" ]] && return

    for (( i=0 ; i< $l ; i++ )) ; do
        id=$(jq -r ".data.tags[$i].id" "${tmpfile}_$1")
        name=$(jq -r ".data.tags[$i].name" "${tmpfile}_$1" )
        alias=$(jq -r ".data.tags[$i].alias" "${tmpfile}_$1" )
        purity=$(jq -r ".data.tags[$i].purity" "${tmpfile}_$1" )
        case "$purity" in
            sfw) mycategory=d ;;
            nsfw) mycategory=s ;;
            sketchy) mycategory=m ;;
        esac
        python "$wallhavenP" createtag "$id" "$name" "$alias" "$mycategory"
        python "$wallhavenP" addwtag "$id" "$1"
        [[ "$arg_4" == "v" ]] && >&2 echo "$name"
    done
}

function downloadit_f(){
    wget -c -q "$imgURL"
    if [[ -f "$PWD/$imgNAME" ]] ; then
        touch "$PWD/$imgNAME"
        echo "$PWD/$imgNAME"
        [[ "$arg_4" == "v" ]] && >&2 echo "$imgNAME: new"
    fi
    dim=$( identify -format '%w  %h' "$PWD/$imgNAME"  )
    dim=( $dim )
    python "$wallhavenP" add "$imgID" "${PWD##*/}" "$PWD/$imgNAME"
    python "$wallhavenP" adddim "$imgID" "${dim[0]}" "${dim[1]}"
    echo "new" >| "$logfile"
    case "$purity" in
        sfw) mycategory=d ;;
        nsfw) mycategory=s ;;
        sketchy) mycategory=m ;;
    esac
    python "$wallhavenP" fixcategory "$imgID" "$mycategory"
}

function getFile_f(){
    downloaded="$(python "$wallhavenP" downloaded "$imgID" )"
    if (( $downloaded == 1 ))
        then
            FILE="$(python "$wallhavenP" get "$imgID" )"
            printf "# "
        else
            FILE=$(downloadit_f)
    fi
    echo "$FILE"
}


[[ "$arg_1" == one ]] && {

    s1="search?page=1&categories=101&purity=$FILTER&"
    s1+="sorting=random&order=desc&q=$squery"

    rm -f "$pageFile" 2>/dev/null
    wget -c -q -O "$pageFile" --header="$httpHeader" "$wAPI/$s1"

    imgURL=$(jq -r ".data[0].path" "$pageFile" )
    imgID=$(jq -r ".data[0].id" "$pageFile" )
    purity=$(jq -r ".data[0].purity" "$pageFile" )
    imgNAME="$(basename "$imgURL")"
    FILE=$(getFile_f)
    echo "$FILE" > "$newFilePath"
    gettags "$imgID"
    exit
}

FIRST=1
s1="search?page=$FIRST&categories=101&purity=$FILTER&"
s1+="sorting=date_added&order=desc&q=$squery"

rm -f "$pageFile" 2>/dev/null
wget -c -q -O "$pageFile" --header="$httpHeader" "$wAPI/$s1"

lastpage=$(jq -r ".meta.last_page" "$pageFile" )
if [[ -z "$arg_5" ]] ; then
    FIRST=1
fi
FIRST=1
for (( i=$FIRST ; i<=$lastpage ; i++ )) ; do
    s1="search?page=$i&categories=101&purity=$FILTER&"
    s1+="sorting=date_added&order=desc&q=$squery"
    echo "page $i/$lastpage"
    rm -f "$pageFile" 2>/dev/null
    wget -c -q -O "$pageFile" --header="$httpHeader" "$wAPI/$s1"
    N=$(jq -r ".data|length" "$pageFile" )
    [[ -z "$N" ]] && continue
    for (( j=0 ; j < $N ; j++ )) ; do
        echo "      $((j+1))/$N"
        echo -en "\e[1A"
        imgURL=$(jq -r ".data[$j].path" "$pageFile" )
        imgID=$(jq -r ".data[$j].id" "$pageFile" )
        purity=$(jq -r ".data[$j].purity" "$pageFile" )
        imgNAME="$(basename "$imgURL")"
        getFile_f
        gettags "$imgID"
        wait
    done
    echo
done


