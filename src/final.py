import tkinter as tk
from tkinter import font, messagebox, Label
import os
import subprocess as sp
import evdev
import shutil
import time
import threading
import vlc
import pyudev

# CARGAR EL VIDEO DE INICIO DE CONSOLA
def load_video():
    player = vlc.MediaPlayer()
    video = vlc.Media("/home/raspcarr/video.mp4")
    player.set_media(video)
    player.play()
    time.sleep(7)
    player.stop()

# CARGAR LOS VIDEOJUEGOS AL DIRECTORIO ROMS
def load_videogrames():
    juegos = {}
    for archivo in os.listdir("/home/raspcarr/roms/"):
        if archivo.endswith(('.smc', '.sfc')):
            nombre_juego = os.path.splitext(archivo)[0]
            juegos[nombre_juego] = os.path.join("/home/raspcarr/roms/", archivo)
    return juegos

# EJECUCIÓN DE VIDEOJUEGO SELECCIONADO
def execute_game(lista_videojuegos, listado_videojuegos):
    try:
        selected_game = lista_videojuegos.get(lista_videojuegos.curselection())
        # Encerrar el nombre del juego entre comillas para manejar espacios
        os.system(f'mednafen -sound.driver sdl "{listado_videojuegos[selected_game]}"')  
    except tk.TclError:
        messagebox.showinfo("Error", "Selecciona un juego primero.")

# APAGADO DE CONSOLA
def turn_off():
    os.system("shutdown now 2> /dev/null")

# REINICIO DE CONSOLA
def reboot():
    os.system("sudo reboot")

# SELECCIÓN DE OPCION
def update_selection(lista_videojuegos, listado_videojuegos):
    selected_index = lista_videojuegos.curselection()
    if selected_index:
        index = selected_index[0]

        # Obtener todos los labels de los juegos
        labels = window.winfo_children()
        labels = [label for label in labels if isinstance(label, Label) and (label['text'] in listado_videojuegos)]

        # Restablecer el estilo de todos los labels
        for label in labels:
            label.config(fg="white", bg="black", font=("Courier", 18))

        # Cambiar el estilo del label seleccionado
        selected_label = labels[index]
        selected_label.config(fg="yellow", bg="black", font=("Press Start 2P", 22))

        lista_videojuegos.selection_clear(0, tk.END)
        lista_videojuegos.selection_set(index)
        lista_videojuegos.activate(index)
        lista_videojuegos.see(index)

# DESPLAZAMIENTO EN LISTADO DE OPCIONES
def navigate(event, lista_videojuegos, listado_videojuegos):
    current = lista_videojuegos.curselection()
    if not current:
        lista_videojuegos.selection_set(0)
        update_selection(lista_videojuegos, listado_videojuegos)
        return
    index = current[0]
    size = len(listado_videojuegos)  # No sumar 1, ya que el botón "Apagar" está fuera de la lista

    if event == -1 and index > 0:  # Arriba
        new_index = max(0, index - 2)
    elif event == 1 and index < size - 1:  # Abajo
        new_index = min(size - 1, index + 2)
    elif event == -2 and index > 0:  # Izquierda
        new_index = max(0, index - 1)
    elif event == 2 and index < size - 1:  # Derecha
        new_index = min(size - 1, index + 1)
    else:
        return

    lista_videojuegos.selection_clear(index)
    lista_videojuegos.selection_set(new_index)
    update_selection(lista_videojuegos, listado_videojuegos)

# CONFIG USB
def auto_mount(path):
    try:
        sp.run(["udisksctl", "mount", "-b", path], check=True)
    except sp.CalledProcessError as e:
        print(f"Failed to mount {path}: {e}")

def get_mount_point(path):
    args = ["findmnt", "-unl", "-S", path]
    cp = sp.run(args, capture_output=True, text=True)
    if cp.returncode == 0:
        return cp.stdout.split()[0]
    else:
        print(f"Failed to get mount point for {path}")
        return None

# VERIFICACIÓN DE ARCHIVOS EXISTENTES
def file_exists_in_destination(file, destination_dir):
    return os.path.exists(os.path.join(destination_dir, file))

# COPIA DE VIDEOJUEGOS A ARCHIVO LOCAL
def move_files(source_dir, destination_dir):
    global window
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".sfc") or file.endswith(".smc"):
                if not file_exists_in_destination(file, destination_dir):
                    file_path = os.path.join(root, file)
                    shutil.copy(file_path, destination_dir)
                    print(f'Moved {file} to {destination_dir}')
                else:
                    print(f'Skipped {file}, already exists in {destination_dir}')
    window.update()
    window.update_idletasks()

# FUNCIÓN PARA DETECTAR USB
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem="block", device_type="partition")

