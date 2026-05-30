"""
PDF generation for student reports using reportlab.
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable,
                                 Image as RLImage)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.graphics.shapes import Drawing, Rect
from datetime import date

# ── Rutas de assets estáticos ─────────────────────────────────────────────────
_BASE = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'img')
)


def _milo(nombre):
    """Devuelve la ruta absoluta de un asset Milo si existe, o None."""
    p = os.path.join(_BASE, nombre)
    return p if os.path.isfile(p) else None


def _milo_img(nombre, ancho=3.2*cm, alto=3.5*cm):
    """Devuelve un flowable RLImage de Milo o un Spacer si el archivo no existe."""
    p = _milo(nombre)
    return RLImage(p, width=ancho, height=alto) if p else Spacer(ancho, alto)


def _milo_segun_nota(nota):
    """Elige el nombre del PNG de Milo apropiado para la nota dada."""
    if nota is None:
        return 'milo_apuntes.png'
    if nota >= 4.5:
        return 'milo_aplaudiendo.png'
    if nota >= 4.0:
        return 'milo_orgulloso.png'
    if nota >= 3.5:
        return 'milo_pulgar.png'
    if nota >= 3.0:
        return 'milo_leyendo1.png'
    return 'milo_preocupado.png'


def _decorar_pagina(canvas, doc):
    """Dibuja el fondo decorativo en cada página del informe."""
    canvas.saveState()
    pw, ph = A4

    # ── Franjas de color top / bottom ────────────────────────────────────────
    canvas.setFillColor(colors.HexColor('#6C63FF'))
    canvas.rect(0, ph - 7, pw, 7, fill=1, stroke=0)

    canvas.setFillColor(colors.HexColor('#4ECDC4'))
    canvas.rect(0, 0, pw, 5, fill=1, stroke=0)

    # ── Burbuja grande esquina superior-derecha ───────────────────────────────
    canvas.setFillColor(colors.HexColor('#EDE9FF'))
    canvas.circle(pw + 10, ph + 10, 130, fill=1, stroke=0)

    # ── Burbuja grande esquina inferior-izquierda ────────────────────────────
    canvas.setFillColor(colors.HexColor('#E0FBF9'))
    canvas.circle(-10, -10, 100, fill=1, stroke=0)

    # ── Círculos pequeños de acento en los márgenes ───────────────────────────
    canvas.setFillColor(colors.HexColor('#FFD166'))
    canvas.circle(pw - 18, ph * 0.58, 14, fill=1, stroke=0)

    canvas.setFillColor(colors.HexColor('#FF6B6B'))
    canvas.circle(18, ph * 0.30, 10, fill=1, stroke=0)

    canvas.setFillColor(colors.HexColor('#6C63FF'))
    canvas.circle(pw - 14, ph * 0.22, 7, fill=1, stroke=0)

    canvas.setFillColor(colors.HexColor('#4ECDC4'))
    canvas.circle(14, ph * 0.72, 6, fill=1, stroke=0)

    canvas.restoreState()


def calcular_nota(pct):
    """Convert percentage to Colombian 1-5 grade."""
    if pct >= 90: return 5.0
    elif pct >= 80: return 4.5
    elif pct >= 70: return 4.0
    elif pct >= 60: return 3.5
    elif pct >= 50: return 3.0
    elif pct >= 40: return 2.5
    else: return 2.0


def calcular_ranking(estudiante):
    """Get student's current ranking position in their salon."""
    if not estudiante.salon:
        return None, None
    from apps.accounts.models import EstudianteProfile
    compañeros = sorted(
        EstudianteProfile.objects.filter(salon=estudiante.salon).all(),
        key=lambda p: p.puntos_acumulados,
        reverse=True,
    )
    total = len(compañeros)
    for i, c in enumerate(compañeros, 1):
        if c.pk == estudiante.pk:
            return i, total
    return None, total


def _nota_color(nota, green, yellow, red):
    if nota >= 4.0:
        return green
    elif nota >= 3.0:
        return yellow
    return red


