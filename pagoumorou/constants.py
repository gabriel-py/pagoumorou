from django.db import models

class PeriodChoices(models.TextChoices):
    WEEK = 'Week'
    BIWEEK = 'Biweek'
    MONTH = 'Month'
    SEMESTER = 'Semester'
    YEAR = 'Year'

class StatusChoices(models.TextChoices):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    EXPIRED = 'Expired'
