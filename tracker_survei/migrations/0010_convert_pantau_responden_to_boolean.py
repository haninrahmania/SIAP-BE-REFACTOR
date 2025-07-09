from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('tracker_survei', '0009_trackersurvei_cleaning_personil_and_more'),
    ]

    operations = [
        # First, convert all existing text labels into boolean TRUE/FALSE
        migrations.RunSQL(
            sql="""
                UPDATE tracker_survei
                SET pantau_responden = CASE
                    WHEN pantau_responden IN ('IN_PROGRESS', 'FINISHED', 'DELAYED')
                        THEN TRUE
                    ELSE FALSE
                END
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Then let Django ALTER the column type to boolean without failing
        migrations.AlterField(
            model_name='trackersurvei',
            name='pantau_data_cleaning',
            field=models.CharField(choices=[('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished'), ('DELAYED', 'Delayed'), ('CLEANING', 'Cleaning in Progress'), ('CLEANED', 'Cleaned')], default='NOT_STARTED', max_length=30),
        ),
        migrations.AlterField(
            model_name='trackersurvei',
            name='pantau_responden',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='trackersurvei',
            name='pra_survei',
            field=models.CharField(choices=[('NOT_STARTED', 'Not Started'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished'), ('DELAYED', 'Delayed'), ('PRE_TEST', 'Pre-Test'), ('SKIP_PRE_TEST', 'Tidak Perlu Pre-Test')], default='NOT_STARTED', max_length=30),
        ),
    ]