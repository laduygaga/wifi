read -p "timeout= "  timeout
sed -i "s/option sessiontimeout.*$/option sessiontimeout '$timeout'/g" /etc/config/nodogsplash
/etc/init.d/nodogsplash restart
# sed -i "s/option sessiontimeout.*$/option sessiontimeout '$timeout'/g" nodogsplash
