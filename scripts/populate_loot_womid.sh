#!/bin/bash

# Initialize the counter
count=0

# Loop to run the commands 3 times
while [ $count -lt 1 ]; do
    # First execution
    sudo mysql rngstreet -e "CALL rngstreet.populate_wom_id_for_loot();"
    sudo mysql rngstreet -e "CALL rngstreet.populate_wom_id_for_pbs();"
    sudo mysql rngstreet -e " delete from stg_loot where item_name like '%scythe%' and source='araxxor';"

    # Increment the counter
    count=$((count + 1))

    # Wait for 20 seconds before the next execution
    sleep 30
done
