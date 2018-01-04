#!/bin/bash

#
# Run a single test.
#

# We expect this to be run from the top level directory! If not then it's
# not going to work - the tests won't find the modules!
export PYTHONPATH=`pwd`/pysrc

test=$1
shift

if [ "x$test" == "x" ]; then
    echo 'Missing test argument! Uasge:'
    echo
    echo '  $0 <st_test>'
    echo
    echo 'Where <st_test> is a test under tests/'
    echo
    echo 'For example: ./run_test.sh ./tests/asset_test.py'
    exit
fi

echo Running test: $test

python ./$test $*