def listen_for_usb():
    while True:
        try:
            action, device = monitor.receive_device()
            if action == "add":
                device_path = f"/dev/{device.sys_name}"
                auto_mount(device_path)
                mp = get_mount_point(device_path)
                if mp:
                    move_files(mp, "/home/raspcarr/roms")
        except pyudev.DeviceNotFoundByFileError:
            print("Error: Device not found.")

# GENERACIÓN DE INTERFAZ
def init_user_interface():
    global window  # Declarar window como global
    window = tk.Tk()
    window.title("SERBLO CONSOLE")
    window.config(cursor="none")  # Ocultar el cursor
    ancho = window.winfo_screenwidth()
    alto = window.winfo_screenheight()
    window.geometry(f"{ancho}x{alto}")
    window.configure(bg="black")  # Cambiar el color de fondo a oscuro

    # Cargar el logo
    try:
        logo = tk.PhotoImage(file="logo.png")
        label_logo = tk.Label(window, image=logo, bg="black")
        label_logo.place(x=20, y=20)
    except tk.TclError:
        print("Error al cargar la imagen del logo.")

    # Usar una fuente más estilizada
    custom_font = font.Font(family="Press Start 2P", size=24)
    etiqueta = tk.Label(window, text="Selecciona un videojuego", font=custom_font, fg="white", bg="black")
    etiqueta.pack(pady=20)

    listado_videojuegos = load_videogrames()

    global lista_videojuegos  # Declarar lista_videojuegos como global
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
    )

    # Colocar videojuegos en dos columnas con mejor distribución y más espacio, movidas a la izquierda
    column_width = ancho // 4
    y_offset = 150  # Espacio inicial en y
    for i, juego in enumerate(listado_videojuegos):
        x_pos = column_width if i % 2 == 0 else column_width * 2
        y_pos = y_offset + (i // 2) * 60
        lbl = tk.Label(window, text=juego, font=("Courier", 18), fg="white", bg="black")
        lbl.place(x=x_pos, y=y_pos)

    # Botón "Apagar" fuera de la lista y con otro color
    boton_apagar = tk.Label(window, text="Apagar (Select)", font=("Courier", 20), fg="white", bg="red")
    # Suponiendo que el ancho total de la ventana es window_width
    boton_apagar.place(x=ancho - boton_apagar.winfo_reqwidth(), y=0)

    # Botón "Reiniciar" fuera de la lista y con otro color
    boton_reiniciar = tk.Label(window, text="Reiniciar (Start)", font=("Courier", 20), fg="white", bg="blue")
    # Suponiendo que el ancho total de la ventana es window_width
    boton_reiniciar.place(x=ancho - boton_reiniciar.winfo_reqwidth(), y=alto - boton_apagar.winfo_reqheight())

    lista_videojuegos.insert(tk.END, *listado_videojuegos)
    lista_videojuegos.selection_set(0)
    update_selection(lista_videojuegos, listado_videojuegos)

    # LISTENER DE MANDO
    joystick_thread = threading.Thread(target=handle_joystick_input, args=(lista_videojuegos, listado_videojuegos))
    joystick_thread.daemon = True
    joystick_thread.start()

    window.mainloop()

# LISTENER PARA CONTROL DE XBOX
def handle_joystick_input(lista_videojuegos, listado_videojuegos):
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "xbox" in device.name.lower():
            while True:
                try:
                    for event in device.read_loop():
                        if event.type == evdev.ecodes.EV_KEY:
                            if event.code == evdev.ecodes.BTN_A and event.value == 1:
                                execute_game(lista_videojuegos, listado_videojuegos)
                            elif event.code == evdev.ecodes.BTN_SELECT and event.value == 1:
                                turn_off()
                            elif event.code == evdev.ecodes.BTN_START and event.value == 1:
                                reboot()
                        elif event.type == evdev.ecodes.EV_ABS:
                            if event.code == evdev.ecodes.ABS_HAT0Y:
                                if event.value == -1:  # Arriba
                                    navigate(-1, lista_videojuegos, listado_videojuegos)
                                elif event.value == 1:  # Abajo
                                    navigate(1, lista_videojuegos, listado_videojuegos)
                            elif event.code == evdev.ecodes.ABS_HAT0X:
                                if event.value == -1:  # Izquierda
                                    navigate(-2, lista_videojuegos, listado_videojuegos)
                                elif event.value == 1:  # Derecha
                                    navigate(2, lista_videojuegos, listado_videojuegos)

                except OSError:
                    print("Error: Joystick disconnected.")
                    break

# MAIN FUNCTION
if __name__ == "__main__":
    # CARGA DE VIDEO DE CONSOLA
    load_video()
    # LISTENER DE USB
    devices_thread = threading.Thread(target=listen_for_usb)
    devices_thread.daemon = True
    devices_thread.start()
    # CARGA DE INTERFAZ
    init_user_interface()