#!/usr/bin/env bash
export FLASK_APP=mokkigo
export FLASK_DEBUG=1

if [ "$#" -eq 0 ]; then
	echo "Usage:"
	echo "    init"
	echo "    run"
	exit 1
fi

while [[ $# -gt 0 ]]; do
	case $1 in
		init)
			flask init-db
			shift
			;;
		run)
			flask run
			shift
			;;
		*)
			exit
			shift
			;;
	esac
done
