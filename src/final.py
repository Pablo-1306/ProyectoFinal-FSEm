import tkinter as tk                # Importa el módulo tkinter para crear interfaces gráficas.
from tkinter import font, messagebox, Label     # Importa elementos específicos de tkinter.
import os                           # Permite interactuar con el sistema operativo.
import subprocess as sp             # Permite ejecutar comandos del sistema en un subproceso.
import evdev                        # Biblioteca para manejar eventos de dispositivos de entrada (como joysticks).
import shutil                       # Permite copiar y mover archivos.
import time                         # Proporciona funciones para trabajar con el tiempo.
import threading                    # Permite ejecutar tareas en segundo plano mediante hilos.
import vlc                          # Biblioteca para manejar la reproducción de multimedia.
import pyudev                       # Biblioteca para manejar eventos de dispositivos USB.

# Función para reproducir el video de introducción.
def load_video():
    player = vlc.MediaPlayer()                      # Crea un reproductor de medios usando VLC.
    video = vlc.Media("/home/raspcarr/video.mp4")   # Carga el archivo de video desde la ruta especificada.
    player.set_media(video)                         # Asocia el video al reproductor.
    player.play()                                   # Inicia la reproducción del video.
    time.sleep(7)                                   # Pausa la ejecución durante 7 segundos para permitir que el video se reproduzca.
    player.stop()                                   # Detiene la reproducción del video.

# Función para cargar los videojuegos desde el directorio ROMS.
def load_videogrames():
    juegos = {}                                             # Crea un diccionario vacío para almacenar los juegos.
    for archivo in os.listdir("/home/raspcarr/roms/"):      # Itera sobre los archivos en el directorio.
        if archivo.endswith(('.smc', '.sfc')):              # Verifica si el archivo tiene extensión válida.
            nombre_juego = os.path.splitext(archivo)[0]     # Obtiene el nombre del archivo sin extensión.
            juegos[nombre_juego] = os.path.join("/home/raspcarr/roms/", archivo)  # Asocia el nombre del juego con su ruta completa.
    return juegos                                           # Devuelve el diccionario de juegos.

# Función para ejecutar el juego seleccionado.
def execute_game(lista_videojuegos, listado_videojuegos):
    try:
        selected_game = lista_videojuegos.get(lista_videojuegos.curselection())             # Obtiene el juego seleccionado de la lista.
        os.system(f'mednafen -sound.driver sdl "{listado_videojuegos[selected_game]}"')     # Ejecuta el juego con el emulador Mednafen.
    except tk.TclError:                         # Maneja el error si no se selecciona ningún juego.
        messagebox.showinfo("Error", "Selecciona un juego primero.")                        # Muestra un mensaje de error.

# Función para apagar la consola.
def turn_off():
    os.system("shutdown now 2> /dev/null")          # Ejecuta el comando para apagar el sistema.

# Función para reiniciar la consola.
def reboot():
    os.system("sudo reboot")                        # Ejecuta el comando para reiniciar el sistema.

# Función para actualizar la selección en la lista de videojuegos.
def update_selection(lista_videojuegos, listado_videojuegos):
    selected_index = lista_videojuegos.curselection()       # Obtiene el índice del elemento seleccionado.
    if selected_index:
        index = selected_index[0]                           # Extrae el índice como un número entero.

        labels = window.winfo_children()                    # Obtiene todos los widgets hijos de la ventana principal.
        labels = [label for label in labels if isinstance(label, Label) and (label['text'] in listado_videojuegos)]  # Filtra los labels que corresponden a juegos.

        for label in labels:                                # Itera sobre cada label en la lista.
            label.config(fg="white", bg="black", font=("Courier", 18))  # Restablece el estilo a blanco sobre negro.

        selected_label = labels[index]                      # Obtiene el label correspondiente al juego seleccionado.
        selected_label.config(fg="yellow", bg="black", font=("Press Start 2P", 22))  # Cambia el estilo del juego seleccionado.

        lista_videojuegos.selection_clear(0, tk.END)        # Limpia todas las selecciones en la lista.
        lista_videojuegos.selection_set(index)              # Selecciona el elemento actual.
        lista_videojuegos.activate(index)                   # Activa el elemento seleccionado.
        lista_videojuegos.see(index)                        # Desplaza la vista para asegurar que el elemento seleccionado sea visible.

