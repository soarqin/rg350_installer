#!/usr/bin/env sh

set -e

if [ $# -eq 0 ]; then
  echo "Usage: $(basename $0) <config json file> <additional files>"
  exit 1
fi

pushd "$(dirname $0)" >/dev/null

DATE=`date +%F`

mkdir -p output
rm -f output/config.json output/date.txt output/default.gcw0.desktop
cat > output/default.gcw0.desktop <<EOF
[Desktop Entry]
Name=简体中文化安装器
Comment=简体中文化安装器 $DATE
Exec=python installer.py
Icon=opendingux
Terminal=false
Type=Application
StartupNotify=true
Categories=applications;
EOF

cp $1 output/config.json
echo "$DATE" > output/date.txt

OPK_FILE=output/rg350-installer-$DATE.opk
rm -f "$OPK_FILE"
shift
mksquashfs output/default.gcw0.desktop opendingux.png output/date.txt output/config.json *.py \
    $* "$OPK_FILE" -no-progress -noappend -comp gzip -all-root

popd >/dev/null
