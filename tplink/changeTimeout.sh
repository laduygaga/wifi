read -p "timeout= "  timeout
sed -i "s/option sessiontimeout.*$/option sessiontimeout '$timeout'/g" /etc/config/nodogsplash
# sed -i "s/option sessiontimeout.*$/option sessiontimeout '$timeout'/g" nodogsplash
