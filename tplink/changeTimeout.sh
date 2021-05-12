#!/bin/sh
read -p "timeout= "  timeout
sed -i "s/option sessiontimeout.*$/option sessiontimeout '$timeout'/g" /etc/config/nodogsplash
sed -i "s/option authidletimeout.*$/option authidletimeout '$timeout'/g" /etc/config/nodogsplash
/etc/init.d/nodogsplash restart
