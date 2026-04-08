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
    compañeros = EstudianteProfile.objects.filter(
        salon=estudiante.salon
    ).order_by('-puntos_totales')
    total = compañeros.count()
    for i, c in enumerate(compañeros, 1):
        if c.pk == estudiante.pk:
            return i, total
    return None, total


def generar_pdf_informe(estudiante, progreso, scores):
    """Generate a PDF report for a student and return bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    PRIMARY = colors.HexColor('#6C63FF')
    ACCENT = colors.HexColor('#4ECDC4')
    LIGHT = colors.HexColor('#F8F6FF')
    GREEN = colors.HexColor('#d4edda')
    YELLOW = colors.HexColor('#fff3cd')
    RED = colors.HexColor('#f8d7da')

    title_style = ParagraphStyle(
        'NestTitle', parent=styles['Title'],
        textColor=PRIMARY, fontSize=22, spaceAfter=4,
        fontName='Helvetica-Bold', alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'NestSub', parent=styles['Normal'],
        textColor=colors.HexColor('#666666'), fontSize=11,
        alignment=TA_CENTER, spaceAfter=2
    )
    section_style = ParagraphStyle(
        'NestSection', parent=styles['Heading2'],
        textColor=PRIMARY, fontSize=13,
        fontName='Helvetica-Bold', spaceBefore=12, spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'NestNormal', parent=styles['Normal'],
        fontSize=10, leading=14
    )
    footer_style = ParagraphStyle(
        'footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#999999'), alignment=TA_CENTER
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph('🐺 NestGrow', title_style))
    story.append(Paragraph('Plataforma de Aprendizaje de Inglés', subtitle_style))
    story.append(Paragraph(f'Informe de Actividades — {date.today().strftime("%d de %B de %Y")}', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=3, color=PRIMARY, spaceAfter=16))

    # ── Student Info ─────────────────────────────────────────────────────────
    story.append(Paragraph('📋 Información del Estudiante', section_style))

    nombre = estudiante.user.get_full_name() or estudiante.user.username
    salon_nombre = estudiante.salon.nombre if estudiante.salon else '—'
    grado = estudiante.get_grado_display() if estudiante.grado else '—'
    identidad = estudiante.numero_identidad or '—'
    profesor_nombre = (estudiante.salon.profesor.user.get_full_name()
                       if estudiante.salon else '—')

    # Calculate ranking
    ranking_pos, ranking_total = calcular_ranking(estudiante)
    ranking_str = f'{ranking_pos}° de {ranking_total} estudiantes' if ranking_pos else '—'

    # Calculate overall nota from all progress
    all_pcts = []
    for p in progreso:
        if p.max_score > 0:
            all_pcts.append(int((p.score / p.max_score) * 100))
    nota_promedio = calcular_nota(sum(all_pcts) / len(all_pcts)) if all_pcts else 0
    juegos_completados = progreso.filter(completed=True).count()

    info_data = [
        ['Nombre completo:', nombre, 'Grado:', grado],
        ['N° Identidad:', identidad, 'Salón:', salon_nombre],
        ['Profesor/a:', profesor_nombre, 'Ranking en salón:', ranking_str],
        ['Juegos completados:', str(juegos_completados),
         'Nota promedio:', f'{nota_promedio:.1f} / 5.0'],
    ]

    info_table = Table(info_data, colWidths=[4*cm, 6*cm, 4*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('TEXTCOLOR', (0, 0), (0, -1), PRIMARY),
        ('TEXTCOLOR', (2, 0), (2, -1), PRIMARY),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ── Nota Highlight Box ───────────────────────────────────────────────────
    if nota_promedio > 0:
        nota_color = GREEN if nota_promedio >= 4.0 else YELLOW if nota_promedio >= 3.0 else RED
        nota_text = f'Nota General del Período: {nota_promedio:.1f} / 5.0'
        nota_data = [[nota_text]]
        nota_table = Table(nota_data, colWidths=[18*cm])
        nota_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), nota_color),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 13),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ]))
        story.append(nota_table)
        story.append(Spacer(1, 16))

    # ── Game Progress with Nota ───────────────────────────────────────────────
    story.append(Paragraph('🎮 Progreso en Actividades', section_style))

    if progreso.exists():
        prog_data = [['Actividad', 'Tipo', 'Puntaje', 'Nota', 'Intentos', 'Estado']]
        for p in progreso:
            pct = int((p.score / p.max_score) * 100) if p.max_score > 0 else 0
            nota = calcular_nota(pct)
            prog_data.append([
                p.game.title,
                p.game.get_game_type_display(),
                str(p.score),
                f'{nota:.1f}',
                str(p.attempts),
                '✅ Completado' if p.completed else '⏳ En progreso',
            ])

        prog_table = Table(prog_data, colWidths=[4.5*cm, 3*cm, 2*cm, 2*cm, 2*cm, 4.5*cm])
        prog_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
            ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 7),
        ]))
        story.append(prog_table)
    else:
        story.append(Paragraph('El estudiante aún no ha realizado actividades.', normal_style))

    story.append(Spacer(1, 16))

    # ── Last 5 Scores ────────────────────────────────────────────────────────
    story.append(Paragraph('⭐ Últimas 5 Puntuaciones', section_style))

    last_scores = scores[:5]  # Already limited to 5 in view
    if last_scores:
        score_data = [['Actividad', 'Puntaje', 'Nota', 'Tiempo (seg)', 'Fecha']]
        for s in last_scores:
            pct = int((s.score / s.max_score) * 100) if s.max_score > 0 else 0
            nota = calcular_nota(pct)
            score_data.append([
                s.game.title,
                str(s.score),
                f'{nota:.1f}',
                str(s.time_spent),
                s.created_at.strftime('%d/%m/%Y'),
            ])
        score_table = Table(score_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3*cm, 4.5*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E8E4FF')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 7),
        ]))
        story.append(score_table)
    else:
        story.append(Paragraph('Sin puntuaciones registradas aún.', normal_style))

    # ── Ranking Section ───────────────────────────────────────────────────────
    if ranking_pos and ranking_total:
        story.append(Spacer(1, 16))
        story.append(Paragraph('🏆 Ranking en el Salón', section_style))
        ranking_data = [[
            f'Posición actual: {ranking_pos}° de {ranking_total} estudiantes',
            f'Puntos acumulados: {estudiante.puntos_totales}',
            f'Nivel: {estudiante.nivel}',
        ]]
        rank_table = Table(ranking_data, colWidths=[6*cm, 6*cm, 6*cm])
        rank_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff9e6')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#FFE66D')),
        ]))
        story.append(rank_table)

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#E8E4FF')))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        'Este informe fue generado automáticamente por NestGrow · Plataforma de Aprendizaje de Inglés · '
        f'Generado el {date.today().strftime("%d/%m/%Y")}',
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()
