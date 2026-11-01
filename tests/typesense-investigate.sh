#!/bin/bash
# v99 (Nov 1 2026): collect the exit-139 evidence before changing Typesense's image/config.
# Run only with the owner's approval: starts the existing service; does not replace/delete data.
set -u
cd "$(dirname "$0")/.." || exit 1
report="$PWD/assets/logs/typesense-investigation-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$report"
docker inspect devsvc-typesense --format 'image={{.Config.Image}} image_id={{.Image}} state={{json .State}} memory={{.HostConfig.Memory}} nano_cpus={{.HostConfig.NanoCpus}} cpuset={{.HostConfig.CpusetCpus}} pids_limit={{.HostConfig.PidsLimit}} shm={{.HostConfig.ShmSize}} mounts={{json .Mounts}}' > "$report/before.txt" || exit 1
image_id=$(docker inspect devsvc-typesense --format '{{.Image}}') || exit 1
docker image inspect "$image_id" --format 'id={{.Id}} digests={{json .RepoDigests}} architecture={{.Architecture}} os={{.Os}} entrypoint={{json .Config.Entrypoint}} cmd={{json .Config.Cmd}} labels={{json .Config.Labels}}' > "$report/image.txt" || exit 1
{ uname -a; lscpu; free -m; df -h .; } > "$report/host.txt"
docker logs --timestamps devsvc-typesense > "$report/before.log" 2>&1
devsvc up typesense > "$report/start.output" 2>&1
rc=$?
printf 'devsvc up typesense exit=%s\n' "$rc" > "$report/result.txt"
docker logs --timestamps devsvc-typesense > "$report/after.log" 2>&1
docker inspect devsvc-typesense --format 'state={{json .State}} memory={{.HostConfig.Memory}} restart={{.HostConfig.RestartPolicy.Name}}' > "$report/after.txt"
printf 'Typesense evidence: %s (start exit %s)\n' "$report" "$rc"
exit "$rc"
