"""
PDF generation for student reports using reportlab.
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import date


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
    gold    = colors.HexColor('#FFB347')
    light   = colors.HexColor('#F8F6FF')
    white   = colors.white

    # ── Estilos de texto ──────────────────────────────────────────────────────
    brand_style   = ParagraphStyle('Br', parent=styles['Normal'],
                                   textColor=colors.HexColor('#8b7fff'), fontSize=9,
                                   spaceAfter=1, alignment=TA_CENTER, fontName='Helvetica-Bold')
    title_style   = ParagraphStyle('T', parent=styles['Heading1'],
                                   textColor=white, fontSize=17, spaceAfter=2,
                                   alignment=TA_CENTER, fontName='Helvetica-Bold')
    dates_style   = ParagraphStyle('D', parent=styles['Normal'],
                                   textColor=colors.HexColor('#ddd8ff'), fontSize=9,
                                   spaceAfter=0, alignment=TA_CENTER)
    section_style = ParagraphStyle('Sec', parent=styles['Heading2'],
                                   textColor=primary, fontSize=12,
                                   spaceBefore=12, spaceAfter=5, fontName='Helvetica-Bold')
    body_style    = ParagraphStyle('B', parent=styles['Normal'], fontSize=10, spaceAfter=3)
    footer_style  = ParagraphStyle('F', parent=styles['Normal'],
                                   textColor=colors.HexColor('#aaaaaa'), fontSize=8,
                                   alignment=TA_CENTER)

    nombre     = estudiante.user.get_full_name() or estudiante.user.username
    salon_name = str(estudiante.salon) if estudiante.salon else '—'
    salon_prof = ''
    if estudiante.salon and hasattr(estudiante.salon, 'profesor'):
        p = estudiante.salon.profesor
        salon_prof = p.user.get_full_name() if hasattr(p, 'user') else ''

    story = []

    # ── 1. Cabecera con fondo morado ──────────────────────────────────────────
    header_data = [[
        Paragraph('NestGrow · Plataforma de Aprendizaje de Inglés', brand_style),
        '',
    ], [
        Paragraph(f'Informe de Período: <b>{periodo.titulo}</b>', title_style),
        '',
    ], [
        Paragraph(
            f'{periodo.fecha_inicio.strftime("%d/%m/%Y")}  →  {periodo.fecha_fin.strftime("%d/%m/%Y")}',
            dates_style,
        ),
        '',
    ]]
    header_table = Table(header_data, colWidths=['100%', 0])
    header_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, -1), primary),
        ('SPAN',         (0, 0), (1, 0)),
        ('SPAN',         (0, 1), (1, 1)),
        ('SPAN',         (0, 2), (1, 2)),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('LEFTPADDING',  (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
    ]))
    story += [header_table, Spacer(1, 10)]

    # ── 2. Datos del estudiante + Nota Final (lado a lado) ────────────────────
    info_rows = [
        ['👤 Estudiante', nombre],
        ['🏫 Salón',       salon_name],
    ]
    if salon_prof:
        info_rows.append(['👩‍🏫 Profesor/a', salon_prof])
    if estudiante.numero_lista:
        info_rows.append(['📋 N° de Lista', estudiante.numero_lista])
    if estudiante.correo_padre:
        info_rows.append(['📧 Correo padre/madre', estudiante.correo_padre])

    info_table = Table(info_rows, colWidths=[4.2*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (0, -1), light),
        ('TEXTCOLOR',    (0, 0), (0, -1), primary),
        ('FONTNAME',     (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9.5),
        ('ROWBACKGROUNDS',(0, 0), (-1, -1), [white, light]),
        ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))

    # Cuadro de nota final
    if nota_final is not None:
        nf_bg    = _nota_bg_pdf(nota_final)
        nf_color = _nota_color_pdf(nota_final)
        nf_emoji = _nota_emoji(nota_final)
        nf_label = _nota_label(nota_final)
        nota_box_data = [[Paragraph(
            f'<b>NOTA FINAL</b>',
            ParagraphStyle('NF_lbl', parent=styles['Normal'], textColor=nf_color,
                           fontSize=9, alignment=TA_CENTER, fontName='Helvetica-Bold'),
        )], [Paragraph(
            f'<b>{nota_final}</b>',
            ParagraphStyle('NF_val', parent=styles['Normal'], textColor=nf_color,
                           fontSize=28, alignment=TA_CENTER, fontName='Helvetica-Bold'),
        )], [Paragraph(
            f'{nf_emoji} {nf_label}',
            ParagraphStyle('NF_sub', parent=styles['Normal'], textColor=nf_color,
                           fontSize=9, alignment=TA_CENTER),
        )]]
        nota_box = Table(nota_box_data, colWidths=[4.5*cm])
        nota_box.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), nf_bg),
            ('TOPPADDING',   (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
            ('LEFTPADDING',  (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
            ('BOX', (0, 0), (-1, -1), 1.5, nf_color),
        ]))
    else:
        nota_box = Paragraph('<i>Sin actividades completadas</i>',
                             ParagraphStyle('NF_na', parent=styles['Normal'],
                                            textColor=colors.grey, fontSize=9,
                                            alignment=TA_CENTER))

    combined = Table([[info_table, Spacer(0.4*cm, 1), nota_box]],
                     colWidths=[None, 0.4*cm, 4.5*cm])
    combined.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story += [combined, Spacer(1, 12)]

    # ── 3. Talleres ───────────────────────────────────────────────────────────
    if fila_talleres:
        story.append(Paragraph('🎓 Talleres', section_style))
        t_data = [['Taller', 'Nota', 'Desempeño', '%']]
        for t in fila_talleres:
            if t['nota'] is not None:
                nota_str  = str(t['nota'])
                label_str = _nota_label(t['nota'])
                pct_str   = f"{t['pct']}%"
            else:
                nota_str = label_str = '—'
                pct_str  = 'Sin completar'
            t_data.append([t['asig'].taller.titulo, nota_str, label_str, pct_str])

        t_table = Table(t_data, colWidths=[None, 2*cm, 3.2*cm, 2.2*cm])
        t_style = [
            ('BACKGROUND',   (0, 0), (-1, 0), primary),
            ('TEXTCOLOR',    (0, 0), (-1, 0), white),
            ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 9.5),
            ('ALIGN',        (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('LEFTPADDING',  (0, 0), (0, -1), 8),
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

    # ── 4. Minijuegos ─────────────────────────────────────────────────────────
    if fila_minijuegos:
        story.append(Paragraph('🎮 Minijuegos', section_style))
        m_data = [['Juego', 'Nota', 'Desempeño', '%']]
        for m in fila_minijuegos:
            if m['nota'] is not None:
                nota_str  = str(m['nota'])
                label_str = _nota_label(m['nota'])
                pct_str   = f"{m['registro'].porcentaje}%"
            else:
                nota_str = label_str = '—'
                pct_str  = 'Sin completar'
            m_data.append([m['asig'].game.title, nota_str, label_str, pct_str])

        m_table = Table(m_data, colWidths=[None, 2*cm, 3.2*cm, 2.2*cm])
        m_style = [
            ('BACKGROUND',   (0, 0), (-1, 0), accent),
            ('TEXTCOLOR',    (0, 0), (-1, 0), white),
            ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 9.5),
            ('ALIGN',        (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#C8F4F1')),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
            ('LEFTPADDING',  (0, 0), (0, -1), 8),
        ]
        for i, m in enumerate(fila_minijuegos, 1):
            nota = m['nota']
            bg = _nota_bg_pdf(nota) if nota else colors.HexColor('#fafafa')
            fc = _nota_color_pdf(nota) if nota else colors.HexColor('#888888')
            m_style += [
                ('BACKGROUND', (1, i), (2, i), bg),
                ('TEXTCOLOR',  (1, i), (2, i), fc),
                ('FONTNAME',   (1, i), (2, i), 'Helvetica-Bold'),
            ]
        m_table.setStyle(TableStyle(m_style))
        story += [m_table, Spacer(1, 8)]

    # ── 5. Modo Historia ──────────────────────────────────────────────────────
    if periodo.meta_historia > 0:
        story.append(Paragraph('⭐ Modo Historia', section_style))
        alcanzado   = estrellas_historia >= periodo.meta_historia
        estado_str  = 'Meta alcanzada ✅' if alcanzado else 'En progreso ⏳'
        hist_color  = colors.HexColor('#1a7a3b') if alcanzado else colors.HexColor('#856404')
        hist_bg     = colors.HexColor('#d4edda') if alcanzado else colors.HexColor('#fff3cd')
        hist_data = [[
            Paragraph(f'Estrellas: <b>{estrellas_historia}</b> de <b>{periodo.meta_historia}</b>', body_style),
            Paragraph(f'<b>{estado_str}</b>',
                      ParagraphStyle('H', parent=styles['Normal'],
                                     textColor=hist_color, fontSize=10,
                                     alignment=TA_CENTER, fontName='Helvetica-Bold')),
        ]]
        hist_table = Table(hist_data, colWidths=[None, 5*cm])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND',   (1, 0), (1, 0), hist_bg),
            ('BACKGROUND',   (0, 0), (0, 0), light),
            ('GRID',         (0, 0), (-1, -1), 0.4, colors.HexColor('#E0DCFF')),
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING',   (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 7),
            ('LEFTPADDING',  (0, 0), (-1, -1), 8),
        ]))
        story += [hist_table, Spacer(1, 8)]

    # ── 6. Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E0DCFF')))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f'Generado automáticamente por <b>NestGrow</b> · Aprendizaje de Inglés · {date.today().strftime("%d/%m/%Y")}',
        footer_style,
    ))

    doc.build(story)
    return buffer.getvalue()
