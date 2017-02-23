#!/bin/sh

cat <<EOF
ProxyPreserveHost On
ProxyRequests Off
ProxyVia On
EOF

for n in `seq $1 $2`
do
  cat <<EOF
ProxyPass "/student$n/shell" "http://192.168.$n.100:80"
ProxyPassReverse "/student$n/shell" "http://192.168.$n.100:80"
<Location "/student$n/jupyter">
    ProxyPass "http://192.168.$n.100:8080/student$n/jupyter"
    ProxyPassReverse "http://192.168.$n.100:8080/student$n/jupyter"
</Location>
<LocationMatch "/student$n/jupyter/(api/kernels/[^/]+/channels|terminals/websocket)(.*)">
    ProxyPassMatch "ws://192.168.$n.100:8080/student$n/jupyter/\$1\$2"
    ProxyPassReverse "ws://192.168.$n.100:8080/student$n/jupyter/\$1\$2"
</LocationMatch>
EOF
done
