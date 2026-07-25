import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_sessions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatsession',
            name='session_id',
        ),
        migrations.AlterField(
            model_name='chatsession',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
