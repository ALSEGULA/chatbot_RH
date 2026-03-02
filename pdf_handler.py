from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf(filename, title, content):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, title)
    c.setFont("Helvetica", 12)
    textobject = c.beginText(100, 720)
    for line in content.split('\n'):
        textobject.textLine(line)
    c.drawText(textobject)
    c.save()

# 1. Politique de Télétravail
create_pdf("politique_teletravail.pdf", "Politique de Teletravail - SMA", 
           "Le teletravail est autorise jusqu'a 2 jours par semaine.\n"
           "Une indemnite forfaitaire de 3.50 euros par jour est versée.\n"
           "Le materiel (ecran, clavier, souris) est fourni sur demande au service RH.")

# 2. Guide des Congés
create_pdf("guide_conges.pdf", "Guide des Conges et Absences", 
           "Les employes beneficient de 28 jours de conges payes par an.\n"
           "La periode de reference va du 1er juin au 30 avril.\n"
           "Les demandes de conges doivent etre validees par le manager par email.")

print("PDFs générés avec succès !")