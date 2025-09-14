# claims/models.py

from django.db import models

class Claim(models.Model):
    """
    Represents the main claim data from claim_list_data.csv.
    """
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Denied', 'Denied'),
        ('Under Review', 'Under Review'),
    ]

    id = models.IntegerField(primary_key=True)
    patient_name = models.CharField(max_length=255, db_index=True)
    billed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    insurer_name = models.CharField(max_length=255, db_index=True)
    discharge_date = models.DateField()

    def __str__(self):
        return f"Claim #{self.id} for {self.patient_name}"

class ClaimDetail(models.Model):
    """
    Represents the detailed claim data from claim_detail_data.csv,
    linked one-to-one with the Claim model.
    """
    claim = models.OneToOneField(
        Claim,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='details'
    )
    denial_reason = models.TextField(null=True, blank=True)
    cpt_codes = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Details for Claim #{self.claim.id}"
