#!/bin/sh

read -p "Nhap router_id: " router_id
opkg update
opkg install libustream-openssl
opkg install nodogsplash

wget --no-check-certificate https://bizfly-wifi.ss-hn-1.bizflycloud.vn/TP-Link/config/firewall
wget --no-check-certificate https://bizfly-wifi.ss-hn-1.bizflycloud.vn/TP-Link/config/network
wget --no-check-certificate https://bizfly-wifi.ss-hn-1.bizflycloud.vn/TP-Link/config/login.sh
wget --no-check-certificate https://bizfly-wifi.ss-hn-1.bizflycloud.vn/TP-Link/config/nodogsplash
wget --no-check-certificate https://bizfly-wifi.ss-hn-1.bizflycloud.vn/TP-Link/config/wireless
sed -i "s/id123123/$router_id/g" login.sh
chmod +x login.sh

cp -v network firewall nodogsplash wireless /etc/config/
cp  -v login.sh /usr/lib/nodogsplash/
/etc/init.d/nodogsplash restart

echo "SUCCESS!"
