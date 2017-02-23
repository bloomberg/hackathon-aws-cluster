#!/bin/sh

for n in `seq $1 $2`
do
  cat <<EOF
ProxyPass "/student$n/shell" "http://192.168.$n.100:80"
ProxyPassReverse "/student$n/shell" "http://192.168.$n.100:80"
<Location /student$n/jupyter>
    ProxyPass "http://192.168.$n.100:8080"
    ProxyPassReverse "http://192.168.$n.100:8080"
    ProxyHTMLEnable On
</Location>
EOF
done
