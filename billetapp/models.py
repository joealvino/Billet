from django.db import models


class Billet(models.Model):
# id est implicite (AutoField / BigAutoField selon settings)
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    statut = models.BooleanField(default=False)


created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return f'Billet #{self.pk} - statut={self.statut}'

from django.db import models

class Billet(models.Model):
    TYPE_CHOICES = [
        ('VIP', 'VIP'),
        ('PREMIUM', 'Premium'),
        ('SIMPLE', 'Simple'),
    ]

    type_billet = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SIMPLE')
    qr_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    statut = models.BooleanField(default=False)

    def __str__(self):
        return f"Billet #{self.id} ({self.type_billet}) - {'Validé' if self.statut else 'Non validé'}"
