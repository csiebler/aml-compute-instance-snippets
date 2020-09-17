#!/bin/bash

set -e
(crontab -l 2>/dev/null; echo "*/5 * * * * python $PWD/shutdown_if_inactive.py") | crontab -
