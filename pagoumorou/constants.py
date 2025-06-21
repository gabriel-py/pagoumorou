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

PERIOD_VERBOSE = {
    PeriodChoices.WEEK: "7 dias",
    PeriodChoices.BIWEEK: "15 dias",
    PeriodChoices.MONTH: "1 mês",
    PeriodChoices.SEMESTER: "1 semestre",
    PeriodChoices.YEAR: "1 ano",
}
