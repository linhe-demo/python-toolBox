#!/bin/bash

###
# Mutual exclusive execution
###
chushu=$1
yushu=$2

label="86bf265ccd81ea7f23b37c15f496dda7_${chushu}_${yushu}"
running=$(ps aux|grep $label|grep -v 'grep'|wc -l)
if [ "$running" -gt 2 ]; then
        echo "$(ps aux|grep $label|grep 'bash '|grep -v 'grep')"
        echo "already running $0  $label($running) $(date +'%Y-%m-%d %T')"
        exit 1
fi

WATERMARK_PATH='/var/job/jjshouse'
SRC_PATH='/opt/data1/jjsimg'
DEST_PATH='/mnt/data1/jjsimg/imgup'
LOG_PATH='/mnt/data1/jjsimg/imggen'

logname=img_$(date +%F_%H)
mkdir -p $LOG_PATH
upimglog="$LOG_PATH/${logname}.log"
updir=up_$(date +%F)
upimgdir="$DEST_PATH/${updir}"
mkdir -p ${upimgdir}

dbhost=
dbhost_ro=
dbname=
dbuser=
dbpass=

mysql_ro="mysql --skip-column-names --default-character-set=utf8 -h$dbhost_ro -u$dbuser -p$dbpass $dbname"
mysql="mysql --skip-column-names --default-character-set=utf8 -h$dbhost -u$dbuser -p$dbpass $dbname"
fetch_host=syncer@sjsmc.opvalue.com
fetch_port=32200


function fetch(){
    path=$(dirname $1)
    mkdir -p $path
    chown -R www-data.www-data $path
    rsync -az -K --progress -e "ssh -p$fetch_port" $fetch_host:$1 $1
}

function resize(){
    outsize=$1
    src=$2
    dest=$3
    thumb_name=$4

    rs=0
    if [ $outsize == '0' ] && [ "$src" != "$dest" ]; then
        cp -f "$src" "$dest"
    elif [ $outsize != '0' ]; then
        case "$thumb_name" in
            'm')
		echo thumb 'm'
                convert -interlace plane -quality 83 -resize $outsize -strip "${src}" "${dest}"
                ;;
            's380')
		echo thumb 's380'
                convert -interlace plane -quality 83 -resize $outsize -strip "${src}" "${dest}"
                ;;
            'o400')
                echo thumb 'o400'
                convert -interlace plane -quality 83 -resize $outsize -strip "${src}" "${dest}"
                ;;
            's400')
                echo thumb 's400'
                convert -interlace plane -quality 83 -resize $outsize -strip "${src}" "${dest}"
                ;;
            *)
                convert -resize $outsize -strip "${src}" "${dest}"
                ;;
        esac
        rs=$?
        if [ $rs -gt 0 ]; then
            echo "convert [-interlace plane -quality 83] -resize $outsize -strip \"$src\" \"$dest\"; # failed"
        fi
    fi
    return $rs
}

function prepare_logo(){
    watermark=$1
    thumb_name=$2
    src_x=$3
    src_y=$4

    rs=0
    if [ "$thumb_name" == 'x' ]; then
        #string watermark
        case $watermark in
            'jjshouse')
                site='JJsHouse';
                ;;
            'jenjenhouse')
                site='JenJenHouse';
                ;;
            'jennyjoseph')
                site='JennyJoseph';
                ;;
            'dressfirst')
                site='DressFirst';
                ;;
            'dressdepot')
                site='DressDepot';
                ;;
            'amormoda')
                site='AmorModa';
                ;;
            'vbridal')
                site='VBridal';
                ;;
            'loveprom')
                site='LoveProm';
                ;;
        esac
        echo "Copyright © ${site}.com Studio";
    else
		if [ ${src_x} -eq ${src_y} -a ${watermark} == "jjshouse" ]; then
            #logo watermark
			logo="$WATERMARK_PATH/gen/${watermark}-${src_x}-square.gen.png"
			if [ ! -f $logo ];then 
				mkdir -p "$WATERMARK_PATH/gen/"
				size='1500x1500';
				logo_src="$WATERMARK_PATH/${watermark}-${size}.png"
				resize ${src_x}x${src_y}^ "$logo_src" "$logo" 'logo'

				rs=$?
			fi
			echo $logo;
		else
		    #logo watermark
			logo="$WATERMARK_PATH/gen/${watermark}-${src_x}.gen.png"
			if [ ! -f $logo ];then 
				mkdir -p "$WATERMARK_PATH/gen/"
				size='1500x2055';
				logo_src="$WATERMARK_PATH/${watermark}-${size}.png"
				#resize $src_x "$logo_src" "$logo" 'logo'
				#echo "resize ${src_x}x${src_y}^ $logo_src $logo logo"
				resize ${src_x}x${src_y}^ "$logo_src" "$logo" 'logo'

				rs=$?
			fi
			echo $logo;
        fi
    fi
    return $rs
}

