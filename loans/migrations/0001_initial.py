# Generated by Django 5.1.3 on 2024-11-07 10:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('phone_number', models.CharField(max_length=15)),
                ('monthly_salary', models.DecimalField(decimal_places=2, max_digits=10)),
                ('approved_limit', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.CharField(max_length=20, unique=True)),
                ('loan_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tenure', models.IntegerField(help_text='Loan tenure in months')),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('monthly_payment', models.DecimalField(decimal_places=2, max_digits=10)),
                ('emis_paid_on_time', models.BooleanField(default=True)),
                ('date_of_approval', models.DateField()),
                ('end_date', models.DateField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='loans.customer')),
            ],
        ),
    ]
