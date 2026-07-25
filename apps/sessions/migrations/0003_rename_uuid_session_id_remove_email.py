from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat_sessions', '0002_remove_chatsession_session_id_alter_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatsession',
            old_name='uuid',
            new_name='session_id',
        ),
        # The session's email duplicated customer_users.email; it is now
        # read through the user relation instead.
        migrations.RemoveField(
            model_name='chatsession',
            name='email',
        ),
    ]
