"""
Make ChatSession.session_id the primary key and drop the surrogate integer
id, mirroring the same change on CustomerUser.

Nothing references chat_sessions, so the swap is a straight drop-column +
promote. The FK on user is also re-declared without ``to_field``: now that
CustomerUser.user_id is that model's primary key, it is the default target
and the column is unchanged, so that part is state-only.

Forward-only: reversing would have to invent integer ids.
"""
import uuid

import django.db.models.deletion
from django.db import migrations, models

FORWARD_SQL = """
DO $$
DECLARE
    v_uq text;
BEGIN
    -- 1. Drop the surrogate key (its PRIMARY KEY constraint goes with it).
    ALTER TABLE chat_sessions DROP COLUMN IF EXISTS id;

    -- 2. Drop the standalone UNIQUE on session_id; the primary key replaces it.
    SELECT c.conname INTO v_uq
      FROM pg_constraint c
      JOIN pg_attribute a
        ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
     WHERE c.conrelid = 'chat_sessions'::regclass
       AND c.contype = 'u'
       AND array_length(c.conkey, 1) = 1
       AND a.attname = 'session_id';
    IF v_uq IS NOT NULL THEN
        EXECUTE format('ALTER TABLE chat_sessions DROP CONSTRAINT %I', v_uq);
    END IF;

    -- 3. Promote session_id to primary key.
    ALTER TABLE chat_sessions ADD PRIMARY KEY (session_id);
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('chat_sessions', '0004_chatsession_user_fk_to_user_id'),
        ('users', '0005_customeruser_user_id_primary_key'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='chatsession',
                    name='id',
                ),
                migrations.AlterField(
                    model_name='chatsession',
                    name='session_id',
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name='chatsession',
                    name='user',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sessions',
                        to='users.customeruser',
                    ),
                ),
            ],
        ),
    ]
