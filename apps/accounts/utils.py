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
    identidad     = estudiante.numero_identidad or '-'
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
