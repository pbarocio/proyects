#SCRIPT PARA MONITOREAR ENLACE DE LAS 5 SUCURSALES Y CREAR UNA TABLA DE STATUS
#set -x #Activar debugging
#Directorio de logs
LOGDIR="$HOME/logs/Monitoreo-Enlaces"
mkdir -p "$LOGDIR"

#Se extrae la fecha
FECHA=$(date +%Y-%m-%d)
#Se extrae el día de la semana
DIA=$(date +%A)

#Se crea el CSV dónde se llevarán los registros de la ejecución por día
HISTORICO="$LOGDIR/historico-$(date +%Y-%m-%d-%A).csv"

#Se crea el CSV dónde se llevarán el registros del estado actual de cada enlace (Se sobreescribe cada ejecución)
ESTADO_ACTUAL=$LOGDIR/Estado-actual.csv
#> $ESTADO_ACTUAL # Faltaba definir la lógica cuándo una sucursal estaba caída por eso lo comenté

#Validar sí existe el archivo del Contador de ejecuciones, sí no existe inicializarlo en 1
if [ ! -f "/tmp/excec-mon-link.txt" ]; then
    echo "1" > /tmp/excec-mon-link.txt
fi

#=======================================================
# ARRANQUE EN FRÍO - SSOT (SINGLE SOURCE OF TRUTH)
#=======================================================
declare -A SSOT

SSOT["CORPORATIVO,TELMEX-1"]="As,8.8.8.8,1"
SSOT["CORPORATIVO,TELMEX-2"]="s,8.8.4.4,2"
SSOT["CORPORATIVO,TELMEX-3"]="s,1.1.1.1,3"
SSOT["CORPORATIVO,TELCEL"]="Is,1.0.0.1,4"

SSOT["PENJAMO,TELMEX-1"]="As,8.8.8.8,1"
SSOT["PENJAMO,TELMEX-2"]="s,8.8.4.4,2"
#SSOT["PENJAMO,TELCEL"]="Is,1.1.1.1,3"

SSOT["LA-PIEDAD,TELMEX-1"]="As,8.8.8.8,1"
SSOT["LA-PIEDAD,TELMEX-2"]="s,8.8.4.4,2"
#SSOT["LA-PIEDAD,TELCEL"]="Is,1.1.1.1,3"

SSOT["MORELIA,TELMEX-1"]="As,8.8.8.8,1"
SSOT["MORELIA,TELMEX-2"]="s,8.8.4.4,2"
#SSOT["MORELIA,TELCEL"]="Is,1.1.1.1,3"

SSOT["PONCITLAN,TELMEX-1"]="As,8.8.8.8,1"
SSOT["PONCITLAN,TELMEX-2"]="s,8.8.4.4,2"
#SSOT["PONCITLAN,TELCEL"]="Is,1.1.1.1,3"

#Declarar la variable $CONTADOR
CONTADOR=$(cat /tmp/excec-mon-link.txt)

#Valida sí el archivo que contiene las ejecuciones está vacío sí no lo crea y escribe encabezados
if [ ! -f "$HISTORICO" ]; then
    echo "Fecha,Hora,Día,Sucursal,Enlace,Ruta,Distancia,Bandera,Num exec" > $HISTORICO
fi

#Declaración de arrays asociativos, el estado previo y el control de los timestamps (Separados porque tienen funciones lógicas diferentes)
declare -A ESTADO_PREVIO   # array asociativo para guardar el estado anterior (flag)
declare -A TS_PREVIO       # array asociativo para guardar el timestamp de caída anterior

#Llenar los arrays con el archivo Estado-actual.csv
if [ -f "$ESTADO_ACTUAL" ]; then
    while IFS=',' read -r suc enlace gateway dist flag ts; do
        # Si la primera palabra de la línea es "sucursal", es el encabezado, la saltamos
        if [[ "$suc" == "sucursal" ]]; then
            continue
        fi
        # Construimos la clave única (sucursal, enlace)
        clave="$suc,$enlace"
        # Guardamos el estado (flag) en el array ESTADO_PREVIO
        ESTADO_PREVIO["$clave"]="$flag"
        # Si el campo ts (timestamp) no está vacío, lo guardamos en TS_PREVIO
        if [ -n "$ts" ]; then
            TS_PREVIO["$clave"]="$ts"
        fi
        # Opcional: mostrar en pantalla lo que se cargó (para depuración)
        # echo "Cargado: $clave -> $flag (ts: $ts)"
    done < "$ESTADO_ACTUAL"
fi

# echo "================================ CONTENIDO DE ESTADO_PREVIO ===================="
# for llave in "${!ESTADO_PREVIO[@]}"; do
#     echo "Lo que trae eahorita ESTADO_PREVIO[$llave]: "${ESTADO_PREVIO["$llave"]}""
#     # if [[ "$llave" == "$SUCURSAL,"* ]]; then
#     #     link=$(echo $llave | cut -d',' -f2)
#     #     echo "Llave : $llave"
#     #     echo "Link: $link"
#     #     echo "Lo que trae el arreglo ahorita: {$ESTADO_PREVIO["$llave"]}"
#     # fi
# done

