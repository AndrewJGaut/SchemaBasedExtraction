
output=$(ps -A -o pid,command | grep chrome)

while read -r line;
do
	pid="$(cut -d' ' -f1 <<<"$line")"
#echo $A
	kill $pid
done <<< "$output"



# proc_id=$(echo $IN | tr " ")

# echo $line
