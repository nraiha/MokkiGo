#!/usr/bin/env bash
export FLASK_APP=mokkigo
export FLASK_ENV=development

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