# echo "================================ ***ESTADO PREVIO*** ===================="
# echo "---"

# echo "================================ CONTENIDO DE TS_PREVIO ===================="
# for llave in "${!TS_PREVIO[@]}"; do
#     echo "Lo que trae eahorita TS_PREVIO[$llave]: "${TS_PREVIO["$llave"]}""
# done
# echo "================================ ***TS_PREVIO*** ===================="
# echo "---"

> $ESTADO_ACTUAL

#Datos de la PC o Servidor
PUERTO=2233
NOMBRE_LLAVE=id_agrocisa_monitoreo
USUARIO=Monitoreo
IPS=(10.147.17.1 10.147.17.2 10.147.17.3 10.147.17.4 10.147.17.5)
SUCURSALES=(CORPORATIVO PENJAMO LA-PIEDAD MORELIA PONCITLAN)
#awk 'NR>4 && !/^;/'

#Se crea el ciclo para iterar sobre el array de $SUCURSALES e $IPS
for i in "${!SUCURSALES[@]}"; do
    SUCURSAL="${SUCURSALES[i]}"
    IP="${IPS[i]}"

    #Crea un archivo intermedio para escribir el resultado del comando en el router, sí se escribe en arrays o variables no respeta la estructura
    TMP_FILE="/tmp/interfaces_$SUCURSAL.txt"
    > $TMP_FILE
    #Conexión por terminal al router con los parámetros definidos anteriormente
    /usr/bin/ssh -o ConnectTimeout=15 -p $PUERTO -i $HOME/.ssh/$NOMBRE_LLAVE $USUARIO@$IP "/ip route print where dst-address=0.0.0.0/0" | awk 'NR>3' | tr -d '\r' > $TMP_FILE
    sleep 2

    if grep -q "No route to host" "$TMP_FILE" || [ ! -s "$TMP_FILE" ]; then
        echo "***********************************"
        echo "* ¡¡¡ $SUCURSAL ESTÁ CAÍDO !!!      *"
        echo "***********************************"
        echo ""
        hora=$(date "+%H:%M:%S")

        for llave in "${!SSOT[@]}"; do
            if [[ "$llave" == "$SUCURSAL,"* ]]; then #Ése if es para comparar sí la llave contiene texto relacionado a la variable $SUCURSAL
                link=$(echo $llave | cut -d',' -f2)
                flag=$(echo "${SSOT[$llave]}" | cut -d',' -f1)
                gateway=$(echo "${SSOT[$llave]}" | cut -d',' -f2)
                distance=$(echo "${SSOT[$llave]}" | cut -d',' -f3)
                ts_actual=$(date +%s)
                echo "-------------------------"
                echo "ENLACE:   | $link     |"
                echo "-------------------------"
                echo "GATEWAY   | $gateway     |"
                echo "-------------------------"
                echo "DISTANCIA | $distance          |"
                echo "-------------------------"
                echo "ESTADO:   |   Is        |"
                echo "------------------------"
                #Valida que el timpestamp venga vaciío o sea que no hay registro
                if [ -z "${TS_PREVIO[$SUCURSAL,$link]}" ]; then
                    ts_original=$(date +%s)
                    echo "=================================================="
                    echo " *REGISTRANDO CAÍDA DE $link : $ts_original ...  |"
                    echo "=================================================="
                    echo "$SUCURSAL,$link,$gateway,$distance,Is,$ts_original" >> $ESTADO_ACTUAL
                else
                    ts_original="${TS_PREVIO[$SUCURSAL,$link]}"
                    echo ""
                    echo "====================================================================="
                    echo " *SE REGISTRÓ LA CAÍDA DE $link en $SUCURSAL, HACE $(((ts_actual - ts_original) / 60 )) MINUTOS!!!  |"
                    echo "====================================================================="
                    if (( (ts_actual - ts_original) > 1200  && (ts_actual - ts_original) <= 1440 )); then
                        #Se envía alerta de Telegram
                        #/usr/bin/curl -s -X POST "https://api.telegram.org/bot/sendMessage" -d chat_id="" -d text="¡¡ALERTA!! el enlace $link de $SUCURSAL está caído, vas a tener qué levantar un ticket :S" > /dev/null 2>&1
                    fi
                    echo "$SUCURSAL,$link,$gateway,$distance,Is,$ts_original" >> $ESTADO_ACTUAL
                fi

                echo "$FECHA,$hora,$DIA,$SUCURSAL,$link,$gateway,$distance,Is,$CONTADOR" >> $HISTORICO
            fi
        done
    else
        echo "***********************************"
        echo "* SUCURSAL $SUCURSAL             *"
        echo "***********************************"
        #Iteramos el archivo intermedio para extraer datos
        while read -r line; do
            #Se eliminan los retornos de línea qué contiene el archivo
            line=$(echo "$line" | tr -d '\r' )

            #Valida sí el registro está vació y sí lo está lo ignora y continúa
            if [[ -z "$line" ]]; then
                continue
            fi
            #Se valida sí el archivo comienza con ;;; para saber que es un comentario y así sacamos el nombre del enlace
            if [[ $line == ";;;"* ]]; then
                #Se eliminan las ;;; con sed
                link=$(echo "$line" | sed 's/^;;; //')
                echo "--------------------------"
                echo "ENLACE:   |   $link    |"
            else
                gateway=$(echo "$line" | awk '{print $4}')
                distance=$(echo "$line" | awk '{print $NF}')

                echo "--------------------------"
                echo "GATEWAY   |   $gateway     |"
                echo "--------------------------"
                echo "DISTANCIA |   $distance           |"
                echo "--------------------------"

                hora=$(date "+%H:%M:%S")
                
                flag=$(echo "$line" | awk '{print $2}')
                # Se valida sí el enlace actual está caído
                ts=$(date +%s)
                if [ $flag = "Is" ]; then
                    echo "ESTADO:   |   $flag          |"
                    echo "--------------------------"
                    if [ -z "${TS_PREVIO[$SUCURSAL,$link]}" ]; then
                        ts_original=$(date +%s)
                        echo "==============================================="
                        echo " *REGISTRANDO CAÍDA DE $link: $ts_original ...  |"
                        echo "==============================================="
                        #Escribimos el archivo agregando contenido cuándo tenemos las variables definidas con el timestamp
                        echo "$FECHA,$hora,$DIA,$SUCURSAL,$link,$gateway,$distance,$flag,$CONTADOR" >> $HISTORICO
                        #Escribimos el archivo Estado-actual.csv contenido cuándo tenemos las variables definidas
                        echo "$SUCURSAL,$link,$gateway,$distance,$flag,$ts_original" >> $ESTADO_ACTUAL
                    else
                        ts_original="${TS_PREVIO[$SUCURSAL,$link]}"
                        ts_actual=$(date +%s)
                        if (( (ts_actual - ts_original) > 1200  && (ts_actual - ts_original) <= 1440 )); then
                            #Se envía alerta de Telegram
                            #/usr/bin/curl -s -X POST "https://api.telegram.org/bot/sendMessage" -d chat_id="" -d text="¡¡ALERTA!! el enlace $link de $SUCURSAL está caído, vas a tener qué levantar un ticket :S" > /dev/null 2>&1
                        fi

                        echo ""
                        echo "===================================================="
                        echo " *SE REGISTRÓ LA CAÍDA DE $link, HACE $(((ts_actual - ts_original) / 60 )) MINUTOS |"
                        echo "===================================================="
                        #Escribimos el archivo agregando contenido cuándo tenemos las variables definidas con el timestamp que ya existe
                        echo "$FECHA,$hora,$DIA,$SUCURSAL,$link,$gateway,$distance,$flag,$CONTADOR" >> $HISTORICO
                        #Escribimos el archivo Estado-actual.csv contenido cuándo tenemos las variables definidas
                        echo "$SUCURSAL,$link,$gateway,$distance,$flag,$ts_original" >> $ESTADO_ACTUAL
                    fi
                else
                    echo "ESTADO:   | $flag            |"
                    echo "--------------------------"
                    echo ""
                     if [[ -n "${ESTADO_PREVIO["$SUCURSAL,$link"]}" ]]; then
                        #echo "##################################################### ESTADO_PREVIO[$SUCURSAL,$link]="${ESTADO_PREVIO["$SUCURSAL,$link"]}" ###########"
                        if [[ "${ESTADO_PREVIO["$SUCURSAL,$link"]}" == "Is" ]]; then
                            echo "====================================================================================================================="
                            echo "* ENLACE $link en $SUCURSAL SE REESTABLECIÓ, ENVIANDO ALERTA!!!... *** "
                            echo "====================================================================================================================="
                            #/usr/bin/curl -s -X POST "https://api.telegram.org/bot/sendMessage" -d chat_id="" -d text="¡¡ALERTA!! el enlace $link de $SUCURSAL se REESTABLECIÓ" > /dev/null 2>&1
                        fi
                     fi
                    #Escribimos el archivo agregando contenido cuándo tenemos las variables definidas
                    echo "$FECHA,$hora,$DIA,$SUCURSAL,$link,$gateway,$distance,$flag,$CONTADOR" >> $HISTORICO
                    #Escribimos el archivo Estado-actual.csv contenido cuándo tenemos las variables definidas
                    echo "$SUCURSAL,$link,$gateway,$distance,$flag" >> $ESTADO_ACTUAL
                fi
            fi
        done < "$TMP_FILE"

        echo ""
        
    fi
done

echo "********************************************************************************************************************"
echo "*** ¡¡¡Éste Script se ha ejecutado ***$CONTADOR*** veces, puedes revisar los detalles de la ejecución en el log!!!     ****"
echo "********************************************************************************************************************"

CONTADOR=$((CONTADOR + 1))
echo $CONTADOR > /tmp/excec-mon-link.txt