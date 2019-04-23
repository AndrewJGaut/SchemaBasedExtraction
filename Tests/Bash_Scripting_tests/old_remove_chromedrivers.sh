
output=$(ps -A -o pid,command | grep chrome)

while read -r line;
do
	IFS='\s' read -ra words <<< "$IN"
	for i in "${ADDR[@]}"; do
		echo $i
	done
	echo $proc_id
done <<< $output



# proc_id=$(echo $IN | tr " ")

# echo $line
