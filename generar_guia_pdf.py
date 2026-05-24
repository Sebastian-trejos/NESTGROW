from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Colores ──────────────────────────────────────────────────────────────────
AZUL_OSCURO  = colors.HexColor("#1a237e")
AZUL_MEDIO   = colors.HexColor("#3949ab")
AZUL_CLARO   = colors.HexColor("#e8eaf6")
VERDE        = colors.HexColor("#2e7d32")
GRIS_TEXTO   = colors.HexColor("#37474f")
GRIS_CLARO   = colors.HexColor("#f5f5f5")
GRIS_BORDE   = colors.HexColor("#bdbdbd")
NARANJA      = colors.HexColor("#e65100")
BLANCO       = colors.white

# ── Estilos ───────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

s_titulo = ParagraphStyle(
    "Titulo",
    fontSize=22, fontName="Helvetica-Bold",
    textColor=AZUL_OSCURO, spaceAfter=6, spaceBefore=0,
    alignment=TA_CENTER, leading=28,
)
s_subtitulo = ParagraphStyle(
    "Subtitulo",
    fontSize=11, fontName="Helvetica",
    textColor=AZUL_MEDIO, spaceAfter=16, spaceBefore=0,
    alignment=TA_CENTER,
)
s_h2 = ParagraphStyle(
    "H2",
    fontSize=13, fontName="Helvetica-Bold",
    textColor=BLANCO, spaceAfter=6, spaceBefore=14,
    leftIndent=0, leading=18,
)
s_h3 = ParagraphStyle(
    "H3",
    fontSize=10.5, fontName="Helvetica-Bold",
    textColor=AZUL_OSCURO, spaceAfter=4, spaceBefore=10,
    leftIndent=0,
)
s_normal = ParagraphStyle(
    "Normal2",
    fontSize=9, fontName="Helvetica",
    textColor=GRIS_TEXTO, spaceAfter=4, leading=13,
)
s_nota = ParagraphStyle(
    "Nota",
    fontSize=8.5, fontName="Helvetica-Oblique",
    textColor=VERDE, spaceAfter=6, spaceBefore=4,
    leftIndent=10, borderPad=4,
)
s_tip = ParagraphStyle(
    "Tip",
    fontSize=8.5, fontName="Helvetica-Oblique",
    textColor=NARANJA, spaceAfter=10, spaceBefore=4,
    leftIndent=10,
)
s_code_cell = ParagraphStyle(
    "CodeCell",
    fontSize=7.8, fontName="Courier",
    textColor=colors.HexColor("#212121"), leading=11,
)
s_label_cell = ParagraphStyle(
    "LabelCell",
    fontSize=8.5, fontName="Helvetica",
    textColor=GRIS_TEXTO, leading=12,
)
s_header_cell = ParagraphStyle(
    "HeaderCell",
    fontSize=8.5, fontName="Helvetica-Bold",
    textColor=BLANCO, leading=12,
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def h2_block(texto):
    """Encabezado H2 con fondo azul."""
    tabla = Table(
        [[Paragraph(texto, s_h2)]],
        colWidths=[17 * cm],
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL_MEDIO),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    return tabla


def make_table(rows, col_labels=("Archivo", "Ruta")):
    """Tabla de 2 columnas con encabezado azul."""
    header = [Paragraph(c, s_header_cell) for c in col_labels]
    data = [header]
    for label, code in rows:
        data.append([
            Paragraph(label, s_label_cell),
            Paragraph(f"<font name='Courier' size='7.8'>{code}</font>", s_label_cell),
        ])
    t = Table(data, colWidths=[5.5 * cm, 11.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_OSCURO),
        ("BACKGROUND",    (0, 1), (-1, -1), GRIS_CLARO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRIS_BORDE),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def make_resumen_table(rows):
    """Tabla de resumen rápido con columnas anchas iguales."""
    header = [Paragraph("Quiero editar...", s_header_cell),
              Paragraph("Archivos mínimos", s_header_cell)]
    data = [header]
    for quiero, archivos in rows:
        data.append([
            Paragraph(quiero, s_label_cell),
            Paragraph(f"<font name='Courier' size='7.5'>{archivos}</font>", s_label_cell),
        ])
    t = Table(data, colWidths=[5.5 * cm, 11.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  AZUL_OSCURO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, GRIS_BORDE),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def hr():
    return HRFlowable(width="100%", thickness=0.5, color=GRIS_BORDE, spaceAfter=6, spaceBefore=4)


def sp(h=6):
    return Spacer(1, h)


# ── Contenido ─────────────────────────────────────────────────────────────────
story = []

# Portada / encabezado
story += [
    sp(10),
    Paragraph("Guia de Archivos para Edicion con IA", s_titulo),
    Paragraph("NestGrow — Referencia para editar modulos sin enviar el ZIP completo", s_subtitulo),
    hr(),
    sp(4),
    Paragraph(
        "Como usar esta guia: cuando vayas a pedirle algo a una IA sin soporte ZIP, "
        "copia y pega el contenido de los archivos listados en la seccion correspondiente. "
        "Siempre incluye el <b>Contexto base</b> + los archivos del modulo que vas a editar.",
        s_nota,
    ),
    sp(10),
]

# ── CONTEXTO BASE ─────────────────────────────────────────────────────────────
story += [
    h2_block("CONTEXTO BASE — Incluir SIEMPRE"),
    sp(6),
    Paragraph("Estos archivos dan contexto general del proyecto. Pegalos al inicio de cualquier conversacion:", s_normal),
    sp(4),
    make_table([
        ("CLAUDE.md",                   "CLAUDE.md"),
        ("Template base",               "templates/base.html"),
        ("Modelos de usuarios",         "apps/accounts/models.py"),
        ("Modelos de minijuegos",       "apps/games/models.py"),
    ], col_labels=("Archivo", "Ruta")),
    sp(4),
    Paragraph(
        "Excepcion: si solo vas a editar una template de visual puro (colores, textos, layout) "
        "sin tocar logica, puedes omitir los dos models.py.",
        s_nota,
    ),
    sp(8),
]

# ── MODULO 1 — Cuentas ────────────────────────────────────────────────────────
story += [h2_block("MODULO 1 — Autenticacion y Cuentas  (/accounts/)"), sp(6)]

story += [
    Paragraph("1a. Login / Registro", s_h3),
    make_table([
        ("Vistas",           "apps/accounts/views.py"),
        ("Formularios",      "apps/accounts/forms.py"),
        ("URLs",             "apps/accounts/urls.py"),
        ("Template login",   "apps/accounts/templates/accounts/login.html"),
        ("Template registro","apps/accounts/templates/accounts/registro.html"),
    ]),
    sp(6),
    Paragraph("1b. Perfiles de usuario (editar perfil)", s_h3),
    make_table([
        ("Modelos",              "apps/accounts/models.py"),
        ("Vistas",               "apps/accounts/views.py"),
        ("Formularios",          "apps/accounts/forms.py"),
        ("Template estudiante",  "apps/accounts/templates/accounts/editar_perfil_estudiante.html"),
        ("Template profesor",    "apps/accounts/templates/accounts/editar_perfil_profesor.html"),
    ]),
    sp(6),
    Paragraph("1c. Salones (crear, ver, gestionar)", s_h3),
    make_table([
        ("Modelos",          "apps/accounts/models.py"),
        ("Vistas",           "apps/accounts/views.py"),
        ("Template detalle", "apps/accounts/templates/accounts/detalle_salon.html"),
        ("Template form",    "apps/accounts/templates/accounts/salon_form.html"),
        ("Template unirse",  "apps/accounts/templates/accounts/unirse_clase.html"),
    ]),
    sp(6),
    Paragraph("1d. Sistema de niveles, huesos y puntos", s_h3),
    make_table([
        ("Modelos (EstudianteProfile, HuesoTransaccion)", "apps/accounts/models.py"),
        ("Modelos (Score, UserProgress)",                 "apps/games/models.py"),
        ("Senales",                                       "apps/accounts/signals.py"),
    ]),
    sp(8),
]

# ── MODULO 2 — Dashboards ─────────────────────────────────────────────────────
story += [h2_block("MODULO 2 — Dashboards"), sp(6)]
story += [
    Paragraph("2a. Dashboard Estudiante", s_h3),
    make_table([
        ("Vistas",    "apps/accounts/views.py"),
        ("Template",  "apps/accounts/templates/accounts/dashboard_estudiante.html"),
    ]),
    sp(6),
    Paragraph("2b. Dashboard Profesor", s_h3),
    make_table([
        ("Vistas",    "apps/accounts/views.py"),
        ("Template",  "apps/accounts/templates/accounts/dashboard_profesor.html"),
    ]),
    sp(8),
]

# ── MODULO 3 — Minijuegos ─────────────────────────────────────────────────────
story += [h2_block("MODULO 3 — Minijuegos  (/juegos/)"), sp(6)]
story += [
    Paragraph("3a. Logica general de minijuegos (puntaje, guardado)", s_h3),
    make_table([
        ("Modelos",                  "apps/games/models.py"),
        ("Vistas (save_score, etc)", "apps/games/views.py"),
        ("URLs",                     "apps/games/urls.py"),
        ("JS puntaje",               "apps/games/static/games/js/score_utils.js"),
        ("CSS compartido",           "apps/games/static/games/css/games.css"),
    ]),
    sp(6),
    Paragraph("3b. Lista de Minijuegos (/juegos/)", s_h3),
    make_table([
        ("Vistas",   "apps/games/views.py"),
        ("Template", "apps/games/templates/games/game_list.html"),
    ]),
    sp(6),
]

minijuegos = [
    ("3c. Drag & Drop",     [("Template","apps/games/templates/games/drag_and_drop.html"),
                              ("JS","apps/games/static/games/js/drag_and_drop.js"),
                              ("Logica Python","apps/games/game_logic/drag_and_drop.py")]),
    ("3d. Sopa de Letras",  [("Template","apps/games/templates/games/word_search.html"),
                              ("JS","apps/games/static/games/js/word_search.js"),
                              ("Logica Python","apps/games/game_logic/word_search.py")]),
    ("3e. Memoria",         [("Template","apps/games/templates/games/memoria.html"),
                              ("JS","apps/games/static/games/js/memoria.js")]),
    ("3f. Puzzle",          [("Template","apps/games/templates/games/puzzle.html"),
                              ("JS","apps/games/static/games/js/puzzle.js")]),
    ("3g. Audio Matching",  [("Template","apps/games/templates/games/audio_game.html"),
                              ("JS","apps/games/static/games/js/audio_game.js"),
                              ("Logica Python","apps/games/game_logic/audio_matching.py")]),
    ("3h. Ahorcado",        [("Template","apps/games/templates/games/ahorcado.html")]),
    ("3i. Quiz",            [("Template","apps/games/templates/games/quiz.html")]),
    ("3j. Globos",          [("Template","apps/games/templates/games/globos.html")]),
    ("3k. Ordenar Letras",  [("Template","apps/games/templates/games/ordenar_letras.html")]),
    ("3l. Pintura",         [("Template","apps/games/templates/games/painting.html")]),
    ("3m. Comparacion",     [("Template","apps/games/templates/games/comparacion.html"),
                              ("JS","apps/games/static/games/js/comparacion.js")]),
]
for titulo, filas in minijuegos:
    story += [Paragraph(titulo, s_h3), make_table(filas), sp(6)]

story += [sp(4)]

# ── MODULO 4 — Talleres ───────────────────────────────────────────────────────
story += [h2_block("MODULO 4 — Talleres  (/talleres/)"), sp(6)]
story += [
    Paragraph("4a. CRUD de Talleres (crear/editar taller, bloques)", s_h3),
    make_table([
        ("Modelos",               "apps/talleres/models.py"),
        ("Vistas",                "apps/talleres/views.py"),
        ("Formularios",           "apps/talleres/forms.py"),
        ("URLs",                  "apps/talleres/urls.py"),
        ("Template lista",        "apps/talleres/templates/talleres/profesor/lista.html"),
        ("Template form taller",  "apps/talleres/templates/talleres/profesor/form.html"),
        ("Template preview",      "apps/talleres/templates/talleres/profesor/preview.html"),
    ]),
    sp(6),
    Paragraph("4b. Sistema de Periodos", s_h3),
    make_table([
        ("Modelos",                  "apps/talleres/models.py"),
        ("Vistas",                   "apps/talleres/views.py"),
        ("Formularios",              "apps/talleres/forms.py"),
        ("Template crear periodo",   "apps/talleres/templates/talleres/profesor/crear_periodo.html"),
        ("Template editar periodo",  "apps/talleres/templates/talleres/profesor/editar_periodo.html"),
        ("Template lista periodos",  "apps/talleres/templates/talleres/profesor/lista_periodos.html"),
        ("Template resultados",      "apps/talleres/templates/talleres/profesor/resultados_periodo.html"),
    ]),
    sp(6),
    Paragraph('4c. Panel Estudiante — "Mis Actividades"', s_h3),
    make_table([
        ("Modelos",               "apps/talleres/models.py"),
        ("Vistas",                "apps/talleres/views.py"),
        ("Template mis talleres", "apps/talleres/templates/talleres/estudiante/mis_talleres.html"),
        ("Template resolver",     "apps/talleres/templates/talleres/estudiante/resolver.html"),
        ("Template resultado",    "apps/talleres/templates/talleres/estudiante/resultado_sesion.html"),
    ]),
    sp(8),
]

# ── MODULO 5 — Historia ───────────────────────────────────────────────────────
story += [h2_block("MODULO 5 — Historia  (/historia/)"), sp(6)]
story += [
    Paragraph("5a. Mapa de Historia (estudiante)", s_h3),
    make_table([
        ("Modelos",       "apps/historia/models.py"),
        ("Vistas",        "apps/historia/views.py"),
        ("URLs",          "apps/historia/urls.py"),
        ("Template mapa", "apps/historia/templates/historia/mapa.html"),
    ]),
    sp(6),
    Paragraph("5b. Reproductor de Leccion", s_h3),
    make_table([
        ("Vistas",           "apps/historia/views.py"),
        ("Template leccion", "apps/historia/templates/historia/leccion.html"),
    ]),
    sp(6),
    Paragraph("5c. Servicios y Logros de Historia", s_h3),
    make_table([
        ("Servicios (logros)", "apps/historia/services.py"),
        ("Senales",            "apps/historia/signals.py"),
        ("Fixture logros",     "apps/historia/fixtures/logros_historia.json"),
    ]),
    sp(6),
    Paragraph("5d. Panel Profesor — Historia", s_h3),
    make_table([
        ("Vistas",                  "apps/historia/views.py"),
        ("Template panel",          "apps/historia/templates/historia/profesor/panel.html"),
        ("Template progreso sec.",  "apps/historia/templates/historia/profesor/progreso_seccion.html"),
    ]),
    sp(6),
    Paragraph("5e. Datos del contenido de Historia (secciones, lecciones)", s_h3),
    make_table([
        ("Fixture contenido",   "apps/historia/fixtures/modo_historia.json"),
        ("Generador fixture",   "apps/historia/management/commands/generate_historia_fixture.py"),
        ("Seed command",        "apps/historia/management/commands/seed_historia.py"),
    ]),
    sp(8),
]

# ── MODULO 6 — Tienda / Habitacion / Museo ────────────────────────────────────
story += [h2_block("MODULO 6 — Tienda, Habitacion y Museo  (/juegos/)"), sp(6)]
story += [
    Paragraph("6a. Tienda (Tienda de Huesos)", s_h3),
    make_table([
        ("Modelos (TiendaItem, Inventario)", "apps/games/models.py"),
        ("Vistas",                           "apps/games/views.py"),
        ("Template",                         "apps/games/templates/games/tienda.html"),
    ]),
    sp(6),
    Paragraph("6b. Habitacion de Milo", s_h3),
    make_table([
        ("Vistas",   "apps/games/views.py"),
        ("Template", "apps/games/templates/games/habitacion_milo.html"),
    ]),
    sp(6),
    Paragraph("6c. Museo Virtual", s_h3),
    make_table([
        ("Vistas",                  "apps/games/views.py"),
        ("Template museo estudiante","apps/games/templates/games/museo_virtual.html"),
        ("Template museo global",   "apps/games/templates/games/museo_global.html"),
    ]),
    sp(6),
    Paragraph("6d. Logros", s_h3),
    make_table([
        ("Modelos",  "apps/games/models.py"),
        ("Vistas",   "apps/games/views.py"),
        ("Template", "apps/games/templates/games/mis_logros.html"),
    ]),
    sp(6),
    Paragraph("6e. Ranking del Salon", s_h3),
    make_table([
        ("Vistas",   "apps/games/views.py"),
        ("Template", "apps/games/templates/games/ranking_salon.html"),
    ]),
    sp(8),
]

# ── MODULO 7 — Vocabulario ────────────────────────────────────────────────────
story += [h2_block("MODULO 7 — Vocabulario y Contenido  (/contenido/)"), sp(6)]
story += [
    Paragraph("7a. Categorias y vocabulario", s_h3),
    make_table([
        ("Modelos",          "apps/content/models.py"),
        ("Vistas",           "apps/content/views.py"),
        ("Formularios",      "apps/content/forms.py"),
        ("URLs",             "apps/content/urls.py"),
        ("Template lista",   "apps/content/templates/content/category_list.html"),
        ("Template detalle", "apps/content/templates/content/vocabulary_detail.html"),
        ("Template mi voc.", "apps/content/templates/content/mi_vocabulario.html"),
    ]),
    sp(6),
    Paragraph("7b. Gestion de vocabulario (panel profesor)", s_h3),
    make_table([
        ("Vistas (games)",          "apps/games/views.py"),
        ("Template categorias",     "apps/games/templates/games/profesor/gestionar_categorias.html"),
        ("Template vocabulario",    "apps/games/templates/games/profesor/gestionar_vocabulario.html"),
        ("Template juegos",         "apps/games/templates/games/profesor/gestionar_juegos.html"),
        ("Template form juego",     "apps/games/templates/games/profesor/juego_form.html"),
    ]),
    sp(8),
]

# ── MODULO 8 — Asistente IA ───────────────────────────────────────────────────
story += [h2_block("MODULO 8 — Asistente IA  (/asistente/)"), sp(6)]
story += [
    make_table([
        ("Modelos",              "apps/asistente/models.py"),
        ("Vistas",               "apps/asistente/views.py"),
        ("Servicios (llamada IA)","apps/asistente/services.py"),
        ("URLs",                 "apps/asistente/urls.py"),
        ("Template",             "apps/asistente/templates/asistente/index.html"),
    ]),
    sp(8),
]

# ── MODULO 9 — Config Global ──────────────────────────────────────────────────
story += [h2_block("MODULO 9 — Configuracion Global"), sp(6)]
story += [
    Paragraph("9a. Settings / Configuracion del proyecto", s_h3),
    make_table([
        ("Settings compartidos", "config/settings/base.py"),
        ("URLs raiz",            "config/urls.py"),
    ]),
    sp(6),
    Paragraph("9b. Estilos y JS globales", s_h3),
    make_table([
        ("CSS global",        "static/css/style.css"),
        ("JS global",         "static/js/main.js"),
        ("JS utilidades Milo","static/js/milo-utils.js"),
        ("Template base",     "templates/base.html"),
    ]),
    sp(6),
    Paragraph("9c. Notificaciones en tiempo real (WebSockets)", s_h3),
    make_table([
        ("Consumer WebSocket", "apps/core/consumers.py"),
        ("Routing",            "apps/core/routing.py"),
        ("Context processors", "apps/core/context_processors.py"),
    ]),
    sp(8),
]

# ── TABLA RESUMEN RAPIDO ──────────────────────────────────────────────────────
story += [
    PageBreak(),
    h2_block("TABLA RESUMEN RAPIDO"),
    sp(8),
    make_resumen_table([
        ("Pantalla de login/registro",     "accounts/views.py  +  accounts/forms.py  +  template"),
        ("Dashboard estudiante",           "accounts/views.py  +  dashboard_estudiante.html"),
        ("Dashboard profesor",             "accounts/views.py  +  dashboard_profesor.html"),
        ("Un minijuego especifico",        "Template del juego  +  JS del juego (si existe)"),
        ("Guardar puntaje de minijuego",   "games/views.py  +  games/models.py  +  score_utils.js"),
        ("Crear / editar un taller",       "talleres/models.py  +  views.py  +  forms.py  +  template"),
        ("Sistema de Periodos",            "talleres/models.py  +  views.py  +  templates de periodos"),
        ('Panel "Mis Actividades"',        "talleres/views.py  +  mis_talleres.html"),
        ("Mapa de Historia",               "historia/views.py  +  mapa.html"),
        ("Leccion de Historia",            "historia/views.py  +  leccion.html"),
        ("Contenido de Historia (datos)",  "fixtures/modo_historia.json  +  generate_historia_fixture.py"),
        ("Tienda",                         "games/models.py  +  games/views.py  +  tienda.html"),
        ("Habitacion de Milo",             "games/views.py  +  habitacion_milo.html"),
        ("Niveles y huesos",               "accounts/models.py  +  accounts/signals.py"),
        ("Estilos visuales globales",      "static/css/style.css  +  templates/base.html"),
        ("Configuracion / settings",       "config/settings/base.py"),
        ("Agregar nueva URL",              "config/urls.py  +  urls.py del modulo correspondiente"),
    ]),
    sp(12),
    Paragraph(
        "Tip: si cambias models.py, recuerda ejecutar "
        "'python manage.py makemigrations && python manage.py migrate' despues. "
        "Si cambias una fixture, recargala con 'python manage.py loaddata &lt;archivo&gt;'.",
        s_tip,
    ),
]

# ── Build PDF ─────────────────────────────────────────────────────────────────
output_path = "GUIA_ARCHIVOS_IA.pdf"

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=2 * cm,
    rightMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
    title="Guia de Archivos para Edicion con IA — NestGrow",
    author="NestGrow",
)

doc.build(story)
print(f"PDF generado: {output_path}")
