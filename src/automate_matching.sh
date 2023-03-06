clear
echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *'
echo Will generate and analyze complete relations between $1 waveforms using $2 cores
echo '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *' 
printf "\n \n"

numCores=$2
numberEdges=$(( $1 * ($1 - 1)/2 ))
binSize=$(( $numberEdges / $2 ))

for i in `seq $2 0`
do
        if [ $inumberEdges % $i -eq 0 ]  
        then $numCores=$i
        fi
done

echo '* * * * * * * *' 
echo 'Will use $i cores'
echo '* * * * * * * *' 
printf "\n \n"

ifIt=$(($numberEdges % $numCores))
mult=$(($numberEdges / $numCores))

if let '$ifIt != 0'; then
        exit
fi

for i in `seq 1 $numCores`
do
        start=$(( ($i - 1) * $binSize))
        end=$(($i * $binSize))
        ./generate_matches.py -n $1 -f $start -t $end &
done

echo 'generate_matches.py complete'