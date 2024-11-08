from django.db import models
from django.db.models import Max

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_id})"

    def save(self, *args, **kwargs):
        self.approved_limit = round(self.monthly_salary * 36, -5)  # Approved limit = 36 * monthly_salary rounded to nearest lakh
        super().save(*args, **kwargs)

class Loan(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name="loans")
    loan_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField(help_text="Loan tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.BooleanField(default=True)
    date_of_approval = models.DateField()
    end_date = models.DateField()
    

    def save(self, *args, **kwargs):
        # Generate loan_id only if it's not already set
        if not self.loan_id:
            last_loan = Loan.objects.aggregate(last_loan=Max('loan_id'))['last_loan']
            # If there are existing loans, calculate next loan_id
            if last_loan:
                # Extract the number from the last loan_id, increment it, and format it
                last_number = int(last_loan.split("LOAN")[-1])
                new_number = last_number + 1
                self.loan_id = f"{new_number:03d}"
            else:
                # If no loans exist, start with LOAN001
                self.loan_id = "LOAN001"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name} {self.customer.last_name}"