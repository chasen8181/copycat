#!/bin/sh

[ "$EXEC_TOOL" ] || EXEC_TOOL=gosu
[ "$COPYCAT_HOST" ] || COPYCAT_HOST=0.0.0.0
[ "$COPYCAT_PORT" ] || COPYCAT_PORT=8080

set -e

echo "\
======================================
========= Welcome to CopyCat =========
======================================
"

copycat_command="python -m \
                  uvicorn \
                  main:app \
                  --app-dir server \
                  --host ${COPYCAT_HOST} \
                  --port ${COPYCAT_PORT} \
                  --proxy-headers \
                  --forwarded-allow-ips '*'"

if [ "$(id -u)" -eq 0 ] && [ "$(id -g)" -eq 0 ]; then
    echo Setting file permissions...
    chown -R ${PUID}:${PGID} ${COPYCAT_PATH}

    echo Starting CopyCat as user ${PUID}...
    exec ${EXEC_TOOL} ${PUID}:${PGID} ${copycat_command}
else
    echo "A user was set by docker, skipping file permission changes."
    echo Starting CopyCat as user "$(id -u)"...
    exec ${copycat_command}
fi
