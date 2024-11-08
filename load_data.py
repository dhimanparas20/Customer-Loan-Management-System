import os
import django
import pandas as pd
from datetime import datetime
from django.db import transaction
from decimal import Decimal

# Set the Django settings module (replace 'cas' with your project's settings module)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cas.settings')
django.setup()

from loans.models import Customer, Loan  # Import your models after setting up Django

# Function to convert values to boolean for the 'EMIs paid on Time' column
def convert_to_boolean(value):
    # Convert numerical and string values to boolean
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ['yes', 'y', '1']:
            return True
        elif value in ['no', 'n', '0']:
            return False
    if isinstance(value, (int, float)):
        return bool(value)  # Treat non-zero as True, 0 as False
    return False  # Default to False if the value can't be converted

# Load Customer data from Excel
customer_df = pd.read_excel('customer_data.xlsx')

with transaction.atomic():
    for _, row in customer_df.iterrows():
        # Update or create Customer records
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],  # Assuming 'Customer ID' is unique
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': int(row['Age']) if pd.notnull(row['Age']) else None,  # Ensure age is an integer
                'phone_number': str(row['Phone Number']),
                'monthly_salary': Decimal(row['Monthly Salary']) if pd.notnull(row['Monthly Salary']) else None,
                'approved_limit': Decimal(row['Approved Limit']) if pd.notnull(row['Approved Limit']) else None
            }
        )
    print("Customer data loaded successfully")

# Load Loan data from Excel
loan_df = pd.read_excel('loan_data.xlsx')

with transaction.atomic():
    for _, row in loan_df.iterrows():
        # Get the Customer instance based on 'Customer ID'
        customer = Customer.objects.get(customer_id=row['Customer ID'])
        
        # Convert date columns correctly (assuming they are in string format in the Excel sheet)
        date_of_approval = pd.to_datetime(row['Date of Approval'], format='%d/%m/%Y').date() if pd.notnull(row['Date of Approval']) else None
        end_date = pd.to_datetime(row['End Date'], format='%d/%m/%Y').date() if pd.notnull(row['End Date']) else None

        # Update or create Loan records
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],  # Assuming 'Loan ID' is unique
            defaults={
                'customer': customer,
                'loan_amount': Decimal(row['Loan Amount']) if pd.notnull(row['Loan Amount']) else None,
                'tenure': int(row['Tenure']) if pd.notnull(row['Tenure']) else None,
                'interest_rate': Decimal(row['Interest Rate']) if pd.notnull(row['Interest Rate']) else None,
                'monthly_payment': Decimal(row['Monthly payment']) if pd.notnull(row['Monthly payment']) else None,
                'emis_paid_on_time': convert_to_boolean(row['EMIs paid on Time']),  # Convert to boolean
                'date_of_approval': date_of_approval,
                'end_date': end_date
            }
        )
    print("Loan data loaded successfully")
