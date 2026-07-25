from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customeruser_human_escalation_required'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customeruser',
            old_name='uuid',
            new_name='user_id',
        ),
    ]
