from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from .models import Billet
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from qrcode import make as make_qr
from io import BytesIO
import pythoncom

from .models import Billet
from docx2pdf import convert  # Assure-toi d'avoir installé docx2pdf


def home(request):
    count = Billet.objects.count()
    latest = Billet.objects.order_by('-id').first()  # tri par ID (plus récent en premier)
    return render(request, 'billetapp/create_billet.html', {'latest': latest, 'count': count})


def create_billet(request):
    if request.method == 'POST':
        type_billet = request.POST.get('type_billet', 'SIMPLE')
        nombre = int(request.POST.get('nombre', 1))

        for _ in range(nombre):
            billet = Billet.objects.create(type_billet=type_billet)
            scan_url = f"{settings.NGROK_URL}{reverse('billetapp:scan_billet', args=[billet.pk])}"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(scan_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_{billet.pk}.png'
            billet.qr_image.save(filename, ContentFile(buffer.getvalue()))
            billet.save()

        return redirect('billetapp:liste_billets')

    return render(request, 'billetapp/create_billet.html')


def scan_billet(request, pk):
    billet = get_object_or_404(Billet, pk=pk)
    if billet.statut:
        message = '❌ Billet déjà scanné'
        valid = False
    else:
        billet.statut = True
        billet.save()
        message = '✅ Billet validé'
        valid = True

    return render(request, 'billetapp/scan_billet.html', {'billet': billet, 'message': message, 'valid': valid})


def liste_billets(request):
    billets = Billet.objects.order_by('-id')
    return render(request, 'billetapp/liste_billets.html', {'billets': billets})


import os
import pythoncom
from io import BytesIO
from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate
from docx2pdf import convert
import qrcode
from django.core.files.base import ContentFile
from .models import Billet
def generate_billet_pdf(billet: Billet) -> str:
    """
    Génère un PDF pour le billet donné à partir d'un template DOCX.
    Le QR code est intégré dans le document.
    Retourne le chemin complet du fichier PDF généré.
    """

    # --- 1. Générer QR code si nécessaire ---
    if not billet.qr_image:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr_data = f"Billet ID: {billet.id} - Type: {billet.type_billet}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        billet.qr_image.save(f"qr_{billet.id}.png", ContentFile(buffer.getvalue()), save=True)

    # --- 2. Initialisation COM (Windows uniquement pour docx2pdf) ---
    pythoncom.CoInitialize()
    try:
        # --- 3. Chemins ---
        output_dir = os.path.join(settings.BASE_DIR, 'billetapp', 'output')
        os.makedirs(output_dir, exist_ok=True)

        temp_docx = os.path.join(output_dir, f'billet_{billet.id}.docx')
        pdf_path = os.path.join(output_dir, f'billet_{billet.id}.pdf')

        # --- 4. Génération DOCX avec docxtpl ---
        template_path = os.path.join(settings.BASE_DIR, 
                                     'billetapp', 'static', 'billetapp', 'assets', 'modele_billet.docx')
        doc = DocxTemplate(template_path)

        # InlineImage permet d'insérer l'image dans le template
        context = {
            'id': billet.id,
            'type_billet': billet.type_billet,
            'statut': 'Validé' if billet.statut else 'Non validé',
            'qr_path': InlineImage(doc, billet.qr_image.path, width=Mm(50)),  # largeur 50mm
        }

        doc.render(context)
        doc.save(temp_docx)

        # --- 5. Conversion DOCX → PDF ---
        convert(temp_docx, pdf_path)

        return pdf_path

    finally:
        pythoncom.CoUninitialize()


# Vue Django pour télécharger le PDF
from django.shortcuts import get_object_or_404
from django.http import FileResponse

def telecharger_billet_pdf(request, billet_id):
    billet = get_object_or_404(Billet, pk=billet_id)
    pdf_path = generate_billet_pdf(billet)
    return FileResponse(
        open(pdf_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(pdf_path)
    )