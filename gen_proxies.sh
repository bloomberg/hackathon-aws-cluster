#!/bin/sh

cat <<EOF
ProxyPreserveHost On
ProxyRequests Off
ProxyVia On
EOF

for n in `seq $1 $2`
do
  cat <<EOF
ProxyPass "/user$n/shell" "http://192.168.$n.100:80"
ProxyPassReverse "/user$n/shell" "http://192.168.$n.100:80"
EOF
done
