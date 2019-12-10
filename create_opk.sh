#!/usr/bin/env sh

set -e

if [ $# -eq 0 ]; then
  echo "Usage: $(basename $0) <additional files>"
  exit 1
fi

pushd "$(dirname $0)" >/dev/null

DATE=`date -r "$1" +%F`

mkdir -p output
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

echo "$DATE" > output/date.txt

OPK_FILE=output/rg350-installer-$DATE.opk
rm -f "$OPK_FILE"
mksquashfs output/default.gcw0.desktop opendingux.png output/date.txt *.py \
    $* "$OPK_FILE" -no-progress -noappend -comp gzip -all-root

popd >/dev/null
