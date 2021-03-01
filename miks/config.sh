#!/usr/bin/sh
read -p "Nhap router_id: " router_id
curl -s https://bizfly-wifi.ss-hn-1.bizflycloud.vn/Mikrotik/login.html -o ./login.html
sed -i "s/id123123456/$router_id/g" login.html
echo "SUCCESS"
