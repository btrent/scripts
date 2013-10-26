#!/usr/bin/env bash

# csv-bar-chart
#
# Generate a png bar chart from a csv file. The name for
# each bar is taking from the first column and its height
# from the second column. Other columns are ignored.
# Gnuplot does all the heavy lifting.

TITLE=""
XLABEL=0
YLABEL=1
WIDTH=600
HEIGHT=600
FILL="#6D929B"
# default font is awful, provide alternate true type font
TTF="/usr/share/fonts/truetype/msttcorefonts/verdana.ttf"

function usage {
  echo "
Usage: csv-bar-chart [csv]

Options:
  -title foo  : place title 'foo' at top of chart
  -xlabel     : include label on x axis
  -noylabel   : do not include label on y axis
  -width x    : set chart width to x pixels
  -height y   : set chart height to y pixels
  -fill color : set fill color (hex code or name)
  -ttf file   : use alternate true type font from file
"
  exit 2
}

# process arguments
while [ "$*" != "" ]; do
  case "$1" in
    "-title")
      shift
      TITLE="$1"
      ;;
    "-xlabel")
      XLABEL=1
      ;;
    "-noylabel")
      YLABEL=0
      ;;
    "-width")
      shift
      WIDTH="$1"
      ;;
    "-height")
      shift
      HEIGHT="$1"
      ;;
    "-fill"|"-color")
      shift
      FILL="$1"
      # ensure hex color codes start with a hash
      FILL=$(echo $FILL | sed 's/^\([0-9a-fA-F]*\)$/#\1/')
      ;;
    "-ttf")
      shift
      TTF="$1"
      ;;
    "-h"|"-help"|"--help")
      usage
      ;;
    *.csv)
      CSV="$1"
      ;;
    *)
      echo "Unrecognized option: '$1'"
      usage
      ;;
  esac
  shift
done

if [ "$CSV" = "" ]; then
  usage
fi

if [ ! -f "$CSV" ]; then
  echo "Error: cannot read '$CSV'"
  exit 1
fi

# compute output file name
PNG=$(echo $CSV | sed 's/csv$/png/')

# gnuplot does not scale y axis well, it leaves no space at top
# compute alternate ymax to leave 10% free space at top of chart
ymax=$(awk 'function num(x) { return x + 0 == x }
            BEGIN   { FS = "," }
            num($2) { if($2 > max) {max = $2} }
            END     { print 1.1 * max }' "$CSV")

if [ $XLABEL -ne 0 ]; then
  xlabel="set xlabel '$(head -n 1 "$CSV" | cut -d ',' -f 1)'"
else
  xlabel=""
fi

if [ $YLABEL -ne 0 ]; then
  ylabel="set ylabel '$(head -n 1 "$CSV" | cut -d ',' -f 2)'"
else
  ylabel=""
fi

# only try to use font if we can find it
if [ -f $TTF ]; then
  font="font '$TTF' 18"
else
  font=""
fi

if [ "$TITLE" != "" ]; then
  TITLE="set title '$TITLE'"
fi

# generate and execute gnuplot program
echo "
set terminal png enhanced $font size $WIDTH, $HEIGHT crop
set output '$PNG'

$TITLE
$xlabel
$ylabel

set datafile separator ','
set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set format y '%.0f'
set yrange [0:$ymax]
set xtic rotate by -60
unset key

plot '$CSV' using 2:xtic(1) title column linetype rgb '$FILL'
" | gnuplot