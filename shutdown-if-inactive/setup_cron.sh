#!/bin/bash
echo "Setting up cronjob for instance auto-shutdown"

# Get path to script
SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
echo "Current working dir: $PWD"
echo "Path to scripts: $SCRIPT_PATH"

# Get python path
PYTHON_PATH=`which python`
echo "Python Path: $PYTHON_PATH"

# Add cron to check every 5min if instance is inactive
echo "Current crontab:"
crontab -l

echo "Adding crontab entry for instance auto-shutdown"
(crontab -l 2>/dev/null; echo "*/1 * * * * $PYTHON_PATH $SCRIPT_PATH/shutdown_if_inactive.py > /tmp/shutdown.log 2>&1") | crontab -

echo "New crontab:"
crontab -l