function mark(){
    logo=$1
    src=$2
    dest=$3

    if [ -n "$(echo $logo | grep 'Copyright ')" ]; then
        mogrify -pointsize 32 -fill white -weight bolder -gravity south -annotate -0+16 "$logo" "$dest"
    elif [ -n "$logo" ]; then
        composite -gravity center -geometry +0+0 $logo "$src" "$dest"
    fi
    echo $dest
}

function process(){
    watermark=$1
    img_type=$2
    thumb_name=$3
    width=$4
    height=$5
    src=$6
    dest=$7

    rs=0

    if [ ! -f "$src" ]; then
        fetch "$src"
        if [ ! -f "$src" ]; then
            echo "SRC $src not found."
            return 2;
        else
            echo "SRC $src fetched."
        fi
    fi

    format=$(identify "$src" | head -n 1 | awk '{print $2}')
    if [ "$format" == 'GIF' ]; then
        newsrc="${src}.gif2.jpg"
        if [ ! -f "$newsrc" ]; then
            convert "$src[0]" -background white -flatten -alpha off "$newsrc"
        fi
        src="$newsrc"
    fi


    if [ -n "$watermark" ]; then
        if [ "$img_type" == 'design' ]; then
            logo="${watermark}.design.png"
            composite -gravity center -geometry +0+0 $logo "$src" "$dest"
        else
            size=$(identify "$src" | head -n 1 | awk '{print $3}')
            x=$(echo $size|awk -F "x" '{print $1}')
            y=$(echo $size|awk -F "x" '{print $2}')
            logo=$(prepare_logo "$watermark" "$thumb_name" "$x" "$y")
	    echo "$logo   debug"
            if [ -f "$logo" ]; then
                cp "$src" "$dest"
                mark "$logo" "$dest" "$dest"
                if [ "$thumb_name" != 'o' ] && [ $width -ne 0 ]; then
                    #resize $width "$dest" "$dest" "$thumb_name"
                    resize ${width}\> "$dest" "$dest" $thumb_name
                    rs=$?
                fi
            else	
                echo "WARN: logo for $watermark $thumb_name $x $y : '$logo' not found."
            fi
        fi
    else
        if [ "$img_type" == 'video' ]; then
            cp "$src" "$dest"
            if [ $? -gt 0 ]; then ls -l "$src"; fi
        else
            case "$thumb_name" in
                'ls')
                    convert "$src" -thumbnail "x${height}>" -gravity center -extent ${width}x${height} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    ;;
                'rs')
                    convert "$src" -thumbnail ${width}x${height}^ -background gray -gravity North -extent ${width}x${height} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    ;;
                's400')
                    convert "$src" -interlace plane -quality 83 -resize ${width} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    ;;
                'o1140')
                    convert "$src"  -resize ${width} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    rs=$?
                    ;;
                'l')
                    convert "$src"  -resize ${width} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    rs=$?
                    ;;
                'r800')
                    convert "$src" -resize x${height} -size x${height} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    rs=$?
                    ;;
                 w*)
                    convert "$src"  -resize ${width} "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    rs=$?
                    ;;
                *)
                    convert "$src" -resize ${width}x${height}\> -size ${width}x${height} xc:white +swap -gravity North -composite "$dest"
                    if [ $? -gt 0 ]; then ls -l "$src"; fi
                    ;;
            esac
        fi
    fi
    return $rs
}

