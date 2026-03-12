#!/bin/sh

curl -f http://localhost:${COPYCAT_PORT}${COPYCAT_PATH_PREFIX}/health || exit 1
