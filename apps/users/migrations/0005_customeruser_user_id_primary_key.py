"""
Make CustomerUser.user_id the primary key and drop the surrogate integer id.

Django cannot express a primary key swap as a plain AlterField, so the
database side is done with explicit SQL. The foreign key on chat_sessions
depends on the UNIQUE constraint over customer_users.user_id, so it is
dropped and restored around the swap; it ends up pointing at the same
column, now backed by the primary key index instead.

Forward-only: reversing would have to invent integer ids.
"""
import uuid

from django.db import migrations, models

FORWARD_SQL = """
DO $$
DECLARE
    v_fk text;
    v_uq text;
BEGIN
    -- 1. Release the dependency chat_sessions has on the unique constraint.
    SELECT conname INTO v_fk
      FROM pg_constraint
     WHERE conrelid = 'chat_sessions'::regclass
       AND confrelid = 'customer_users'::regclass
       AND contype = 'f';
    IF v_fk IS NOT NULL THEN
        EXECUTE format('ALTER TABLE chat_sessions DROP CONSTRAINT %I', v_fk);
    END IF;

    -- 2. Drop the surrogate key (its PRIMARY KEY constraint goes with it).
    ALTER TABLE customer_users DROP COLUMN IF EXISTS id;

    -- 3. Drop the standalone UNIQUE on user_id; the primary key replaces it.
    SELECT c.conname INTO v_uq
      FROM pg_constraint c
      JOIN pg_attribute a
        ON a.attrelid = c.conrelid AND a.attnum = ANY (c.conkey)
     WHERE c.conrelid = 'customer_users'::regclass
       AND c.contype = 'u'
       AND array_length(c.conkey, 1) = 1
       AND a.attname = 'user_id';
    IF v_uq IS NOT NULL THEN
        EXECUTE format('ALTER TABLE customer_users DROP CONSTRAINT %I', v_uq);
    END IF;

    -- 4. Promote user_id to primary key.
    ALTER TABLE customer_users ADD PRIMARY KEY (user_id);

    -- 5. Restore the foreign key against the new primary key.
    ALTER TABLE chat_sessions
        ADD CONSTRAINT chat_sessions_user_id_fk_customer_users_user_id
        FOREIGN KEY (user_id) REFERENCES customer_users (user_id)
        DEFERRABLE INITIALLY DEFERRED;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rename_uuid_customeruser_user_id'),
        ('chat_sessions', '0004_chatsession_user_fk_to_user_id'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=migrations.RunSQL.noop),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='customeruser',
                    name='id',
                ),
                migrations.AlterField(
                    model_name='customeruser',
                    name='user_id',
                    field=models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
            ],
        ),
    ]
