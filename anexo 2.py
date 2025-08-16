# --------------------------------------
# NUEVA VERSIÓN CON SPACY Y PDFPLUMBER
# --------------------------------------

# Importamos las bibliotecas necesarias
import pdfplumber  # Para extraer texto de PDFs con buena estructura
import spacy        # Para procesar el lenguaje natural

import tkinter as tk
from tkinter import filedialog

# Cargamos el modelo de spaCy para español
nlp = spacy.load("es_core_news_sm")

# --------------------------------------
# FUNCIONES DE EXTRACCIÓN
# --------------------------------------

def extraer_texto_pdf(ruta_pdf):
    """
    Extrae el texto de un PDF utilizando pdfplumber.
    Esta herramienta permite conservar la estructura del texto mejor que otras bibliotecas.
    """
    texto_completo = ""
    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text() + "\n"
    return texto_completo

def extraer_titulo_spacy(texto, num_lineas=5):
    """
    Usa las primeras líneas del texto como posible título.
    Aplica spaCy para eliminar entidades irrelevantes si es necesario.
    """
    lineas = texto.split('\n')
    primeras = [linea.strip() for linea in lineas if linea.strip()][:num_lineas]
    return " ".join(primeras).strip() if primeras else "Título no encontrado"

def buscar_autor_spacy(texto):
    """
    Utiliza spaCy para identificar nombres propios que podrían ser el autor.
    Busca personas dentro de las primeras 20 líneas del documento.
    """
    lineas = texto.split('\n')[:20]
    texto_corto = " ".join(lineas)
    doc = nlp(texto_corto)
    autores = [ent.text for ent in doc.ents if ent.label_ == "PER"]
    return autores[0] if autores else "Autor no encontrado"

def extraer_parrafos(texto, seccion, num_parrafos=2, max_lineas_por_parrafo=5):
    """
    Busca una sección específica y extrae hasta 2 párrafos controlados.
    """
    texto = texto.lower()
    seccion = seccion.lower()

    if seccion in texto:
        partes = texto.split(seccion, 1)
        contenido = partes[1].strip()
        lineas = [linea.strip() for linea in contenido.split('\n') if linea.strip()]

        parrafos = []
        parrafo_actual = []

        for linea in lineas:
            parrafo_actual.append(linea)
            if len(parrafo_actual) >= max_lineas_por_parrafo or linea.endswith('.'):
                parrafos.append(" ".join(parrafo_actual).capitalize())
                parrafo_actual = []
            if len(parrafos) >= num_parrafos:
                break

        return "\n\n".join(parrafos) if parrafos else f"{seccion.capitalize()} no encontrada."

    return f"{seccion.capitalize()} no encontrada."

def extraer_director_spacy(texto):
    """
    Busca palabras clave como 'director', 'asesor' o 'tutor' y aplica spaCy
    para identificar nombres relacionados.
    """
    lineas = texto.lower().split('\n')
    for linea in lineas:
        if any(pal in linea for pal in ['director', 'tutor', 'asesor']):
            doc = nlp(linea)
            for ent in doc.ents:
                if ent.label_ == "PER":
                    return ent.text
    return "Director no encontrado"

# --------------------------------------
# FUNCIÓN PRINCIPAL DE EXTRACCIÓN
# --------------------------------------

def extraer_informacion_trabajo(texto):
    titulo = extraer_titulo_spacy(texto)
    autor = buscar_autor_spacy(texto)
    metodologia = extraer_parrafos(texto, "Metodología", num_parrafos=2)
    director = extraer_director_spacy(texto)
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
    root = tk.Tk()
    root.geometry("400x150")
    root.title("Seleccionar trabajos de grado")

    def abrir_archivos():
        archivos = filedialog.askopenfilenames(filetypes=[("Archivos PDF", "*.pdf")])

        if archivos:
            for archivo in archivos:
                print(f"\n📄 Archivo seleccionado: {archivo}")
                texto = extraer_texto_pdf(archivo)
                info = extraer_informacion_trabajo(texto)

                print("🔹 Título:", info["Título"])
                print("🔹 Autor:", info["Autor"])
                print("🔹 Metodología:\n", info["Metodología"])
                print("🔹 Director:", info["Director"])
                print("🔹 Conclusiones:\n", info["Conclusiones"])
                print("\n" + "=" * 70 + "\n")
        else:
            print("⚠️ No se seleccionó ningún archivo.")

        root.destroy()

    tk.Button(root, text="Seleccionar PDFs", command=abrir_archivos,
              font=("Arial", 12), bg="green", fg="white").pack(pady=50)

    root.mainloop()

# --------------------------------------
# EJECUCIÓN DEL PROGRAMA
# --------------------------------------

seleccionar_multiples_pdfs()