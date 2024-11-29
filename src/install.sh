#!/bin/bash

# Actualizar el sistema
echo "Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar herramientas de compilación y dependencias
echo "Instalando herramientas de compilación y dependencias..."
sudo apt install -y \
build-essential \
libasound2-dev \
libglib2.0-dev \
libpng-dev \
libzstd-dev \
libjpeg-dev \
libsdl2-dev \
wget \
xinit \
xserver-xorg \
x11-xserver-utils \
vlc \
python3-vlc \
python3-pyudev \
python3-evdev \
python3-tk

# Descargar Mednafen
echo "Descargando Mednafen..."
wget https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz

# Descomprimir Mednafen
echo "Descomprimiendo Mednafen..."
tar -xvf mednafen-1.32.1.tar.xz

# Entrar a la carpeta de Mednafen y configurar
cd mednafen-1.32.1 || exit
echo "Configurando Mednafen..."
./configure

# Compilar el código fuente
echo "Compilando Mednafen, esto puede tardar..."
cd src || exit
make

# Instalar Mednafen
echo "Instalando Mednafen..."
sudo make install

# Copiar archivo de configuración de Mednafen
echo "Copiando archivo de configuración..."
mkdir -p ~/.mednafen
cp mednafen.cfg ~/.mednafen/mednafen.cfg

# Descargar los videojuegos
echo "Descargando videojuegos..."
cd /home/raspcarr || exit
wget --content-disposition "https://drive.google.com/uc?export=download&id=1rPQ99st3MSAt5NqlyWxtWNrreEoPU9rR"

# Descomprimir los videojuegos
echo "Descomprimiendo videojuegos..."
unzip roms.zip -d /home/raspcarr/roms/

# Configurar permisos
echo "Configurando permisos del directorio de videojuegos..."
sudo chmod -R 755 /home/raspcarr/roms/

# Crear archivo .xinitrc para ejecutar el programa al iniciar el entorno gráfico
echo "Configurando inicio automático del programa..."
echo "python3 final.py" > ~/.xinitrc

# Configurar inicio automático de la interfaz gráfica en el arranque
sudo bash -c 'echo "startx" >> /etc/rc.local'

# Finalizar el proceso
echo "Instalación completada. El sistema se reiniciará ahora."
sudo reboot
