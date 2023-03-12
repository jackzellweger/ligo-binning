clear

echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
echo Will generate and analyze $1 waveforms, binning them into $2 bins using $3 cores
numCores=$3
echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'

# Calculates number of edges in final graph
numberEdges=$(( $1 * ($1 - 1)/2 ))

# Calculates the bin
binSize=$(( $numberEdges / $3 ))

for i in `seq 20 0`
do
	if let '$numberEdges % i == 0'
		$numCores=
done

ifIt=$(($numberEdges % $3))
#mult=$(($numberEdges / $3))

if let '$ifIt != 0'; then
	exit
fi

for i in `seq 1 $3`
do
	start=$(( ($i - 1) * $binSize))
	end=$(($i * $binSize))
done

#./generate_matches.py --number $binSize --from $start --to $end

./generate_matches.py -n $1
echo generate_matches.py complete

./bin_by_duration.py -n $1 -b $2
echo bin_by_duration.py complete

./bin_by_weight.py -n $1 -b $2
echo bin_by_weight.py complete
