#!/bin/bash

#
# Run all tests.
#

export PYTHONPATH=`pwd`

for t in `ls tests/*.py`; do
    echo "Execting test: $t"
    
    python tests/$t
done
