#!/bin/sh

url="http://10.100.1.5"

login_url="$url/eportal/InterFace.do?method=login"
logout_url="$url/eportal/InterFace.do?method=logout"

useragent="just an agent"

# use python3 urllib.parse.quote_plus to encode first
campus="%E6%A0%A1%E5%9B%AD%E7%BD%91"           # 校园网
telecom="%E4%B8%AD%E5%9B%BD%E7%94%B5%E4%BF%A1" # 中国电信
mobile="%E4%B8%AD%E5%9B%BD%E7%A7%BB%E5%8A%A8"  # 中国移动
unicom="%E4%B8%AD%E5%9B%BD%E8%81%94%E9%80%9A"  # 中国联通

check() {
  response=$(curl -Ls --max-redirs 5 $url -H "User-Agent: $useragent" \
    --connect-timeout 5 --max-time 5 --retry 5 --retry-delay 0 --retry-max-time 10)

  if [ $? -ne 0 ]; then
    echo "error: can't connect to $url"
    exit 1
  fi

  count=$(echo "$response" | grep -Eic "top.self.location.href='(.*?)'")

  if [ "$count" -eq 1 ]; then
    redirect_url=$(echo "$response" | grep -Eio "top.self.location.href='(.*?)'" | grep -Eio "'(.*?)'" | sed "s/'//g")
    querystring=$(echo "$redirect_url" | cut -d "?" -f 2)
    return 0
  fi

  if [ "$count" -eq 0 ]; then
    echo "nothing to do, the network maybe connected"
    return 1
  else
    echo "error: more than one redirect url"
    exit 1
  fi
}

login() {
  curl -s "$login_url" \
    -H "User-Agent: $useragent" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "userId=$userId" \
    -d "password=$password" \
    -d "operatorPwd=" \
    -d "operatorUserId=" \
    -d "validcode=" \
    -d "passwordEncrypt=false" \
    --data-urlencode "queryString=$querystring" \
    --data-urlencode "service=$service" \
    --connect-timeout 5 --max-time 5 --retry 5 --retry-delay 0 --retry-max-time 10
  # -v --trace -

  if [ $? -ne 0 ]; then
    echo "error: login failed"
  fi
}

logout() {
  curl -s "$logout_url" -H "User-Agent: $useragent" -d "userIndex=" \
    --connect-timeout 5 --max-time 5 --retry 5 --retry-delay 0 --retry-max-time 10

  if [ $? -ne 0 ]; then
    echo "error: logout failed"
  fi
}

if [ "$1" = "-q" ]; then
  logout
  exit 0
fi

userId=$1
password=$2
service=$3

case $service in
"campus")
  service=$campus
  ;;

"telecom")
  service=$telecom
  ;;

"mobile")
  service=$mobile
  ;;

"unicom")
  service=$unicom
  ;;

*)
  echo "usage: $0 [userId] [password] [service] (start a loop check)"
  echo "usage: $0 -q (disconnect the network)"
  echo "service must be one of them (campus, telecom, mobile, unicom)"
  exit 1
  ;;
esac

os=$(uname -s)

if [ "$os" = "Darwin" ]; then
  sleep_ms=30
elif [ "$os" = "Linux" ]; then
  sleep_ms=30s
else
  echo "error: unsupported platform"
  exit 1
fi

while true; do
  if check; then
    login
  fi
  sleep $sleep_ms
done

exit 0
