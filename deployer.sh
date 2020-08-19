#! /bin/sh

set -e

if [ "$4" = "" ]; then
  echo There should be 3 positional arguments
  echo "[role-name] [hcl-file-path] [deployer-url] [jwt]"
  exit 1
fi

ROLE=$1
JOB_HCL=$2
URL=$3
JWT=$4

echo Role Name: "$1"
echo Job HCL file: "$2"
echo URL: "$3"
echo JWT: Exists
echo


if [ "$(command -v curl > /dev/null; echo $?)" != "0" ]; then
  echo No curl detected. Please install curl
  exit 1
fi
if [ "$(command -v sed > /dev/null; echo $?)" != "0" ]; then
  echo No sed detected
  exit 1
fi

mkdir -p /tmp/nomad-deployer/

echo Preparing HCL...

sed -e "s/\"/\\\\\"/g" "$JOB_HCL" > /tmp/nomad-deployer/"$JOB_HCL"_1
sed -e ':a;N;$!ba;s/\n/\\n/g' < /tmp/nomad-deployer/"$JOB_HCL"_1 > /tmp/nomad-deployer/"$JOB_HCL"_2

PREPARED_HCL=/tmp/nomad-deployer/"$JOB_HCL"_2

echo
echo Prepared HCL:

cat "$PREPARED_HCL"
echo
echo Executing request...

CURL_RESPONSE_FILE=/tmp/nomad-deployer/curl.txt
curl --output "$CURL_RESPONSE_FILE" \
  --silent \
  --write-out "%{http_code}\n" \
  -H "Content-Type: application/json" \
  -d "{\"role\":\"$ROLE\",\"job_hcl\":\"$(cat "$PREPARED_HCL")\",\"jwt\":\"${JWT}\"}" \
  "$URL"
echo Response:
cat "$CURL_RESPONSE_FILE"
echo

case "$(cat "$CURL_RESPONSE_FILE")" in
    *"success"*)    echo Deploy success;   ;;
    *)              echo Deploy failed; exit 1;
esac

rm -rf /tmp/nomad-deployer/