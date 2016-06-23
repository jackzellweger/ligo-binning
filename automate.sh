clear

echo Will generate and analyze $1 waveforms with $2 bins using $3 cores

numberEdges=$(( $1 * ($1 - 1)/2 ))

binSize=$(( $numberEdges / $3 ))

if let '$numberEdges / $3'; then
  echo "$a is non-zero"
fi

./generate_matches.py -n $1

echo generate_matches.py complete

./bin_by_duration.py -n $1 -b $2

echo bin_by_duration.py complete

./bin_by_weight.py -n $1 -b $2

