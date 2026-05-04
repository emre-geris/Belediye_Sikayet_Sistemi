from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0004_llm_output_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='complaint',
            name='llm_summary',
        ),
    ]