def generar_pdf_informe(estudiante, progreso, talleres_data):
    """
    Generate a PDF report for a student and return bytes.

    progreso      — QuerySet of UserProgress (minijuegos individuales)
    talleres_data — list of dicts: [{'sesion': SesionTaller, 'nota_info': dict|None}]
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    PRIMARY = colors.HexColor('#6C63FF')
    ACCENT  = colors.HexColor('#4ECDC4')
    LIGHT   = colors.HexColor('#F8F6FF')
    GREEN   = colors.HexColor('#d4edda')
    YELLOW  = colors.HexColor('#fff3cd')
    RED     = colors.HexColor('#f8d7da')
    GREY    = colors.HexColor('#f5f5f5')

    title_style = ParagraphStyle(
        'NestTitle', parent=styles['Title'],
        textColor=PRIMARY, fontSize=22, spaceAfter=4,
        fontName='Helvetica-Bold', alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        'NestSub', parent=styles['Normal'],
        textColor=colors.HexColor('#666666'), fontSize=11,
        alignment=TA_CENTER, spaceAfter=2,
    )
    section_style = ParagraphStyle(
        'NestSection', parent=styles['Heading2'],
        textColor=PRIMARY, fontSize=13,
        fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        'NestNormal', parent=styles['Normal'],
        fontSize=10, leading=14,
    )
    footer_style = ParagraphStyle(
        'footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph('NestGrow', title_style))
    story.append(Paragraph('Plataforma de Aprendizaje de Ingles', subtitle_style))
    story.append(Paragraph(
        f'Informe de Desempeno - {date.today().strftime("%d de %B de %Y")}',
        subtitle_style,
    ))
    story.append(HRFlowable(width='100%', thickness=3, color=PRIMARY, spaceAfter=16))

    # ── Calcular nota promedio de talleres ───────────────────────────────────
    notas_talleres = [
        d['nota_info']['nota']
        for d in talleres_data
        if d['nota_info'] and d['sesion'].completada
    ]
    nota_general = (
        round(sum(notas_talleres) / len(notas_talleres), 1)
        if notas_talleres else None
    )

    # ── Student Info ─────────────────────────────────────────────────────────
    story.append(Paragraph('Informacion del Estudiante', section_style))

    nombre        = estudiante.user.get_full_name() or estudiante.user.username
    salon_nombre  = estudiante.salon.nombre if estudiante.salon else '-'
    grado         = estudiante.get_grado_display() if estudiante.grado else '-'
    identidad     = (f'N° Lista: {estudiante.numero_lista}') if estudiante.numero_lista else '-'
    profesor_nom  = (
        estudiante.salon.profesor.user.get_full_name()
        if estudiante.salon else '-'
    )
    ranking_pos, ranking_total = calcular_ranking(estudiante)
    ranking_str   = f'{ranking_pos} de {ranking_total} estudiantes' if ranking_pos else '-'
    talleres_comp = sum(1 for d in talleres_data if d['sesion'].completada)
    juegos_jugados = progreso.count()

    info_data = [
        ['Nombre completo:', nombre,         'Grado:',          grado],
        ['N Identidad:',    identidad,       'Salon:',          salon_nombre],
        ['Profesor/a:',     profesor_nom,    'Ranking salon:',  ranking_str],
        ['Talleres completados:', str(talleres_comp),
         'Juegos jugados:', str(juegos_jugados)],
    ]
    if nota_general:
        info_data.append(['Nota promedio talleres:', f'{nota_general} / 5.0', '', ''])

    info_table = Table(info_data, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), LIGHT),
        ('TEXTCOLOR',    (0, 0), (0, -1),  PRIMARY),
        ('TEXTCOLOR',    (2, 0), (2, -1),  PRIMARY),
        ('FONTNAME',     (0, 0), (0, -1),  'Helvetica-Bold'),
        ('FONTNAME',     (2, 0), (2, -1),  'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT, colors.white]),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
        ('PADDING',      (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ── Nota General (basada en talleres) ────────────────────────────────────
    if nota_general:
        nota_color = _nota_color(nota_general, GREEN, YELLOW, RED)
        ng_data = [[f'Nota General del Periodo (talleres): {nota_general} / 5.0']]
        ng_table = Table(ng_data, colWidths=[18*cm])
        ng_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), nota_color),
            ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 13),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('PADDING',    (0, 0), (-1, -1), 12),
            ('GRID',       (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ]))
        story.append(ng_table)
        story.append(Spacer(1, 16))

    # ── Desempeno en Talleres ────────────────────────────────────────────────
    story.append(Paragraph('Desempeno en Talleres', section_style))

    if talleres_data:
        t_header = ['Taller', 'Nota', 'Correctas / Total', 'Estado', 'Fecha']
        t_rows = [t_header]
        for d in talleres_data:
            sesion = d['sesion']
            ni = d['nota_info']
            if ni:
                nota_str     = f"{ni['nota']:.1f}"
                correctas_str = f"{ni['correctas']} / {ni['total']} ({ni['pct']}%)"
            else:
                nota_str      = '-'
                correctas_str = 'Sin preguntas calificables'
            estado = 'Completado' if sesion.completada else 'En progreso'
            fecha  = (
                sesion.completada_en.strftime('%d/%m/%Y')
                if sesion.completada and sesion.completada_en else '-'
            )
            t_rows.append([
                sesion.taller.titulo,
                nota_str,
                correctas_str,
                estado,
                fecha,
            ])

        t_table = Table(t_rows, colWidths=[5*cm, 2*cm, 4.5*cm, 3.5*cm, 3*cm])
        t_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
            ('ALIGN',      (1, 0), (-1, -1), 'CENTER'),
            ('PADDING',    (0, 0), (-1, -1), 7),
        ]
        # Color-code nota cells
        for row_idx, d in enumerate(talleres_data, start=1):
            ni = d['nota_info']
            if ni:
                cell_color = _nota_color(ni['nota'], GREEN, YELLOW, RED)
                t_styles.append(('BACKGROUND', (1, row_idx), (1, row_idx), cell_color))

        t_table.setStyle(TableStyle(t_styles))
        story.append(t_table)
    else:
        story.append(Paragraph(
            'El estudiante aun no ha iniciado ningun taller.', normal_style
        ))

    story.append(Spacer(1, 16))

    # ── Minijuegos Individuales (sin nota — solo jugo o no) ──────────────────
    story.append(Paragraph('Minijuegos Individuales', section_style))

    if progreso.exists():
        m_header = ['Juego', 'Tipo', 'Jugo?', 'Intentos', 'Ultimo intento']
        m_rows = [m_header]
        for p in progreso.order_by('game__title'):
            ultimo = (
                p.updated_at.strftime('%d/%m/%Y')
                if hasattr(p, 'updated_at') and p.updated_at else '-'
            )
            m_rows.append([
                p.game.title,
                p.game.get_game_type_display(),
                'Si' if p.attempts > 0 else 'No',
                str(p.attempts),
                ultimo,
            ])

        m_table = Table(m_rows, colWidths=[5*cm, 3.5*cm, 2*cm, 2.5*cm, 5*cm])
        m_styles = [
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
            ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
            ('ALIGN',      (2, 0), (-1, -1), 'CENTER'),
            ('PADDING',    (0, 0), (-1, -1), 7),
        ]
        # Highlight "No jugó" rows in light grey
        for row_idx, p in enumerate(progreso.order_by('game__title'), start=1):
            if p.attempts == 0:
                m_styles.append(('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.HexColor('#dc3545')))
        m_table.setStyle(TableStyle(m_styles))
        story.append(m_table)
    else:
        story.append(Paragraph(
            'El estudiante aun no ha jugado ningun minijuego individual.', normal_style
        ))

    # ── Ranking ───────────────────────────────────────────────────────────────
    if ranking_pos and ranking_total:
        story.append(Spacer(1, 16))
        story.append(Paragraph('Ranking en el Salon', section_style))
        r_data = [[
            f'Posicion: {ranking_pos} de {ranking_total}',
            f'Puntos XP acumulados: {estudiante.puntos_acumulados}',
            f'Nivel: {estudiante.nivel}',
        ]]
        r_table = Table(r_data, colWidths=[6*cm, 6*cm, 6*cm])
        r_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
            ('FONTNAME',   (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE',   (0, 0), (-1, -1), 10),
            ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
            ('PADDING',    (0, 0), (-1, -1), 10),
            ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#FFE66D')),
        ]))
        story.append(r_table)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E8E4FF')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Este informe fue generado automaticamente por NestGrow · '
        f'Plataforma de Aprendizaje de Ingles · {date.today().strftime("%d/%m/%Y")}',
        footer_style,
    ))

    doc.build(story)
    return buffer.getvalue()


def _nota_emoji(nota):
    if nota is None:   return ''
    if nota >= 4.5:    return '🏆'
    if nota >= 4.0:    return '⭐'
    if nota >= 3.5:    return '👍'
    if nota >= 3.0:    return '📖'
    return '💪'

def _nota_label(nota):
    if nota is None:   return 'Sin datos'
    if nota >= 4.5:    return 'Excelente'
    if nota >= 4.0:    return 'Alto'
    if nota >= 3.5:    return 'Básico'
    if nota >= 3.0:    return 'En proceso'
    return 'Reforzar'

def _nota_color_pdf(nota):
    if nota is None:            return colors.HexColor('#888888')
    if nota >= 4.0:             return colors.HexColor('#1a7a3b')
    if nota >= 3.5:             return colors.HexColor('#856404')
    if nota >= 3.0:             return colors.HexColor('#e67e22')
    return colors.HexColor('#721c24')

def _nota_bg_pdf(nota):
    if nota is None:            return colors.HexColor('#f0f0f0')
    if nota >= 4.0:             return colors.HexColor('#d4edda')
    if nota >= 3.5:             return colors.HexColor('#fff3cd')
    if nota >= 3.0:             return colors.HexColor('#ffe5cc')
    return colors.HexColor('#f8d7da')


def _barra_progreso(pct, bar_width=82, bar_height=7):
    """Devuelve un Drawing con una barra de progreso coloreada."""
    d = Drawing(bar_width, bar_height)
    d.add(Rect(0, 0, bar_width, bar_height,
               fillColor=colors.HexColor('#E8E4FF'),
               strokeColor=colors.HexColor('#C8C0FF'),
               strokeWidth=0.5))
    if pct and pct > 0:
        fill_w = max(bar_width * pct / 100, 2)
        if pct >= 80:
            fill_color = colors.HexColor('#28a745')
        elif pct >= 60:
            fill_color = colors.HexColor('#ffc107')
        elif pct >= 40:
            fill_color = colors.HexColor('#fd7e14')
        else:
            fill_color = colors.HexColor('#dc3545')
        d.add(Rect(0, 0, fill_w, bar_height, fillColor=fill_color, strokeColor=None))
    return d


def generar_pdf_informe_periodo(estudiante, periodo, fila_talleres, fila_minijuegos,
                                 estrellas_historia, nota_final=None):
    """PDF visual de resultados de un período para un estudiante."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles  = getSampleStyleSheet()
    primary = colors.HexColor('#6C63FF')
    accent  = colors.HexColor('#4ECDC4')
    light   = colors.HexColor('#F8F6FF')
    white   = colors.white
    W       = 17.4 * cm  # ancho disponible (A4 - márgenes)

    # ── Estilos de texto ──────────────────────────────────────────────────────
    brand_style   = ParagraphStyle('Br',  parent=styles['Normal'],
                                   textColor=colors.HexColor('#8b7fff'), fontSize=9,
                                   spaceAfter=1, alignment=TA_CENTER, fontName='Helvetica-Bold')
    title_style   = ParagraphStyle('T',   parent=styles['Heading1'],
                                   textColor=white, fontSize=17, spaceAfter=2,
                                   alignment=TA_CENTER, fontName='Helvetica-Bold')
    dates_style   = ParagraphStyle('D',   parent=styles['Normal'],
                                   textColor=colors.HexColor('#ddd8ff'), fontSize=9,
                                   spaceAfter=0, alignment=TA_CENTER)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'],
                                   textColor=primary, fontSize=12,
                                   spaceBefore=12, spaceAfter=4, fontName='Helvetica-Bold')
    sub_style     = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9,
                                   textColor=colors.HexColor('#666666'), spaceAfter=5)
    body_style    = ParagraphStyle('B',   parent=styles['Normal'], fontSize=10, spaceAfter=3)
    footer_style  = ParagraphStyle('F',   parent=styles['Normal'],
                                   textColor=colors.HexColor('#aaaaaa'), fontSize=8,
                                   alignment=TA_CENTER)
    center9       = ParagraphStyle('C9',  parent=styles['Normal'], fontSize=9,
                                   alignment=TA_CENTER, leading=14)

    nombre     = estudiante.user.get_full_name() or estudiante.user.username
    salon_name = str(estudiante.salon) if estudiante.salon else '—'
    salon_prof = ''
    if estudiante.salon and hasattr(estudiante.salon, 'profesor'):
        p = estudiante.salon.profesor
        salon_prof = p.user.get_full_name() if hasattr(p, 'user') else ''

    story = []

    # ── 1. Cabecera morada con Milo celebrando ────────────────────────────────
    milo_cabecera = _milo_img('milo_emociontotal.png', ancho=2.8*cm, alto=3.4*cm)

    # Columna de texto dentro del header (sin fondo propio — hereda el morado)
    hdr_text = Table([
        [Paragraph('NestGrow  ·  Plataforma de Aprendizaje de Ingles', brand_style)],
        [Paragraph(f'Informe de Periodo: <b>{periodo.titulo}</b>',      title_style)],
        [Paragraph(
            f'{periodo.fecha_inicio.strftime("%d/%m/%Y")}  →  '
            f'{periodo.fecha_fin.strftime("%d/%m/%Y")}  ·  Salon: {salon_name}',
            dates_style,
        )],
    ], colWidths=[W - 3.2*cm])
    hdr_text.setStyle(TableStyle([
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ]))

    header_table = Table([[hdr_text, milo_cabecera]], colWidths=[W - 3.2*cm, 3.2*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), primary),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',         (1, 0), (1, 0),  'CENTER'),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (0, 0),  0),
        ('RIGHTPADDING',  (1, 0), (1, 0),  6),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    story += [header_table, Spacer(1, 10)]

    # ── 2. Info + Nota Final + Milo de calificación ───────────────────────────
    INFO_W = W - 0.3*cm - 4.5*cm - 0.3*cm - 3.2*cm  # = 9.1 cm

    info_rows = [
        ['Estudiante', nombre],
        ['Salon',      salon_name],
    ]
    if salon_prof:
        info_rows.append(['Profesor/a', salon_prof])
    if estudiante.numero_lista:
        info_rows.append(['N de Lista', str(estudiante.numero_lista)])
    nivel = getattr(estudiante, 'nivel', None)
    xp    = getattr(estudiante, 'puntos_acumulados', 0) or 0
    if nivel is not None:
        info_rows.append(['Nivel / XP', f'Nivel {nivel}  -  {xp} XP'])
    ranking_pos, ranking_total = calcular_ranking(estudiante)
    if ranking_pos:
        trofeo = 'Oro' if ranking_pos == 1 else 'Plata' if ranking_pos == 2 else 'Bronce' if ranking_pos == 3 else 'Top'
        info_rows.append([f'Ranking ({trofeo})', f'{ranking_pos} de {ranking_total}'])
    if estudiante.correo_padre:
        info_rows.append(['Correo padre', estudiante.correo_padre])

    info_table = Table(info_rows, colWidths=[3.6*cm, INFO_W - 3.6*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (0, -1), light),
        ('TEXTCOLOR',     (0, 0), (0, -1), primary),
        ('FONTNAME',      (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9.5),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [white, light]),
        ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
    ]))

    # Cuadro de nota final
    if nota_final is not None:
        nf_bg    = _nota_bg_pdf(nota_final)
        nf_color = _nota_color_pdf(nota_final)
        nf_emoji = _nota_emoji(nota_final)
        nf_label = _nota_label(nota_final)
        nota_box_data = [
            [Paragraph('<b>NOTA FINAL</b>',
                       ParagraphStyle('NF_lbl', parent=styles['Normal'], textColor=nf_color,
                                      fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
            [Paragraph(f'<b>{nota_final}</b>',
                       ParagraphStyle('NF_val', parent=styles['Normal'], textColor=nf_color,
                                      fontSize=26, alignment=TA_CENTER, fontName='Helvetica-Bold'))],
            [Paragraph(f'{nf_emoji} {nf_label}',
                       ParagraphStyle('NF_sub', parent=styles['Normal'], textColor=nf_color,
                                      fontSize=9, alignment=TA_CENTER))],
        ]
        nota_box = Table(nota_box_data, colWidths=[4.5*cm])
        nota_box.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), nf_bg),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (-1, -1), 4),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ('BOX', (0, 0), (-1, -1), 1.5, nf_color),
        ]))
    else:
        nota_box = Paragraph('<i>Sin actividades completadas</i>',
                             ParagraphStyle('NF_na', parent=styles['Normal'],
                                            textColor=colors.grey, fontSize=9,
                                            alignment=TA_CENTER))

    # Milo apropiado según la nota
    milo_nota = _milo_img(_milo_segun_nota(nota_final), ancho=3.0*cm, alto=3.5*cm)

    combined = Table(
        [[info_table, Spacer(0.3*cm, 1), nota_box, Spacer(0.3*cm, 1), milo_nota]],
        colWidths=[INFO_W, 0.3*cm, 4.5*cm, 0.3*cm, 3.2*cm],
    )
    combined.setStyle(TableStyle([
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',       (4, 0), (4, 0),  'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',(0, 0), (-1, -1), 0),
    ]))
    story += [combined, Spacer(1, 12)]

    # ── 3. Resumen de actividad (3 chips de colores) ──────────────────────────
    t_completados = sum(1 for t in fila_talleres  if t['nota'] is not None)
    t_total       = len(fila_talleres)
    m_completados = sum(1 for m in fila_minijuegos if m['nota'] is not None)
    m_total       = len(fila_minijuegos)
    total_act     = t_total + m_total
    pct_global    = round((t_completados + m_completados) / total_act * 100) if total_act > 0 else 0

    if total_act > 0:
        c3_bg = (colors.HexColor('#E8F5E9') if pct_global >= 80
                 else colors.HexColor('#FFF8E1') if pct_global >= 50
                 else colors.HexColor('#FFEBEE'))
        summary_table = Table([[
            Paragraph(
                f'<b>Talleres</b><br/><font size=13><b>{t_completados}/{t_total}</b></font><br/>completados',
                center9,
            ),
            Paragraph(
                f'<b>Minijuegos</b><br/><font size=13><b>{m_completados}/{m_total}</b></font><br/>completados',
                center9,
            ),
            Paragraph(
                f'<b>Completitud</b><br/><font size=13><b>{pct_global}%</b></font><br/>del periodo',
                center9,
            ),
        ]], colWidths=[W/3, W/3, W/3])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (0, 0), colors.HexColor('#EDE9FF')),
            ('BACKGROUND',    (1, 0), (1, 0), colors.HexColor('#E8FAF9')),
            ('BACKGROUND',    (2, 0), (2, 0), c3_bg),
            ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))
        story += [summary_table, Spacer(1, 10)]

    # ── 4. Talleres ───────────────────────────────────────────────────────────
    if fila_talleres:
        story.append(Paragraph('Talleres', section_style))
        story.append(Paragraph(
            f'{t_completados} de {t_total} taller{"es" if t_total != 1 else ""}'
            f' completado{"s" if t_completados != 1 else ""}',
            sub_style,
        ))
        t_data = [['Taller', 'Nota', 'Desempeno', 'Progreso', 'Fecha']]
        for t in fila_talleres:
            if t['nota'] is not None:
                nota_str  = str(t['nota'])
                label_str = _nota_label(t['nota'])
                bar       = _barra_progreso(t['pct'], bar_width=82)
                sesion    = t.get('sesion')
                fecha_str = (
                    sesion.completada_en.strftime('%d/%m/%y')
                    if sesion and sesion.completada_en else '—'
                )
            else:
                nota_str  = '—'
                label_str = 'Sin completar'
                bar       = _barra_progreso(0)
                fecha_str = '—'
            t_data.append([t['asig'].taller.titulo, nota_str, label_str, bar, fecha_str])

        # 6 + 1.8 + 3 + 3.8 + 2.8 = 17.4 cm
        t_table = Table(t_data, colWidths=[6*cm, 1.8*cm, 3*cm, 3.8*cm, 2.8*cm])
        t_style = [
            ('BACKGROUND',    (0, 0), (-1, 0), primary),
            ('TEXTCOLOR',     (0, 0), (-1, 0), white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9.5),
            ('ALIGN',         (1, 0), (2, -1), 'CENTER'),
            ('ALIGN',         (4, 0), (4, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (0, -1), 8),
            ('LEFTPADDING',   (3, 1), (3, -1), 4),
        ]
        for i, t in enumerate(fila_talleres, 1):
            bg = _nota_bg_pdf(t['nota']) if t['nota'] else colors.HexColor('#fafafa')
            fc = _nota_color_pdf(t['nota']) if t['nota'] else colors.HexColor('#888888')
            t_style += [
                ('BACKGROUND', (1, i), (2, i), bg),
                ('TEXTCOLOR',  (1, i), (2, i), fc),
                ('FONTNAME',   (1, i), (2, i), 'Helvetica-Bold'),
            ]
        t_table.setStyle(TableStyle(t_style))
        story += [t_table, Spacer(1, 8)]

    # ── 5. Minijuegos ─────────────────────────────────────────────────────────
    if fila_minijuegos:
        story.append(Paragraph('Minijuegos', section_style))
        story.append(Paragraph(
            f'{m_completados} de {m_total} minijuego{"s" if m_total != 1 else ""}'
            f' completado{"s" if m_completados != 1 else ""}',
            sub_style,
        ))
        m_data = [['Juego', 'Tipo', 'Nota', 'Desempeno', 'Progreso']]
        for m in fila_minijuegos:
            tipo_str = (m['asig'].game.get_game_type_display()
                        if hasattr(m['asig'].game, 'get_game_type_display')
                        else m['asig'].game.game_type)
            if m['nota'] is not None:
                nota_str  = str(m['nota'])
                label_str = _nota_label(m['nota'])
                pct_val   = m['registro'].porcentaje if m['registro'] else 0
                bar       = _barra_progreso(pct_val, bar_width=82)
            else:
                nota_str  = '—'
                label_str = 'Sin completar'
                bar       = _barra_progreso(0)
            m_data.append([m['asig'].game.title, tipo_str, nota_str, label_str, bar])

        # 5.2 + 3 + 1.8 + 3.6 + 3.8 = 17.4 cm
        m_table = Table(m_data, colWidths=[5.2*cm, 3*cm, 1.8*cm, 3.6*cm, 3.8*cm])
        m_style = [
            ('BACKGROUND',    (0, 0), (-1, 0), accent),
            ('TEXTCOLOR',     (0, 0), (-1, 0), white),
            ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 9.5),
            ('ALIGN',         (2, 0), (3, -1), 'CENTER'),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID',          (0, 0), (-1, -1), 0.4, colors.HexColor('#C8F4F1')),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING',   (0, 0), (0, -1), 8),
            ('LEFTPADDING',   (4, 1), (4, -1), 4),
        ]
        for i, m in enumerate(fila_minijuegos, 1):
            nota = m['nota']
            bg = _nota_bg_pdf(nota) if nota else colors.HexColor('#fafafa')
            fc = _nota_color_pdf(nota) if nota else colors.HexColor('#888888')
            m_style += [
                ('BACKGROUND', (2, i), (3, i), bg),
                ('TEXTCOLOR',  (2, i), (3, i), fc),
                ('FONTNAME',   (2, i), (3, i), 'Helvetica-Bold'),
            ]
        m_table.setStyle(TableStyle(m_style))
        story += [m_table, Spacer(1, 8)]

    # ── 6. Modo Historia con Milo estrella ────────────────────────────────────
    if periodo.meta_historia > 0:
        story.append(Paragraph('Modo Historia', section_style))
        alcanzado  = estrellas_historia >= periodo.meta_historia
        pct_hist   = min(round((estrellas_historia / periodo.meta_historia) * 100), 100)
        estado_str = 'Meta alcanzada' if alcanzado else 'En progreso'
        hist_color = colors.HexColor('#1a7a3b') if alcanzado else colors.HexColor('#856404')
        hist_bg    = colors.HexColor('#d4edda') if alcanzado else colors.HexColor('#fff3cd')
        bar_hist   = _barra_progreso(pct_hist, bar_width=100, bar_height=8)

        milo_star = _milo_img('milo_star.png', ancho=2.8*cm, alto=3.0*cm)

        # 4.5 + 3.8 + 6.3 + 2.8 = 17.4 cm
        hist_table = Table([[
            Paragraph(
                f'Estrellas: <b>{estrellas_historia}</b> de <b>{periodo.meta_historia}</b>',
                body_style,
            ),
            bar_hist,
            Paragraph(
                f'<b>{estado_str}  ({pct_hist}%)</b>',
                ParagraphStyle('H', parent=styles['Normal'],
                               textColor=hist_color, fontSize=10,
                               alignment=TA_CENTER, fontName='Helvetica-Bold'),
            ),
            milo_star,
        ]], colWidths=[4.5*cm, 3.8*cm, 6.3*cm, 2.8*cm])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (1, 0), light),
            ('BACKGROUND',    (2, 0), (2, 0), hist_bg),
            ('BACKGROUND',    (3, 0), (3, 0), white),
            ('GRID',          (0, 0), (2, 0), 0.4, colors.HexColor('#E0DCFF')),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN',         (1, 0), (1, 0),  'CENTER'),
            ('ALIGN',         (3, 0), (3, 0),  'CENTER'),
            ('TOPPADDING',    (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING',   (0, 0), (2, 0),  8),
        ]))
        story += [hist_table, Spacer(1, 8)]

    # ── 7. Footer con Milo saludando ──────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E0DCFF')))
    story.append(Spacer(1, 6))

    milo_footer = _milo_img('milo_saludando.png', ancho=1.8*cm, alto=2.2*cm)
    footer_table = Table([[
        Paragraph(
            f'Generado automaticamente por <b>NestGrow</b> · Aprendizaje de Ingles'
            f' · {date.today().strftime("%d/%m/%Y")}',
            footer_style,
        ),
        milo_footer,
    ]], colWidths=[W - 2.0*cm, 2.0*cm])
    footer_table.setStyle(TableStyle([
        ('VALIGN',      (0, 0), (-1, -1), 'BOTTOM'),
        ('ALIGN',       (1, 0), (1, 0),  'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',(0, 0), (-1, -1), 0),
        ('TOPPADDING',  (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 0),
    ]))
    story.append(footer_table)

    doc.build(story,
              onFirstPage=_decorar_pagina,
              onLaterPages=_decorar_pagina)
    return buffer.getvalue()