# Función para navegar por la lista usando un control.
def navigate(event, lista_videojuegos, listado_videojuegos):
    current = lista_videojuegos.curselection()              # Obtiene la selección actual.
    if not current:                                         # Si no hay nada seleccionado.
        lista_videojuegos.selection_set(0)                  # Selecciona el primer elemento.
        update_selection(lista_videojuegos, listado_videojuegos)  # Actualiza la selección.
        return

    index = current[0]                                      # Obtiene el índice actual.
    size = len(listado_videojuegos)                         # Obtiene el tamaño de la lista de juegos.

    if event == -1 and index > 0:                           # Presión de la cruceta arriba.
        new_index = max(0, index - 2)
    elif event == 1 and index < size - 1:                   # Presión de la cruceta abajo.
        new_index = min(size - 1, index + 2)
    elif event == -2 and index > 0:                         # Presión de la cruceta izquierda.
        new_index = max(0, index - 1)
    elif event == 2 and index < size - 1:                   # Presión de la cruceta derecha.
        new_index = min(size - 1, index + 1)
    else:
        return                                              # Si no hay movimiento válido, termina la función.

    lista_videojuegos.selection_clear(index)                # Limpia la selección anterior.
    lista_videojuegos.selection_set(new_index)              # Selecciona el nuevo índice.
    update_selection(lista_videojuegos, listado_videojuegos)  # Actualiza la vista con el nuevo elemento.

# Función para montar automáticamente un dispositivo USB en una ruta específica.
def auto_mount(path):
    try:
        sp.run(["udisksctl", "mount", "-b", path], check=True)  # Ejecuta el comando para montar el dispositivo usando udisksctl.
    except sp.CalledProcessError as e:                          # Captura errores si el comando falla.
        print(f"Failed to mount {path}: {e}")                   # Muestra un mensaje de error en la consola.

# Función para obtener el punto de montaje de un dispositivo.
def get_mount_point(path):
    args = ["findmnt", "-unl", "-S", path]                      # Comando para obtener el punto de montaje.
    cp = sp.run(args, capture_output=True, text=True)           # Ejecuta el comando y captura la salida.
    if cp.returncode == 0:                                      # Si el comando se ejecutó con éxito.
        return cp.stdout.split()[0]                             # Devuelve el punto de montaje como una cadena.
    else:
        print(f"Failed to get mount point for {path}")          # Muestra un mensaje si falla.
        return None                                             # Devuelve None si no se encontró el punto de montaje.

# Función para verificar si un archivo ya existe en el directorio de destino.
def file_exists_in_destination(file, destination_dir):
    return os.path.exists(os.path.join(destination_dir, file))  # Devuelve True si el archivo existe en la ruta especificada.

# Función para mover archivos de una fuente a un destino, solo si no existen en el destino.
def move_files(source_dir, destination_dir):
    global window                                       # Declara la variable 'window' como global para actualizar la interfaz.
    if not os.path.exists(destination_dir):             # Verifica si el directorio de destino no existe.
        os.makedirs(destination_dir)                    # Crea el directorio de destino.

    for root, dirs, files in os.walk(source_dir):       # Recorre todos los archivos en el directorio de origen.
        for file in files:                              # Itera sobre cada archivo.
            if file.endswith(".sfc") or file.endswith(".smc"):  # Verifica si el archivo es una ROM válida.
                if not file_exists_in_destination(file, destination_dir):  # Verifica si el archivo no existe en el destino.
                    file_path = os.path.join(root, file)        # Obtiene la ruta completa del archivo.
                    shutil.copy(file_path, destination_dir)     # Copia el archivo al destino.
                    print(f'Moved {file} to {destination_dir}')  # Muestra un mensaje indicando que se movió el archivo.
                else:
                    print(f'Skipped {file}, already exists in {destination_dir}')  # Muestra un mensaje si el archivo ya existe.
    window.update()                                      # Actualiza la interfaz gráfica.
    window.update_idletasks()                            # Procesa cualquier tarea pendiente de la interfaz.