function process_thumb_row(){
    row=$1
    echo $row debug;
    goods_id=$(echo "$row"|awk -F"\t" '{print $2}')
    echo $goods_id|grep -E '^[0-9]+$' > /dev/null
    if [ $? -eq 0 ]; then
        goods_thumb_id=$(echo "$row"|awk -F"\t" '{print $1}')
        img_id=$(echo "$row"|awk -F"\t" '{print $3}')
        thumb_name=$(echo "$row"|awk -F"\t" '{print $4}')
        width=$(echo "$row"|awk -F"\t" '{print $5}')
        height=$(echo "$row"|awk -F"\t" '{print $6}')
        watermark=$(echo "$row"|awk -F"\t" '{print $7}'|tr "[A-Z]" "[a-z]")
        img_url=$(echo "$row"|awk -F"\t" '{print $8}')
        img_original=$(echo "$row"|awk -F"\t" '{print $9}')
        img_type=$(echo "$row"|awk -F"\t" '{print $10}')

	if [ "$img_type" = 'banner' ]; then
		echo 'escape processing banner'
		continue
	fi

        echo " goods_thumb_id: $goods_thumb_id"

        thumb=$img_url
        ori=$img_original

        ori_img="$SRC_PATH/$ori"

        if [ -n "$watermark" ]; then
            if [ "$watermark" = "jjshouse" -o "$watermark" = "jenjenhouse" -o "$watermark" = "jennyjoseph" -o "$watermark" = "amormoda" -o "$watermark" = "dressdepot" -o "$watermark" = "dressfirst" -o "$watermark" = "vbridal" -o "$watermark" = "loveprom" ]; then
                dst_img="${upimgdir}/$watermark/$thumb_name/$thumb"
            else
                echo "unkown $watermark";
                continue
            fi
        else
            dst_img="${upimgdir}/$thumb_name/$thumb"
        fi

        dst_dir=${dst_img%/*}
        echo $ori_img =\> $dst_img
        test -d "$dst_dir" || mkdir -p "$dst_dir"

        process "$watermark" "$img_type" "$thumb_name" "$width" "$height" "$ori_img" "$dst_img"
        rs=$?
	echo "process result: $rs"
        if [ $rs -ne 0 ]; then
            continue
        elif [ "$goods_thumb_id" -gt 0 -a -f "$dst_img" -a $(ls -s $dst_img|cut -d' ' -f1) -gt 1 ]; then
            cat <<SQL_END  | $mysql
UPDATE goods_thumb SET has_done = 1 WHERE goods_thumb_id = $goods_thumb_id AND has_done = 0 LIMIT 1
SQL_END
            chown www-data.www-data $dst_img
            echo $dst_img >> $upimglog
        fi
    else
        echo "ERROR: parsing goods_id from row"
        echo $row
    fi
}

function process_images(){
    limit=$1
    thread_count=$2
    thread_no=$3
    condition=$4

#    cat <<SQL_END  | $mysql_ro | while read row; do
#SELECT gt.goods_thumb_id, gt.goods_id, gt.img_id, gt.thumb_name, gt.width, gt.height, gt.watermark, gg.img_url, img_original, gg.img_type
#FROM goods_thumb gt
#INNER JOIN goods_gallery gg ON gt.img_id = gg.img_id  AND gg.img_type != 'banner'
#WHERE gt.has_done = 0
#AND goods_thumb_id % $thread_count = $thread_no
#AND gg.img_url <> ''
#AND gg.last_update_time > SUBDATE(NOW(),INTERVAL 20 DAY)
#$condition
#ORDER BY goods_thumb_id DESC
#SQL_END
    cat <<SQL_END  | $mysql_ro | while read row; do
SELECT gt.goods_thumb_id, gt.goods_id, gt.img_id, gt.thumb_name, gt.width, gt.height, gt.watermark, gg.img_url, img_original, gg.img_type
FROM goods_thumb gt
force index(last_update_time)
INNER JOIN goods_gallery gg ON gt.img_id = gg.img_id  AND gg.img_type != 'banner'
WHERE gt.has_done = 0
AND goods_thumb_id % $thread_count = $thread_no
AND gg.img_url <> ''
AND gt.last_update_time > SUBDATE(NOW(),INTERVAL 7 DAY)
$condition
ORDER BY goods_thumb_id DESC
LIMIT 10000
SQL_END
        if [ "$iii" = "" ]; then
                iii=0
        fi
        (( iii++ ))
        echo -n "[$iii] "
        process_thumb_row "$row"
	sleep 0.5
    done;
}

hour=$(date +%H)
cond=''

process_images 500 $chushu $yushu "$cond"


