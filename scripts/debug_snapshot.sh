#!/bin/bash
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
set -eu -o pipefail

COMPOSE_FILE="$(pwd)/docker-compose.yml"

while getopts "hp:f:" opt; do
  case $opt in
    h)
      echo "Collect debug snapshot"
      echo ""
      echo "This snapshot includes:"
      echo "  - backup of the database"
      echo "  - logs from all services"
      echo "  - config.yaml"
      echo ""
      echo "Snapshot will be collected in /tmp. If you want to redefine, set TMPDIR."
      echo ""
      echo "${0} [-p projectname] [-f /path/to/docker-compose.yml] /path/to/snapshot" >&2
      exit 0
      ;;
    p)
      PROJECT_NAME="${OPTARG:-}"
      ;;
    f)
      COMPOSE_FILE="${OPTARG:-}"
      ;;
    \?)
      exit 1
      ;;
  esac
done

shift $((OPTIND - 1))
if [ $# -eq 0 ]; then
    echo "You need to supply path to the final snapshot."
    exit 1
fi

COMPOSE_FILE="$(readlink -f "$COMPOSE_FILE")"
PROJECT_NAME="${PROJECT_NAME:-${COMPOSE_PROJECT_NAME:-$(basename "$(dirname "$COMPOSE_FILE")")}}"
COMPOSE_CMD="docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME"

backup_dir="$(mktemp -d)"
rm_backup_dir() {
    rm -rf "$backup_dir"
}
trap rm_backup_dir EXIT

for service_name in $($COMPOSE_CMD config --services)
do
    service_dir="$backup_dir/$service_name"
    service_id="$($COMPOSE_CMD ps -q "$service_name")"
    mkdir -p "$service_dir"

    echo "Collect data from service $service_name"
    docker cp "$service_id:/etc/decapod/config.yaml" "$service_dir" >/dev/null 2>&1 || true
    docker cp "$service_id:/etc/git-release" "$service_dir" >/dev/null 2>&1 || true
    docker cp "$service_id:/etc/decapod-release" "$service_dir" >/dev/null 2>&1 || true
    docker cp "$service_id:/packages-npm" "$service_dir" >/dev/null 2>&1 || true
    docker cp "$service_id:/packages-python2" "$service_dir" >/dev/null 2>&1 || true
    docker cp "$service_id:/packages-python3" "$service_dir" >/dev/null 2>&1 || true
    $COMPOSE_CMD logs --no-color -t "$service_name" > "$service_dir/log"
    $COMPOSE_CMD exec -T "$service_name" date +%s 2>/dev/null > "$service_dir/unix_timestamp" || true
    $COMPOSE_CMD exec -T "$service_name" date 2>/dev/null > "$service_dir/date" || true
    $COMPOSE_CMD exec -T "$service_name" dpkg -l 2>/dev/null > "$service_dir/packages-os" || true
    docker inspect --type container "$service_id" 2>/dev/null > "$service_dir/docker-inspect" || true
done

echo "Collect information about docker"
docker info 2>/dev/null > "$backup_dir/docker-info"

echo "Collect docker-compose.yml"
$COMPOSE_CMD config > "$backup_dir/docker-compose.yml"

echo "Collect all logs"
$COMPOSE_CMD logs --no-color -t > "$backup_dir/all_logs"

echo "Collect backup"
$COMPOSE_CMD exec -T admin decapod-admin db backup > "$backup_dir/db_backup"

echo "Collect monitoring results"
docker cp "$($COMPOSE_CMD ps -q admin):/www/monitoring" "$backup_dir/ceph-monitoring"

echo "Create archive with snapshot"
tar -C "$(dirname "$backup_dir")" --transform "s?^$(basename "$backup_dir")?snapshot?" -cJf "$1" "$(basename "$backup_dir")"
