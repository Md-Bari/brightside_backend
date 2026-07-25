"""
Repoint ChatSession.user at CustomerUser.user_id so that
``chat_sessions.user_id`` stores the customer's UUID instead of the
integer primary key.

A plain AlterField cannot do this: PostgreSQL cannot cast bigint to uuid.
So a temporary column is added, populated by joining on the old integer
key, and then swapped into place. Existing sessions keep their owner.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_uuid_customeruser_user_id'),
        ('chat_sessions', '0003_rename_uuid_session_id_remove_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='user_new',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sessions_tmp',
                to='users.customeruser',
                to_field='user_id',
            ),
        ),
        migrations.RunSQL(
            sql="""
                UPDATE chat_sessions cs
                SET user_new_id = cu.user_id
                FROM customer_users cu
                WHERE cs.user_id = cu.id;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RemoveField(
            model_name='chatsession',
            name='user',
        ),
        migrations.RenameField(
            model_name='chatsession',
            old_name='user_new',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='chatsession',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sessions',
                to='users.customeruser',
                to_field='user_id',
            ),
        ),
    ]
