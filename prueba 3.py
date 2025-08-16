# --------------------------------------
# IMPORTAMOS BIBLIOTECAS NECESARIAS
# --------------------------------------

import pdfplumber  # Para leer el contenido de archivos PDF de forma más precisa que PyMuPDF
import nltk  # Herramienta de procesamiento de lenguaje natural (Natural Language Toolkit)
from nltk import sent_tokenize, word_tokenize, ne_chunk, pos_tag  # Funciones útiles para analizar texto
from nltk.tree import Tree  # Para analizar entidades nombradas como nombres de personas
import tkinter as tk  # Interfaz gráfica de usuario
from tkinter import filedialog  # Para permitir al usuario seleccionar archivos desde el explorador

# Descargamos los recursos de NLTK (solo se hace una vez, la primera vez que se ejecuta el código)
nltk.download('punkt')  # Necesario para dividir texto en oraciones y palabras
nltk.download('averaged_perceptron_tagger')  # Para etiquetar palabras según su función gramatical
nltk.download('maxent_ne_chunker')  # Para detectar entidades nombradas como personas o lugares
nltk.download('words')  # Diccionario de palabras en inglés, usado por NLTK internamente

# --------------------------------------
# FUNCIONES DE EXTRACCIÓN DE TEXTO CON PDFPLUMBER
# --------------------------------------
def extraer_texto_pdf(ruta_pdf):
    """
    Esta función abre el archivo PDF usando pdfplumber y extrae todo el texto
    de manera limpia, página por página. Se añade doble salto de línea para simular párrafos.
    """
    texto = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            contenido = pagina.extract_text()
            if contenido:
                texto += contenido + "\n\n"  # Separamos párrafos con doble salto
    return texto
# --------------------------------------
# FUNCIONES USANDO NLTK
# --------------------------------------
def extraer_titulo(texto):
    """
    Esta función intenta capturar el título desde las primeras líneas del texto.
    Se asume que el título está en las primeras 3 líneas del documento.
    """
    lineas = texto.strip().split("\n")
    primeras = [l.strip() for l in lineas if l.strip()][:3]
    return " ".join(primeras) if primeras else "Título no encontrado"

def extraer_autor(texto):
    """
    Esta función analiza las primeras oraciones del texto para detectar un nombre propio
    usando NLTK. Busca estructuras tipo 'Nombre Apellido'.
    """
    oraciones = sent_tokenize(texto)
    for oracion in oraciones[:5]:  # Solo analiza las 5 primeras oraciones
        palabras = word_tokenize(oracion)
        etiquetas = pos_tag(palabras)  # Clasifica palabras: sustantivo, verbo, etc.
        entidades = ne_chunk(etiquetas)  # Busca entidades nombradas como nombres de personas
        for chunk in entidades:
            if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
                nombre = " ".join(c[0] for c in chunk)
                if len(nombre.split()) >= 2:
                    return nombre
    return "Autor no encontrado"

def extraer_director(texto):
    """
    Esta función busca una línea que mencione al director, tutor o asesor del trabajo.
    No es muy precisa, pero funciona si esas palabras aparecen claramente en el texto.
    """
    claves = ['director', 'asesor', 'tutor']
    for linea in texto.lower().split("\n"):
        if any(clave in linea for clave in claves):
            return linea.strip().capitalize()
    return "Director no encontrado"

def extraer_parrafos(texto, seccion, num_parrafos=2):
    """
    Esta función busca una sección como 'metodología' o 'conclusiones' dentro del texto.
    Luego extrae los primeros párrafos después de encontrar esa sección.
    """
    texto = texto.lower()
    seccion = seccion.lower()
    if seccion in texto:
        contenido = texto.split(seccion, 1)[-1].strip()  # Se queda con lo que viene después del título de sección
        contenido = contenido.split("\n\n")  # Se divide en párrafos según los saltos de línea

        parrafos = []
        for bloque in contenido:
            limpio = bloque.strip().replace("\n", " ")  # Elimina saltos dentro del párrafo
            if len(limpio.split()) > 10:  # Filtra párrafos con poco texto
                parrafos.append(limpio)
            if len(parrafos) == num_parrafos:
                break

        return "\n\n".join(parrafos) if parrafos else f"{seccion.capitalize()} no encontrada."
    return f"{seccion.capitalize()} no encontrada."

# --------------------------------------
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# --------------------------------------
def extraer_info(texto):
    """
    Llama a las funciones de extracción para obtener información clave del texto.
    Devuelve un diccionario con los resultados.
    """
    return {
        "Título": extraer_titulo(texto),
        "Autor": extraer_autor(texto),
        "Director": extraer_director(texto),
        "Metodología": extraer_parrafos(texto, "metodología", num_parrafos=1),
        "Conclusiones": extraer_parrafos(texto, "conclusiones", num_parrafos=1)
    }

# --------------------------------------
# INTERFAZ PARA SELECCIÓN DE ARCHIVOS
# --------------------------------------
def seleccionar_multiples_pdfs():
    """
    Abre una ventana de interfaz gráfica para que el usuario seleccione uno o varios archivos PDF.
    Luego procesa cada archivo y muestra la información extraída en consola.
    """
    root = tk.Tk()  # Crea la ventana
    root.geometry("400x150")
    root.title("Seleccionar PDFs")

    def abrir():
        archivos = filedialog.askopenfilenames(filetypes=[("PDFs", "*.pdf")])  # Selector de archivos
        if archivos:
            for archivo in archivos:
                print(f"\n📄 Procesando: {archivo}\n")
                texto = extraer_texto_pdf(archivo)
                info = extraer_info(texto)
                for clave, valor in info.items():
                    print(f"🔹 {clave}:\n{valor}\n")
                print("=" * 60)
        else:
            print("⚠️ No se seleccionaron archivos.")
        root.destroy()  # Cierra la ventana después de seleccionar

    # Botón para iniciar la selección de PDFs
    tk.Button(root, text="Seleccionar PDFs", command=abrir,
              font=("Arial", 12), bg="green", fg="white").pack(pady=50)
    root.mainloop()

seleccionar_multiples_pdfs()
