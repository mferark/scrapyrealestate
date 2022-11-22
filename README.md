# Scrapyrealestate

Este programa en Python escrapea varios portales inmobiliarios y posteriormente envía las nuevas viviendas detectadas a un grupo de Telegram configurado por el usuario.

## Requisitos

- Windows, Mac o Linux
- Python >= 3.9
- Pip 3
- Conexión a internet
- Canal de Telegram (ver más abajo)
- <b><a href="https://t.me/scrapyrealestate_testing">Grupo de Telegram Testing</a> (Ayuda y resolución de problemas/dudas)</b>

## 1. Instalación
### Instalación con Docker (Recomendada)
- Instalar Docker.
- Ahora tenemos dos opciones: 
  - Descargamos la imagen y la ejecutamos manualmente.
    ```
    docker pull mferark/scrapyrealestate
    docker run -d -p 8080:8080 --name scrapyrealestate mferark/scrapyrealestate
    ```
  - O bien, usando docker-compose (a veces hay que instalarlo por separado de docker).
    - Descargamos el archivo docker-compose.yaml en un directorio nuevo.
      ```
      curl https://raw.githubusercontent.com/mferark/scrapyrealestate/master/docker-compose.yaml -O docker-compose.yaml
      ```
    - Bajamos la ultima imagen
      ```
      docker-compose pull
      ```
    - Vamos al directorio y ejecutamos el contenedor con docker-compose.
      ```
      docker-compose up -d
      ```
    
- Para ver los logs podemos ejecutar:
```
docker logs ID_CONTENEDOR
```
- Y para ver los ID:
```
docker ps
```

### Instalación sin docker, Python y paquetes
- Instalar Python 3 (mínimo 3.9).
- Instalar los diferentes paquetes del archivo requirements.txt. Tanto si ya tenemos otros paquetes instalados como si no, es recomendable crear un <a href="https://docs.python.org/es/3/tutorial/venv.html">entorno virtual</a> de python que evitará posibles incopatibilidades.
```
pip3 install -r scrapyrealestate/requirements.txt
```

#### Ejecutar script 
Vamos dentro del directorio scrapyrealestate y ejecutamos main.py (importante estar dentro del directorio):

Para Windows es recomendable usar PowerShell y para Linux y Mac la terminal.
```
cd scrapyrealestate
python3 main.py
```
Para evitar que se cierre y dejarlo en segundo plano (en una máquina Linux):

```
nohup python3 main.py &
```

## 2. Editar la configuración

- Si hemos visto os logs veremos que el progama esta esperando que le entremos la configuración mediante una URL. Para ellos vamos a la siguiente:
```
http://127.0.0.1:8080/
```

- Dentro és necesario completar algunos parámetros:

- **scrapy_rs_name** Nombre del programa.
- **log_level** Nivel de log mínimos que muestra el script. Por defecto INFO.
- **log_level_scrapy** Nivel de log mínimos que muestra python scrapy. Por defecto WARNING.
- **scrapy_time_update** Tiempo entre cada búsqueda (mínimo 300, en segundos).
- **telegram_chatuserID** El valor se obtiene de un canal de Telegram. Tenemos que crear previamente uno, si no lo tenemos ya, y obtener el chat id (ver más abajo).
- **max_price** Precio a mostrar máximo. Sí no queremos límite usamos 0.
- **urls:** Introducir las URL de idealista, pisos.com, fotocasa y habitaclia. En el caso de fotocasa necesita tener ordenación de las viviendas más recientes. Recomendado para ciudades pequeñas, barrios medianos y pueblos, ya que solo coge las 2 primeras viviendas de la página. Actualmente no es muy funcional.
- **proxy_idealista** Por seguridad y evitar que baneen nuestra IP, es recomendable su uso. Aún así al ser proxys gratuitos en ocasiones no son muy eficientes.

### Crear canal Telegram y obtener chat id
- **Crear el canal** en Telegram. Lo podemos hacer privado o público. Lo ideal es que fuera público y poder compartirlo para que más gente pueda usarlo. La intención de todo eso es intentar crear una red con esos grupos públicos y que puedan encontrarse en un sitio unificado. De momento se iran guardando todos estos grupos en una base de datos externa para más adelante poder generar esta red.
- **Añadir al canal el bot @scrapyrealestatebot** con permisos para poder publicar mensajes. Eso es necesario para que se publiquen correctamente las viviendas en el canal. Si no está bien añadido, el programa no iniciara.
- **Obtener el chat id**. Lo podemos hacer con el bot de Telegram @RawDataBot, o si estamos en el PC, en la barra de direcciones.