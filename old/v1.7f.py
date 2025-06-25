import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import re
import json
import datetime
import threading

# Configurar tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GeneradorEstructura:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🏗️ Generador de Estructura de Carpetas")
        self.root.geometry("1200x800")

        # Ruta por defecto (escritorio)
        self.ruta_destino = os.path.join(os.path.expanduser("~"), "Desktop")

        # Plantillas disponibles
        self.plantillas = {
            "Web Vanilla": """mi-proyecto-vanilla/
├── public/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── assets/
│   ├── images/
│   └── fonts/
└── README.md""",

            "Express": """api-express/
├── app.js
├── package.json
├── routes/
│   ├── index.js
│   └── users.js
├── controllers/
│   └── usersController.js
├── models/
│   └── user.model.js
├── middleware/
└── .env""",

            "MVC": """mvc-proyecto/
├── config/
│   └── database.js
├── controllers/
│   └── userController.js
├── models/
│   └── userModel.js
├── views/
│   ├── layouts/
│   └── partials/
├── routes/
│   └── userRoutes.js
└── app.js""",

            "Hexagonal": """hexagonal-app/
├── adapters/
│   ├── infrastructure/
│   └── presentation/
├── application/
│   ├── usecases/
│   └── dtos/
├── domain/
│   ├── entities/
│   └── repositories/
├── interfaces/
└── config/
    └── database.js"""
        }

        # Crear la interfaz
        self.crear_interfaz()

        # Iniciar el hilo para actualizar la vista previa
        self.actualizar_vista_previa_periodicamente()

    def crear_interfaz(self):
        # Frame principal
        frame_principal = ctk.CTkFrame(self.root)
        frame_principal.pack(pady=10, padx=20, fill="both", expand=True)

        # Sección de ruta
        frame_ruta = ctk.CTkFrame(frame_principal)
        frame_ruta.pack(pady=20, padx=20, fill="x")

        label_ruta_titulo = ctk.CTkLabel(
            frame_ruta,
            text="📁 Ruta de Destino:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label_ruta_titulo.pack(pady=(15, 5))

        self.label_ruta = ctk.CTkLabel(
            frame_ruta,
            text=self.ruta_destino,
            font=ctk.CTkFont(size=12),
            text_color="lightblue"
        )
        self.label_ruta.pack(pady=(0, 10))

        # Frame para los botones de la ruta (alineados en fila)
        frame_botones_ruta = ctk.CTkFrame(frame_ruta)
        frame_botones_ruta.pack(pady=(0, 15))

        btn_cambiar_ruta = ctk.CTkButton(
            frame_botones_ruta,
            text="🔄 Cambiar Ruta",
            command=self.cambiar_ruta,
            width=150,
            height=35
        )
        btn_cambiar_ruta.pack(side="left", padx=5)

        # Botón para generar proyecto
        btn_generar_proyecto = ctk.CTkButton(
            frame_botones_ruta,
            text="🚀 Generar Proyecto",
            command=self.generar_estructura,
            width=150,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        btn_generar_proyecto.pack(side="left", padx=5)

        # Botones para guardar/cargar proyectos
        btn_guardar = ctk.CTkButton(
            frame_botones_ruta,
            text="💾 Guardar Proyecto",
            command=self.guardar_proyecto,
            width=150,
            height=35,
            fg_color="#4a148c",  # Morado oscuro
            hover_color="#6a0dad"
        )
        btn_guardar.pack(side="left", padx=5)

        btn_cargar = ctk.CTkButton(
            frame_botones_ruta,
            text="📂 Cargar Proyecto",
            command=self.cargar_proyecto,
            width=150,
            height=35,
            fg_color="#4a148c",  # Morado oscuro
            hover_color="#6a0dad"
        )
        btn_cargar.pack(side="left", padx=5)

        # Frame para texto y herramientas
        frame_contenido = ctk.CTkFrame(frame_principal)
        frame_contenido.pack(pady=20, padx=20, fill="both", expand=True)

        # Título de la sección de texto
        label_instrucciones = ctk.CTkLabel(
            frame_contenido,
            text="📝 Editor de Estructura:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        label_instrucciones.pack(pady=(15, 10))

        # Frame horizontal para herramientas, texto y vista previa
        frame_horizontal = ctk.CTkFrame(frame_contenido)
        frame_horizontal.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        # Panel izquierdo - Herramientas de caracteres
        frame_herramientas = ctk.CTkFrame(frame_horizontal, width=200)
        frame_herramientas.pack(side="left", fill="y", padx=(0, 10))
        frame_herramientas.pack_propagate(False)

        titulo_herramientas = ctk.CTkLabel(
            frame_herramientas,
            text="🔧 Herramientas",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        titulo_herramientas.pack(pady=(15, 10))

        # Botones para caracteres del árbol
        caracteres = [
            ("├── ", "├── Rama"),
            ("└── ", "└── Final"),
            ("│   ", "│ Línea"),
            ("    ", "Indent"),
            ("/", "/ Carpeta"),
            ("# ", "# Comentario")
        ]

        for char, descripcion in caracteres:
            btn = ctk.CTkButton(
                frame_herramientas,
                text=descripcion,
                command=lambda c=char: self.insertar_caracter(c),
                width=180,
                height=30,
                font=ctk.CTkFont(family="Courier New", size=12)
            )
            btn.pack(pady=2, padx=10)

        # Separador
        separador1 = ctk.CTkLabel(frame_herramientas, text="───────────", text_color="gray")
        separador1.pack(pady=5)

        # MENÚ DE PLANTILLAS
        self.menu_plantillas = ctk.CTkOptionMenu(
            frame_herramientas,
            values=["Seleccione una plantilla"] + list(self.plantillas.keys()),
            command=self.cargar_plantilla,
            fg_color="#8a2be2",
            button_color="#6a0dad",
            dropdown_fg_color="#8a2be2",
            dropdown_text_color="white",
            width=180,
            height=30
        )
        self.menu_plantillas.pack(pady=2, padx=10)

        # Botón "Limpiar Todo"
        btn_limpiar = ctk.CTkButton(
            frame_herramientas,
            text="🧹 Limpiar Todo",
            command=self.limpiar_texto,
            width=180,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        btn_limpiar.pack(pady=2, padx=10)

        # Panel central - Área de texto
        frame_texto = ctk.CTkFrame(frame_horizontal)
        frame_texto.pack(side="left", fill="both", expand=True)

        # Área de texto con scrollbar
        self.texto_entrada = ctk.CTkTextbox(
            frame_texto,
            height=350,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none"
        )
        self.texto_entrada.pack(pady=15, padx=15, fill="both", expand=True)

        # Panel derecho - Vista previa
        frame_vista_previa = ctk.CTkFrame(frame_horizontal, width=300)
        frame_vista_previa.pack(side="right", fill="y", padx=(10, 0))
        frame_vista_previa.pack_propagate(False)

        # Título para la vista previa
        label_vista_previa = ctk.CTkLabel(
            frame_vista_previa,
            text="👁️ Vista Previa",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label_vista_previa.pack(pady=(10, 5))

        # Área para mostrar la vista previa
        self.vista_previa = ctk.CTkTextbox(
            frame_vista_previa,
            height=350,
            font=ctk.CTkFont(family="Courier New", size=12),
            wrap="none",
            state="disabled"
        )
        self.vista_previa.pack(pady=5, padx=5, fill="both", expand=True)

        # Cargar ejemplo inicial
        self.cargar_ejemplo()

        # Frame para botones principales (bien visible)
        frame_botones_principales = ctk.CTkFrame(frame_principal)
        frame_botones_principales.pack(pady=20, padx=20, fill="x")

        # Botón GENERAR grande y visible (ya existente)
        btn_generar = ctk.CTkButton(
            frame_botones_principales,
            text="🚀 GENERAR ESTRUCTURA",
            command=self.generar_estructura,
            width=300,
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        btn_generar.pack(pady=20)

        # Footer
        footer = ctk.CTkLabel(
            self.root,
            text="💡 Tip: Usa '/' al final para carpetas, sin '/' para archivos | Usa # para comentarios",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        footer.pack(pady=(0, 10))

    def guardar_proyecto(self):
        """Guarda la estructura actual en un archivo JSON"""
        texto = self.texto_entrada.get("1.0", "end").strip()
        if not texto:
            messagebox.showwarning("Advertencia", "No hay estructura para guardar")
            return

        # Obtener ruta para guardar
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".folderstruct",
            filetypes=[("Folder Structure Files", "*.folderstruct"), ("All Files", "*.*")]
        )

        if not ruta_archivo:
            return

        try:
            # Crear un diccionario con la información a guardar
            proyecto = {
                "estructura": texto,
                "ruta_destino": self.ruta_destino,
                "fecha": datetime.datetime.now().isoformat()
            }

            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(proyecto, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Éxito", "Proyecto guardado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el proyecto: {str(e)}")

    def cargar_proyecto(self):
        """Carga una estructura desde un archivo JSON"""
        ruta_archivo = filedialog.askopenfilename(
            filetypes=[("Folder Structure Files", "*.folderstruct"), ("All Files", "*.*")]
        )

        if not ruta_archivo:
            return

        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                proyecto = json.load(f)

            # Cargar la estructura en el editor
            self.texto_entrada.delete("1.0", "end")
            self.texto_entrada.insert("1.0", proyecto.get("estructura", ""))

            # Cargar la ruta si está disponible
            if "ruta_destino" in proyecto and os.path.exists(proyecto["ruta_destino"]):
                self.ruta_destino = proyecto["ruta_destino"]
                self.label_ruta.configure(text=self.ruta_destino)

            messagebox.showinfo("Éxito", "Proyecto cargado correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el proyecto: {str(e)}")

    def actualizar_vista_previa(self, event=None):
        """Actualiza la vista previa cuando el texto cambia"""
        texto = self.texto_entrada.get("1.0", "end").strip()

        if not texto:
            self.vista_previa.configure(state="normal")
            self.vista_previa.delete("1.0", "end")
            self.vista_previa.insert("1.0", "Escribe una estructura para ver la vista previa...")
            self.vista_previa.configure(state="disabled")
            return

        try:
            estructura = self.parsear_estructura(texto)
            if not estructura:
                self.vista_previa.configure(state="normal")
                self.vista_previa.delete("1.0", "end")
                self.vista_previa.insert("1.0", "Estructura no válida")
                self.vista_previa.configure(state="disabled")
                return

            # Generar una representación visual de la estructura
            vista = self.generar_vista_previa(estructura)
            self.vista_previa.configure(state="normal")
            self.vista_previa.delete("1.0", "end")
            self.vista_previa.insert("1.0", vista)
            self.vista_previa.configure(state="disabled")

        except Exception as e:
            self.vista_previa.configure(state="normal")
            self.vista_previa.delete("1.0", "end")
            self.vista_previa.insert("1.0", f"Error al generar vista previa:\n{str(e)}")
            self.vista_previa.configure(state="disabled")

    def generar_vista_previa(self, estructura):
        """Genera una representación visual de la estructura"""
        if not estructura:
            return "Estructura vacía"

        # Crear una representación visual con indentación
        resultado = []
        for item in estructura:
            indent = "    " * item['nivel']
            if item['es_carpeta']:
                resultado.append(f"{indent}📁 {item['nombre']}/")
            else:
                resultado.append(f"{indent}📄 {item['nombre']}")

        return "\n".join(resultado)

    def actualizar_vista_previa_periodicamente(self):
        """Actualiza la vista previa cada 5 segundos"""
        def actualizar():
            while True:
                self.actualizar_vista_previa()
                threading.Event().wait(5)

        threading.Thread(target=actualizar, daemon=True).start()

    def cargar_plantilla(self, nombre_plantilla):
        """Carga una plantilla seleccionada desde el menú"""
        if nombre_plantilla == "Seleccione una plantilla":
            return

        ejemplo = self.plantillas.get(nombre_plantilla, "")
        self.texto_entrada.delete("1.0", "end")
        self.texto_entrada.insert("1.0", ejemplo)

    def insertar_caracter(self, caracter):
        """Inserta un carácter en la posición del cursor"""
        try:
            # Obtener posición actual del cursor
            cursor_pos = self.texto_entrada.index("insert")

            # Insertar el carácter
            self.texto_entrada.insert(cursor_pos, caracter)

            # Mantener el foco en el área de texto
            self.texto_entrada.focus_set()
        except:
            # Si hay error, insertar al final
            self.texto_entrada.insert("end", caracter)

    def cargar_ejemplo(self):
        """Carga un ejemplo en el área de texto"""
        ejemplo = """mi-proyecto/
├── src/                   # Código fuente
│   ├── components/        # Componentes React
│   │   ├── Header.jsx     # Cabecera
│   │   └── Footer.jsx     # Pie de página
│   ├── pages/             # Páginas
│   │   ├── Home.jsx       # Página principal
│   │   └── About.jsx      # Acerca de
│   ├── utils/             # Utilidades
│   │   └── helpers.js     # Funciones auxiliares
│   └── App.jsx            # Componente principal
├── public/                # Archivos públicos
│   ├── index.html         # HTML base
│   ├── favicon.ico        # Icono
│   └── images/            # Imágenes
│       ├── logo.png       # Logo
│       └── banner.jpg     # Banner
├── docs/                  # Documentación
│   ├── README.md          # Documentación principal
│   └── API.md             # Documentación API
├── package.json           # Configuración npm
├── .gitignore             # Archivos ignorados por Git
└── LICENSE                # Licencia del proyecto"""

        self.texto_entrada.delete("1.0", "end")
        self.texto_entrada.insert("1.0", ejemplo)

    def limpiar_texto(self):
        """Limpia el área de texto"""
        self.texto_entrada.delete("1.0", "end")

    def cambiar_ruta(self):
        """Permite seleccionar nueva ruta"""
        nueva_ruta = filedialog.askdirectory(initialdir=self.ruta_destino)
        if nueva_ruta:
            self.ruta_destino = nueva_ruta
            self.label_ruta.configure(text=self.ruta_destino)

    def parsear_estructura(self, texto):
        """Parsea la estructura usando indentación real"""
        lineas = texto.strip().split('\n')
        estructura = []
        stack_padres = []

        for linea in lineas:
            if not linea.strip():
                continue

            # Calcular indentación real
            contenido_match = re.search(r'[^│├└─\s]', linea)
            if not contenido_match:
                continue

            indentacion = contenido_match.start()
            contenido = linea[indentacion:].strip()

            if not contenido:
                continue

            # Separar nombre del comentario
            if '#' in contenido:
                nombre_parte = contenido.split('#')[0].strip()
                comentario = contenido.split('#')[1].strip()
            else:
                nombre_parte = contenido
                comentario = ""

            # Determinar si es carpeta
            es_carpeta = nombre_parte.endswith('/')
            nombre = nombre_parte.rstrip('/')

            if not nombre:
                continue

            # Calcular nivel
            nivel = indentacion // 4

            # Ajustar stack
            while len(stack_padres) > nivel:
                stack_padres.pop()

            # Construir ruta
            if nivel == 0:
                ruta_completa = nombre
                stack_padres = [nombre]
            else:
                ruta_completa = os.path.join(*stack_padres, nombre)
                if es_carpeta:
                    stack_padres.append(nombre)

            estructura.append({
                'nombre': nombre,
                'ruta_completa': ruta_completa,
                'nivel': nivel,
                'es_carpeta': es_carpeta,
                'comentario': comentario
            })

        return estructura

    def crear_carpetas_y_archivos(self, estructura, texto_original):
        """Crea la estructura de carpetas y archivos"""
        try:
            rutas_creadas = []
            proyecto_raiz = None

            for item in estructura:
                ruta_completa = os.path.join(self.ruta_destino, item['ruta_completa'])

                if item['nivel'] == 0:
                    proyecto_raiz = item['nombre']

                if item['es_carpeta']:
                    if not os.path.exists(ruta_completa):
                        os.makedirs(ruta_completa)
                        rutas_creadas.append(f"📁 {item['ruta_completa']}/")
                else:
                    directorio = os.path.dirname(ruta_completa)
                    if directorio and not os.path.exists(directorio):
                        os.makedirs(directorio)

                    if not os.path.exists(ruta_completa):
                        with open(ruta_completa, 'w', encoding='utf-8') as f:
                            if item['comentario']:
                                f.write(f"// {item['comentario']}\n")
                        rutas_creadas.append(f"📄 {item['ruta_completa']}")

            # Crear README.md
            if proyecto_raiz:
                readme_path = os.path.join(self.ruta_destino, proyecto_raiz, 'README.md')
                if not any(item['nombre'] == 'README.md' for item in estructura):
                    with open(readme_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {proyecto_raiz.title()}\n\n")
                        f.write("## Estructura del Proyecto\n\n")
                        f.write("```\n")
                        f.write(texto_original)
                        f.write("\n```\n")

                    rutas_creadas.append(f"📄 {proyecto_raiz}/README.md")

            return rutas_creadas, proyecto_raiz

        except Exception as e:
            raise Exception(f"Error al crear estructura: {str(e)}")

    def generar_estructura(self):
        """Función principal para generar carpetas y archivos"""
        texto = self.texto_entrada.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("⚠️ Advertencia", "Por favor, ingresa una estructura de carpetas.")
            return

        try:
            if not os.path.exists(self.ruta_destino):
                messagebox.showerror("❌ Error", f"La ruta no existe: {self.ruta_destino}")
                return

            estructura = self.parsear_estructura(texto)

            if not estructura:
                messagebox.showwarning("⚠️ Advertencia", "No se pudo interpretar la estructura.")
                return

            # Preview más compacto
            total_carpetas = sum(1 for item in estructura if item['es_carpeta'])
            total_archivos = sum(1 for item in estructura if not item['es_carpeta'])

            preview = f"🎯 Se creará:\n\n"
            preview += f"📁 {total_carpetas} carpetas\n"
            preview += f"📄 {total_archivos} archivos\n\n"
            preview += f"📍 En: {self.ruta_destino}\n\n"
            preview += "¿Continuar con la creación?"

            if not messagebox.askyesno("🚀 Confirmar Creación", preview):
                return

            # Crear estructura
            rutas_creadas, proyecto_raiz = self.crear_carpetas_y_archivos(estructura, texto)

            # Mensaje de éxito
            mensaje = f"🎉 ¡Estructura creada exitosamente!\n\n"
            mensaje += f"📁 Proyecto: {proyecto_raiz}\n"
            mensaje += f"📍 Ubicación: {self.ruta_destino}\n"
            mensaje += f"📊 Total: {len(rutas_creadas)} elementos\n"

            messagebox.showinfo("✅ Éxito", mensaje)

        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def ejecutar(self):
        self.root.mainloop()

def main():
    app = GeneradorEstructura()
    app.ejecutar()

if __name__ == "__main__":
    main()