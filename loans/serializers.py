from rest_framework import serializers
from .models import Customer,Loan
import datetime

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'age', 'monthly_salary', 'phone_number', 'approved_limit']
        read_only_fields = ['approved_limit']  # Make 'approved_limit' read-only

    # Optional: You can add any validation or custom methods here

class LoanSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_payment', 'tenure', 'customer']

class CheckEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()

class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()

class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(required=False)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField(max_length=255)
    monthly_installment = serializers.DecimalField(max_digits=10, decimal_places=2)    

class LoanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_payment', 'tenure','repayments_left']

    # Adding a custom field to calculate the number of EMIs left
    repayments_left = serializers.SerializerMethodField()

    def get_repayments_left(self, obj):
        # Calculate the number of EMIs left, assuming 'tenure' represents the total number of months
        current_month = datetime.datetime.now().month
        repayments_left = obj.tenure - current_month  # This is a simple calculation, adjust as necessary.
        return repayments_left    