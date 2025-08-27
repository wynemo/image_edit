#!/bin/bash

set -e

IMAGE_NAME="wynemo/image-edit"


docker build --platform linux/amd64 -t $IMAGE_NAME .
docker push $IMAGE_NAME