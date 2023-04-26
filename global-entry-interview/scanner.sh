#!/usr/bin/env bash

if [ "x$#" != "x1" ]
then
    echo "usage: $0 <location_id>"
    echo
    echo "example:"
    echo "  $0 5420"
    echo
    echo "note:"
    echo "  You can see the location ID on the website of Global Entry appointment scheduling with browser debugging tool."
    exit 1
fi

LOCATION_ID="$1"

function get_soonest_interview_time {
    API_URL="https://ttp.cbp.dhs.gov/schedulerapi/slots?orderBy=soonest&limit=1&locationId=$LOCATION_ID&minimum=1"
    curl -s "$API_URL" | jq -r '.[0].startTimestamp'
}

BASELINE_INTERVIEW_TIME=$(get_soonest_interview_time)
echo "Let's say the baseline interview time is $BASELINE_INTERVIEW_TIME."
echo "I'll let you know when there is a better interview time."
echo "If you can't hear me saying \"scanner started\", please turn up your volume."
say "scanner started"
while true
do
    INTERVIEW_TIME=$(get_soonest_interview_time)
    if [[ "$INTERVIEW_TIME" < "$BASELINE_INTERVIEW_TIME" ]]
    then
        echo "Congratulations! You can schedule an appointment at $INTERVIEW_TIME."
        while true
        do
            say "you can schedule an appointment at $INTERVIEW_TIME"
            sleep 1
        done
    fi

    sleep 60
done
