# Importamos las bibliotecas necesarias
import fitz  # PyMuPDF: permite abrir y leer archivos PDF
import re    # re: para trabajar con expresiones regulares (útil para encontrar nombres)
import tkinter as tk  # tkinter: interfaz gráfica para seleccionar archivos
from tkinter import filedialog  # filedialog: módulo para abrir ventanas de selección de archivos

# --------------------------------------
# FUNCIONES DE EXTRACCIÓN DE TEXTO
# --------------------------------------

def extraer_texto_pdf(ruta_pdf):
    """
    Esta función abre un archivo PDF y extrae todo el texto.
    Se utiliza cuando se quiere analizar el contenido completo del documento.
    """
    documento = fitz.open(ruta_pdf)  # Abre el archivo PDF
    texto_completo = ""

    for pagina in documento:  # Recorre todas las páginas del documento
        texto_completo += pagina.get_text()  # Extrae el texto de cada página y lo agrega a una variable

    documento.close()  # Cierra el documento para liberar memoria
    return texto_completo  # Devuelve todo el texto en una sola cadena

def extraer_texto_primera_pagina(ruta_pdf):
    """
    Esta función extrae el texto solo de la primera página del PDF.
    Es útil para identificar el título o el autor, que suelen aparecer al inicio.
    """
    documento = fitz.open(ruta_pdf)       # Abrimos el PDF
    primera_pagina = documento.load_page(0)  # Cargamos la primera página (índice 0)
    texto = primera_pagina.get_text()     # Extraemos su texto
    documento.close()                     # Cerramos el documento
    return texto                          # Retornamos el texto de esa página

# --------------------------------------
# FUNCIONES DE EXTRACCIÓN DE INFORMACIÓN
# --------------------------------------

def extraer_primeras_lineas(texto, num_lineas=5):
    """
    Toma las primeras líneas del texto como posible título del trabajo.
    """
    lineas = texto.split('\n')  # Divide el texto en líneas
    primeras_lineas = []

    for linea in lineas:
        if linea.strip():  # Asegura que la línea no esté vacía
            primeras_lineas.append(linea)
            if len(primeras_lineas) >= num_lineas:
                break

    # Une las líneas y las devuelve como una cadena
    return " ".join(primeras_lineas).strip() if primeras_lineas else "Título no encontrado"

def buscar_autor_despues_titulo(texto, titulo, lineas_busqueda=2):
    """
    Busca el nombre del autor justo después del título o después de la palabra 'Autor'.
    """
    if titulo in texto:
        texto_despues = texto.split(titulo, 1)[-1]  # Separa el texto desde el título hacia adelante
    else:
        return "Autor no encontrado"

    lineas = [linea.strip() for linea in texto_despues.split('\n') if linea.strip()]

    patrones = ['autor', 'autores', 'presentado por']
    autor_encontrado = False
    posibles_lineas = []

    for i, linea in enumerate(lineas):
        if any(p in linea.lower() for p in patrones):  # Si contiene la palabra 'autor'
            autor_encontrado = True
            continue
        if autor_encontrado:
            return linea  # Retorna la línea siguiente a 'autor'
        if not autor_encontrado and len(posibles_lineas) < lineas_busqueda:
            posibles_lineas.append(linea)

    return " ".join(posibles_lineas) if posibles_lineas else "Autor no encontrado"

def buscar_nombre(texto):
    """
    Encuentra posibles nombres (Nombre Apellido) en el texto usando expresiones regulares.
    """
    patron = r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b'
    nombres = re.findall(patron, texto)
    nombres = list(set(nombres))  # Elimina duplicados
    return nombres if nombres else "Nombre no encontrado"

