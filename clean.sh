#!/bin/bash

#
# Delete all the annoying files that I don't like.
#

find -type f -name *~ | rm -f
find -type f -name *.pyc | rm -f
