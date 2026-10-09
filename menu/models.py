from django.db import models
from django.contrib.auth.models import User


class Kategoriya(models.Model):
    nom = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10, default='🍽️')

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"


class Taom(models.Model):
    kategoriya = models.ForeignKey(Kategoriya, on_delete=models.SET_NULL, null=True, blank=True, related_name='taomlar')
    nom = models.CharField(max_length=100)
    tavsif = models.TextField(blank=True)
    narx = models.PositiveIntegerField()
    rasm = models.ImageField(upload_to='taomlar/', null=True, blank=True)
    mavjud = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    def narx_formatted(self):
        return f"{self.narx:,} so'm".replace(',', ' ')

    class Meta:
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"


class Buyurtma(models.Model):
    STATUS_CHOICES = [
        ('yangi', '🆕 Yangi'),
        ('tasdiqlangan', '✅ Tasdiqlangan'),
        ('tayyorlanmoqda', '👨‍🍳 Tayyorlanmoqda'),
        ('yetkazildi', '🚀 Yetkazildi'),
        ('bekor', '❌ Bekor qilindi'),
    ]

    foydalanuvchi = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    taom = models.ForeignKey(Taom, on_delete=models.CASCADE)
    mijoz = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20)
    manzil = models.CharField(max_length=255, blank=True, default='')
    izoh = models.TextField(blank=True, default='')
    miqdor = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yangi')
    vaqt = models.DateTimeField(auto_now_add=True)

    def jami_narx(self):
        return self.taom.narx * self.miqdor

    def jami_narx_formatted(self):
        return f"{self.jami_narx():,} so'm".replace(',', ' ')

    def __str__(self):
        return f"{self.mijoz} — {self.taom.nom}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-vaqt']