def extraer_parrafos(texto, seccion, num_parrafos=2, max_lineas_por_parrafo=5):
    """
    Busca una sección del texto (por ejemplo, 'Metodología', 'Conclusiones') y extrae los primeros 2 párrafos siguientes.
    
    Parámetros:
    - texto: texto completo extraído del PDF.
    - seccion: palabra clave que identifica la sección a buscar ('Metodología', 'Conclusiones', etc.).
    - num_parrafos: número máximo de párrafos que se desea extraer (por defecto 2).
    - max_lineas_por_parrafo: cantidad de líneas que se aceptan como máximo dentro de un párrafo estimado.

    Esta función es útil cuando los documentos no separan claramente los párrafos con líneas vacías.
    """

    # Convertimos todo el texto y la palabra clave a minúsculas para evitar errores por mayúsculas/minúsculas
    texto = texto.lower()
    seccion = seccion.lower()

    # Verificamos si la palabra clave (sección) está presente en el texto
    if seccion in texto:
        # Dividimos el texto justo a partir de la palabra clave encontrada
        partes = texto.split(seccion, 1)
        contenido = partes[1].strip()  # Tomamos el contenido posterior a la sección

        # Dividimos el contenido en líneas (una línea por salto de línea)
        # También eliminamos líneas vacías usando strip()
        lineas = [linea.strip() for linea in contenido.split('\n') if linea.strip()]

        # Inicializamos lista para guardar párrafos ya formados
        parrafos = []

        # Lista temporal para ir armando un párrafo línea por línea
        parrafo_actual = []

        # Recorremos cada línea encontrada después de la sección
        for linea in lineas:
            parrafo_actual.append(linea)  # Agregamos la línea actual al párrafo en construcción

            # Evaluamos si ya tenemos suficientes líneas o si la línea termina en punto
            if len(parrafo_actual) >= max_lineas_por_parrafo or linea.endswith('.'):
                # Si cumple una de las condiciones, unimos el párrafo actual en una sola cadena
                parrafos.append(" ".join(parrafo_actual).capitalize())  # Capitaliza la primera letra
                parrafo_actual = []  # Reiniciamos el párrafo actual para construir el siguiente

            # Si ya alcanzamos el número deseado de párrafos, salimos del bucle
            if len(parrafos) >= num_parrafos:
                break

        # Si encontramos párrafos, los devolvemos unidos con doble salto de línea para mayor claridad
        return "\n\n".join(parrafos) if parrafos else f"{seccion.capitalize()} no encontrada."

    # Si la sección no se encuentra en el texto, devolvemos un mensaje indicando que no fue hallada
    return f"{seccion.capitalize()} no encontrada."

def extraer_director(texto):
    """
    Intenta encontrar una línea que mencione al director, tutor o asesor del trabajo.
    """
    texto = texto.lower()
    lineas = texto.split('\n')
    for linea in lineas:
        if any(p in linea for p in ['director', 'tutor', 'asesor']):
            return linea.strip().capitalize()
    return "Director no encontrado"

# --------------------------------------
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# --------------------------------------

def extraer_informacion_trabajo(texto):
    """
    Reúne toda la información importante extraída del texto del trabajo.
    """
    titulo = extraer_primeras_lineas(texto)
    autor = buscar_autor_despues_titulo(texto, titulo)
    metodologia = extraer_parrafos(texto, "Metodología", num_parrafos=2)
    director = extraer_director(texto)
    conclusiones = extraer_parrafos(texto, "Conclusiones", num_parrafos=2)

    return {
        "Título": titulo,
        "Autor": autor,
        "Metodología": metodologia,
        "Director": director,
        "Conclusiones": conclusiones
    }

# --------------------------------------
# INTERFAZ GRÁFICA PARA SELECCIÓN DE ARCHIVOS
# --------------------------------------

def seleccionar_multiples_pdfs():
    """
    Abre una ventana para seleccionar múltiples archivos PDF.
    Por cada uno, se extrae y muestra la información estructurada.
    """
    root = tk.Tk()               # Crea la ventana principal
    root.geometry("400x150")     # Define el tamaño de la ventana
    root.title("Seleccionar trabajos de grado")

    def abrir_archivos():
        # Abre el explorador de archivos para seleccionar varios PDFs
        archivos_pdf = filedialog.askopenfilenames(filetypes=[("Archivos PDF", "*.pdf")])

        if archivos_pdf:
            for archivo in archivos_pdf:
                print(f"\n Archivo seleccionado: {archivo}")

                # Extraemos el contenido del PDF
                texto = extraer_texto_pdf(archivo)

                # Extraemos la información clave
                info = extraer_informacion_trabajo(texto)

                # Mostramos los resultados en consola
                print("🔹 Título:", info["Título"])
                print("🔹 Autor:", info["Autor"])
                print("🔹 Metodología:\n", info["Metodología"])
                print("🔹 Director:", info["Director"])
                print("🔹 Conclusiones:\n", info["Conclusiones"])
                print("\n" + "=" * 70 + "\n")
        else:
            print("⚠️ No se seleccionó ningún archivo.")

        root.destroy()  # Cierra la ventana una vez finalizado

    # Botón que inicia el proceso de selección de archivos
    btn = tk.Button(root, text="Seleccionar PDFs", command=abrir_archivos,
                    font=("Arial", 12), bg="green", fg="white")
    btn.pack(pady=50)  # Ubicación del botón

    root.mainloop()  # Inicia la ventana gráfica

# --------------------------------------
# EJECUCIÓN DEL PROGRAMA
# --------------------------------------

seleccionar_multiples_pdfs()