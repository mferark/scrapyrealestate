## Scrapyrealestate

Este programa en Python escrapea varios portales inmobiliarios y posteriormente envía las nuevas viviendas detectadas a un grupo de Telegram configurado por el usuario.

### Prerrequisitos

- Windows, Mac o Linux
- Python >= 3.9
- Pip 3
- Conexión a internet
- Canal de Telegram (ver más abajo)
- <b><a href="https://t.me/scrapyrealestate_testing">Grupo de Telegram Testing</a> (Ayuda y resolución de problemas/dudas)</b>

### Instalación Python y paquetes
- Instalar Python 3 (mínimo 3.9)
- Instalar los diferentes paquetes del archivo requirements.txt. Tanto si ya tenemos otros paquetes instalados como si no, es recomendable crear un <a href="https://docs.python.org/es/3/tutorial/venv.html">entorno virtual</a> de python que evitará posibles incopatibilidades.

```
pip3 install -r scrapyrealestate/requirements.txt
```
### Editar archivo de configuracion

Para que todo funcione es necesario editar algunos parámetros del archivo config.yaml:

- **log_level** Nivel de log mínimo que guarda en el archivo **/logs/logs.log**.
- **scrapy_time_update** Tiempo (mínimo 300) entre cada búsqueda (en segundos).
- **telegram_chatuserID** El valor se obtiene de un canal de Telegram. Tenemos que crear previamente uno, si no lo tenemos ya, y obtener el chat id (ver más abajo).
- **urls:** Las urls de fotocasa necesita tener ordenación de las viviendas más recientes. Recomendado para ciudades pequeñas, barrios medianos y pueblos (aprox. 300 viviendas en total), ya que solo coge las 3 primeras viviendas de la página.
 

### Crear canal Telegram y obtener chat id
- **Crear el canal** en Telegram. Lo podemos hacer privado o público. Lo ideal es que fuera público y poder compartirlo para que más gente pueda usarlo. La intención de todo eso es intentar crear una red con esos grupos públicos y que puedan encontrarse en un sitio unificado. De momento se iran guardando todos estos grupos en una base de datos externa para más adelante poder generar esta red.
- **Añadir al canal el bot @scrapyrealestatebot** con permisos para poder publicar mensajes. Eso es necesario para que se publiquen correctamente las viviendas en el canal. Si no está bien añadido, el programa no iniciara.
- **Obtener el chat id**. Lo podemos hacer con el bot de Telegram @RawDataBot.

### Ejecutar script 
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
### Crear servicio 
En máquinas Linux también podemos crear un servicio con esta opción del programa:
```
sudo python3 main.py -ms
```
Para que funcione es necesario antes instalar los paquetes con sudo. Si no necesitamos el servicio no es necesario.
Nos preguntará primero si queremos que lo active para iniciarse de inicio y seguidamente si lo queremos ejecutar.
```
sudo pip3 install -r scrapyrealestate/requirements.txt
```
Una vez instalados con sudo los podemos volver a borrar, ya que realmente no es una buena praxis.
```
sudo pip3 uninstall -r scrapyrealestate/requirements.txt
```
Finalmente podemos ver como esta el servicio:
````
sudo systemctl status scrapyrealestate.service
````