# Inicializa el contexto para monitorear dispositivos USB.
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)                  # Crea un monitor para detectar eventos de dispositivos.
monitor.filter_by(subsystem="block", device_type="partition")   # Filtra solo dispositivos de almacenamiento.

# Función para escuchar eventos de conexión de dispositivos USB.
def listen_for_usb():
    while True:                                             # Bucle infinito para seguir escuchando eventos.
        try:
            action, device = monitor.receive_device()       # Escucha un evento de dispositivo.
            if action == "add":                             # Si se detecta un dispositivo nuevo.
                device_path = f"/dev/{device.sys_name}"     # Construye la ruta del dispositivo.
                auto_mount(device_path)                     # Monta el dispositivo automáticamente.
                mp = get_mount_point(device_path)           # Obtiene el punto de montaje.
                if mp:
                    move_files(mp, "/home/raspcarr/roms")   # Mueve los archivos al directorio de ROMs.
        except pyudev.DeviceNotFoundByFileError:
            print("Error: Device not found.")               # Muestra un mensaje si no se encuentra el dispositivo.

# Función para inicializar la interfaz de usuario.
def init_user_interface():
    global window                                           # Declara la variable 'window' como global.
    window = tk.Tk()                                        # Crea la ventana principal.
    window.title("SERBLO CONSOLE")                          # Establece el título de la ventana.
    window.config(cursor="none")                            # Oculta el cursor.
    ancho = window.winfo_screenwidth()                      # Obtiene el ancho de la pantalla.
    alto = window.winfo_screenheight()                      # Obtiene el alto de la pantalla.
    window.geometry(f"{ancho}x{alto}")                      # Ajusta el tamaño de la ventana al tamaño de la pantalla.
    window.configure(bg="black")                            # Establece el fondo de la ventana como negro.

    try:
        logo = tk.PhotoImage(file="logo.png")               # Carga la imagen del logo.
        label_logo = tk.Label(window, image=logo, bg="black")  # Crea un label para mostrar el logo.
        label_logo.place(x=20, y=20)                        # Coloca el logo en la esquina superior izquierda.
    except tk.TclError:
        print("Error al cargar la imagen del logo.")        # Muestra un mensaje si no se puede cargar la imagen.

    custom_font = font.Font(family="Press Start 2P", size=24)  # Crea una fuente personalizada.
    etiqueta = tk.Label(window, text="Selecciona un videojuego", font=custom_font, fg="white", bg="black")  # Crea un label para el título.
    etiqueta.pack(pady=20)                                  # Añade un margen superior.

    listado_videojuegos = load_videogrames()                # Carga los videojuegos disponibles.

    global lista_videojuegos                                # Declara la lista de videojuegos como global.
    lista_videojuegos = tk.Listbox(
        window,
        font=("Courier", 20),
        selectmode=tk.SINGLE,
        bg="#394E9A",
        fg="white",
        highlightthickness=0,
        activestyle="none",
        width=30,
        height=15
    )  # Crea una lista para mostrar los videojuegos.

    # Distribuye los juegos en dos columnas.
    column_width = ancho // 4
    y_offset = 150
    for i, juego in enumerate(listado_videojuegos):
        x_pos = column_width if i % 2 == 0 else column_width * 2
        y_pos = y_offset + (i // 2) * 60
        lbl = tk.Label(window, text=juego, font=("Courier", 18), fg="white", bg="black")
        lbl.place(x=x_pos, y=y_pos)

    # Botón para apagar la consola.
    boton_apagar = tk.Label(window, text="Apagar (Select)", font=("Courier", 20), fg="white", bg="red")
    boton_apagar.place(x=ancho - boton_apagar.winfo_reqwidth(), y=0)

    # Botón para reiniciar la consola.
    boton_reiniciar = tk.Label(window, text="Reiniciar (Start)", font=("Courier", 20), fg="white", bg="blue")
    boton_reiniciar.place(x=ancho - boton_reiniciar.winfo_reqwidth(), y=alto - boton_apagar.winfo_reqheight())

    lista_videojuegos.insert(tk.END, *listado_videojuegos)
    lista_videojuegos.selection_set(0)
    update_selection(lista_videojuegos, listado_videojuegos)

    # Inicia un hilo para manejar la entrada del joystick.
    joystick_thread = threading.Thread(target=handle_joystick_input, args=(lista_videojuegos, listado_videojuegos))
    joystick_thread.daemon = True
    joystick_thread.start()

    window.mainloop()  # Inicia el bucle principal de la interfaz.


# Función para manejar la entrada del joystick de Xbox.
def handle_joystick_input(lista_videojuegos, listado_videojuegos):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]  # Lista todos los dispositivos de entrada disponibles.
    for device in devices:                                      # Itera sobre cada dispositivo encontrado.
        if "xbox" in device.name.lower():                       # Verifica si el dispositivo es un control de Xbox.
            while True:                                         # Bucle infinito para manejar la entrada continua del joystick.
                try:
                    for event in device.read_loop():            # Lee los eventos generados por el dispositivo.
                        if event.type == evdev.ecodes.EV_KEY:   # Verifica si el evento es una pulsación de tecla/botón.
                            if event.code == evdev.ecodes.BTN_A and event.value == 1:   # Botón A presionado.
                                execute_game(lista_videojuegos, listado_videojuegos)    # Ejecuta el juego seleccionado.
                            elif event.code == evdev.ecodes.BTN_SELECT and event.value == 1:  # Botón SELECT presionado.
                                turn_off()                      # Apaga la consola.
                            elif event.code == evdev.ecodes.BTN_START and event.value == 1:  # Botón START presionado.
                                reboot()                        # Reinicia la consola.
                        elif event.type == evdev.ecodes.EV_ABS: # Verifica si el evento es de tipo analógico (movimiento).
                            if event.code == evdev.ecodes.ABS_HAT0Y:  # Movimiento vertical en el D-pad.
                                if event.value == -1:           # CRUCETA arriba.
                                    navigate(-1, lista_videojuegos, listado_videojuegos)  # Desplaza hacia arriba en la lista.
                                elif event.value == 1:          # CRUCETA abajo.
                                    navigate(1, lista_videojuegos, listado_videojuegos)  # Desplaza hacia abajo en la lista.
                            elif event.code == evdev.ecodes.ABS_HAT0X:  # Movimiento horizontal en el D-pad.
                                if event.value == -1:           # CRUCETA izquierda.
                                    navigate(-2, lista_videojuegos, listado_videojuegos)  # Desplaza hacia la izquierda.
                                elif event.value == 1:          # CRUCETA derecha.
                                    navigate(2, lista_videojuegos, listado_videojuegos)  # Desplaza hacia la derecha.

                except OSError:                                 # Maneja errores si el joystick se desconecta.
                    print("Error: Joystick disconnected.")      # Muestra un mensaje de error.
                    break                                       # Sale del bucle si el joystick se desconecta.

# Punto de entrada principal del programa.
if __name__ == "__main__":
    load_video()  # Reproduce el video de inicio.
    
    # Inicia un hilo separado para escuchar dispositivos USB.
    devices_thread = threading.Thread(target=listen_for_usb)
    devices_thread.daemon = True  # Configura el hilo como daemon para que termine junto con el programa.
    devices_thread.start()  # Comienza a escuchar dispositivos USB.
    
    init_user_interface()  # Inicia la interfaz de usuario.
