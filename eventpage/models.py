from django.db import models


class EventPage(models.Model):
    id = models.AutoField(primary_key=True)  # 01 - PK
    event = models.OneToOneField('main.Event', on_delete=models.CASCADE, related_name='event_page')  # 02 - One-to-One
    is_deleted = models.BooleanField(default=False)  # 11

    def __str__(self):
        return f"EventPage for {self.event}"

    def soft_delete(self):
        self.is_deleted = True
        self.save()


class BlockType(models.TextChoices):
    GENERAL = 'GENERAL', 'General Block'
    TITLE = 'TITLE', 'Title Block'
    TEXT = 'TEXT', 'Text Block'
    IMAGE = 'IMAGE', 'Image Block'
    COUNTDOWN = 'COUNTDOWN', 'Countdown Block'
    BUTTON = 'BUTTON', 'Button Block'
    PAY = 'PAY', 'Pay Block'
    MERCADOPAGO = 'MERCADOPAGO', 'MercadoPago Block'
    SPOTIFY = 'SPOTIFY', 'Spotify Block'
    TARJETEROS = 'TARJETEROS', 'Tarjeteros Block'


class EventPageBlock(models.Model):
    id = models.AutoField(primary_key=True)
    event_page = models.ForeignKey(EventPage, on_delete=models.CASCADE, related_name='blocks')
    type = models.CharField(max_length=20, choices=BlockType.choices)
    order = models.PositiveIntegerField()
    data = models.JSONField(default=dict)


    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_type_display()} Block for {self.event_page}"
