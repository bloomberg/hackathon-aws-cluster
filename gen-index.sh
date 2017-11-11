#!/bin/sh

cat <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Git Hackathon Cluster</title>
  </head>
  <body>
    <table>
EOF

for n in `seq $1 $2`
do
  cat <<EOF
<tr>
<th>User $n</th>
<td><a target="_blank" href="/user$n/shell">Shell</a></td>
</tr>
EOF
done

cat <<EOF
    </table>
  </body>
</html>
EOF
