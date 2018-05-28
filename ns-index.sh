#!/bin/bash
for year in {1995..2017}
do
	for month in {1..12}
	do
		printf "PARSING $year-$month\n"
		python3 ns/links.py --month $month --year $year --datum pridani 
	done
done