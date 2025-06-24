from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from io import BytesIO

def generar_reporte_ventas(ventas, filename=None):
    # Generar nombre de archivo único si no se proporciona
    if filename is None:
        filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Crear buffer en memoria para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []  # Lista de elementos que conformarán el PDF
    styles = getSampleStyleSheet()
    
    # ========================================================================
    # CONFIGURACIÓN DE ESTILOS PERSONALIZADOS
    # ========================================================================
    
    # Estilo para el título principal
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0d6efd')  # Azul corporativo
    )
    
    # ========================================================================
    # ENCABEZADO DEL DOCUMENTO
    # ========================================================================
    
    # Intentar agregar logo de la empresa
    try:
        logo_path = "static/images/logo.png"
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
    except:
        # Si no se puede cargar el logo, continuar sin él
        pass
    
    # Títulos del documento
    story.append(Paragraph("MUEBLES MET VIL", title_style))
    story.append(Paragraph("Reporte Completo de Ventas", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # ========================================================================
    # INFORMACIÓN GENERAL DEL REPORTE
    # ========================================================================
    
    # Calcular estadísticas generales
    total_ventas = sum(venta.total for venta in ventas)
    ventas_directas = [v for v in ventas if v.tipo_venta == 'directa']
    ventas_por_compra = [v for v in ventas if v.tipo_venta == 'por_compra']
    
    # Tabla con información del reporte
    info_data = [
        ['Fecha de generación:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Total de ventas:', str(len(ventas))],
        ['Ventas directas:', str(len(ventas_directas))],
        ['Ventas por compras:', str(len(ventas_por_compra))],
        ['Total ingresos:', f'${total_ventas:,.2f}'],
        ['Generado por:', 'Sistema Administrativo']
    ]
    
    # Crear y estilizar tabla de información
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # ========================================================================
    # TABLA PRINCIPAL DE VENTAS
    # ========================================================================
    
    if ventas:
        # Encabezados de la tabla
        data = [['ID', 'Fecha', 'Cliente', 'Producto', 'Cant.', 'P.Unit.', 'Total', 'Tipo', 'Origen']]
        
        # Agregar cada venta a la tabla
        for venta in ventas:
            tipo_badge = 'Directa' if venta.tipo_venta == 'directa' else 'Por Compra'
            origen = f'Compra #{venta.compra_id}' if venta.compra_id else 'Manual'
            
            data.append([
                str(venta.id),
                venta.fecha.strftime('%d/%m/%Y'),
                venta.cliente,
                venta.producto.nombre if venta.producto else 'N/A',
                str(venta.cantidad),
                f'${venta.precio_unitario:,.2f}',
                f'${venta.total:,.2f}',
                tipo_badge,
                origen
            ])
        
        # Fila de totales
        data.append(['', '', '', '', '', '', f'${total_ventas:,.2f}', 'TOTAL', ''])
        
        # Crear tabla con anchos de columna específicos
        table = Table(data, colWidths=[0.4*inch, 0.8*inch, 1.2*inch, 1.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        
        # Aplicar estilos a la tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Filas de datos
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            # Fila de totales
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        story.append(table)
        
        # ====================================================================
        # RESUMEN POR TIPO DE VENTA
        # ====================================================================
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("Resumen por Tipo de Venta", styles['Heading3']))
        
        resumen_data = [
            ['Tipo de Venta', 'Cantidad', 'Total'],
            ['Ventas Directas', str(len(ventas_directas)), f'${sum(v.total for v in ventas_directas):,.2f}'],
            ['Ventas por Compras', str(len(ventas_por_compra)), f'${sum(v.total for v in ventas_por_compra):,.2f}']
        ]
        
        resumen_table = Table(resumen_data, colWidths=[2*inch, 1*inch, 1.5*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(resumen_table)
        
    else:
        # Mensaje si no hay ventas
        story.append(Paragraph("No hay ventas registradas en el período seleccionado.", styles['Normal']))
    
    # Construir el PDF y retornar buffer
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_factura_compra(compra, filename=None):
    
    if filename is None:
        filename = f"factura_compra_{compra.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado para facturas
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#dc3545')  # Rojo corporativo
    )
    
    # ========================================================================
    # ENCABEZADO DE LA FACTURA
    # ========================================================================
    
    # Logo de la empresa
    try:
        logo_path = "static/images/logo.png"
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
    except:
        pass
    
    # Títulos
    story.append(Paragraph("MUEBLES MET VIL", title_style))
    story.append(Paragraph("FACTURA DE COMPRA", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Información de la empresa
    empresa_info = [
        "Dirección: Calle 123 #45-67, Ciudad",
        "Teléfono: +57 123 456 7890",
        "Email: info@mueblesmetvil.com",
        "NIT: 123.456.789-0"
    ]
    
    for info in empresa_info:
        story.append(Paragraph(info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # ========================================================================
    # INFORMACIÓN DE LA FACTURA
    # ========================================================================
    
    factura_data = [
        ['Factura No.:', f"FAC-{compra.id:06d}"],
        ['Fecha:', compra.fecha_aprobacion.strftime('%d/%m/%Y') if compra.fecha_aprobacion else compra.fecha.strftime('%d/%m/%Y')],
        ['Cliente:', compra.usuario.nombre if compra.usuario else 'N/A'],
        ['Estado:', compra.estado.upper()],
        ['Venta Relacionada:', f"#{compra.venta[0].id}" if hasattr(compra, 'venta') and compra.venta else 'N/A']
    ]
    
    factura_table = Table(factura_data, colWidths=[2*inch, 3*inch])
    factura_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(factura_table)
    story.append(Spacer(1, 20))
    
    # ========================================================================
    # DETALLE DE LA COMPRA
    # ========================================================================
    
    story.append(Paragraph("DETALLE DE LA COMPRA", styles['Heading3']))
    story.append(Spacer(1, 10))
    
    # Tabla de productos
    detalle_data = [
        ['Producto', 'Cantidad', 'Precio Unitario', 'Total']
    ]
    
    detalle_data.append([
        compra.producto.nombre if compra.producto else 'N/A',
        str(compra.cantidad),
        f'${compra.precio_unitario:,.2f}',
        f'${compra.total:,.2f}'
    ])
    
    # Cálculos de totales
    detalle_data.append(['', '', 'SUBTOTAL:', f'${compra.total:,.2f}'])
    detalle_data.append(['', '', 'IVA (19%):', f'${compra.total * 0.19:,.2f}'])
    detalle_data.append(['', '', 'TOTAL:', f'${compra.total * 1.19:,.2f}'])
    
    detalle_table = Table(detalle_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    detalle_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        # Totales
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(detalle_table)
    story.append(Spacer(1, 30))
    
    # ========================================================================
    # PIE DE PÁGINA
    # ========================================================================
    
    story.append(Paragraph("¡Gracias por su compra!", styles['Heading3']))
    story.append(Paragraph("Esta factura es válida como comprobante de compra.", styles['Normal']))
    
    # Agregar comentarios si existen
    if compra.comentarios:
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Comentarios: {compra.comentarios}", styles['Normal']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_reporte_productos(productos, filename=None):
    
    if filename is None:
        filename = f"reporte_productos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Logo y título
    try:
        logo_path = "static/images/logo.png"
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
    except:
        pass
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0d6efd')
    )
    
    story.append(Paragraph("MUEBLES MET VIL", title_style))
    story.append(Paragraph("Reporte de Inventario", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Tabla de productos
    if productos:
        data = [['ID', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Estado']]
        
        for producto in productos:
            estado = 'Disponible' if producto.stock > 0 else 'Agotado'
            data.append([
                str(producto.id),
                producto.nombre,
                producto.categoria or 'N/A',
                f'${producto.precio:,.2f}',
                str(producto.stock),
                estado
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
