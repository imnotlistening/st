#!/bin/bash
#
# Run some tests.
#

export PYTHONPATH=`pwd`

for t in `ls tests`; do
    echo "Execting test: $t"
    
    python tests/$t
done
