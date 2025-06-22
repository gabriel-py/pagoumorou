# pagoumorou/migrations/0007_add_performance_indexes.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagoumorou', '0006_alter_destination_destination_type'), # MAKE SURE THIS DEPENDENCY MATCHES YOUR LAST MIGRATION FILE!
    ]

    operations = [
        # Index for RoomPrice filtering by period and room
        migrations.AddIndex(
            model_name='roomprice',
            index=models.Index(fields=['period', 'room'], name='pagoumorou_roomprice_period_room_idx'),
        ),
        # Index for Room filtering by gender
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['accept_men'], name='room_accept_men_idx'),
        ),
        migrations.AddIndex(
            model_name='room',
            index=models.Index(fields=['accept_women'], name='room_accept_women_idx'),
        ),
        # Index for Rental filtering by room and dates for availability
        migrations.AddIndex(
            model_name='rental',
            index=models.Index(fields=['room', 'start_date', 'end_date'], name='rental_room_dates_idx'),
        ),
    ]