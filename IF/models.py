from django.db import models
from django.db.models import F, ExpressionWrapper, fields

class Shipment(models.Model):
    order_id = models.CharField(max_length=50)
    order_date = models.DateField()
    ship_date = models.DateField()
    region = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    ship_mode = models.CharField(max_length=50)
    route = models.CharField(max_length=255)

    @property
    def lead_time(self):
        return (self.ship_date - self.order_date).days