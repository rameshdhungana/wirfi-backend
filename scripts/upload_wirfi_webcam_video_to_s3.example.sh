#!/bin/bash
DIR="/tmp"

inotifywait --monitor --event close_write,moved_to --format '%w%f' "${DIR}" |
    while read path action file; do
        echo "The file '$path$file' appeared in directory via '$action' action"
        file_path=${path}${file}

        echo "upload $file_path to S3"
        aws s3 cp ${file_path} s3://wirfi-webcam-video/
    done
