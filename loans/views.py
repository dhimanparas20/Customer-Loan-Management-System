from rest_framework import viewsets,status
from rest_framework.response import Response
from loans.models import Customer
from .serializers import CustomerSerializer
from rest_framework.decorators import action
from django.db.models import Sum
from loans.models import Customer, Loan
from .serializers import CheckEligibilityRequestSerializer, CheckEligibilityResponseSerializer,CreateLoanRequestSerializer,CreateLoanResponseSerializer,LoanSerializer,LoanListSerializer
from datetime import datetime,timedelta
from rest_framework.views import APIView
from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

class CustomerViewSet(viewsets.ViewSet):
    def create(self, request):
        # Validate and deserialize data
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            # Save the customer and return the response
            customer = serializer.save()  # The approved_limit will be calculated automatically
            return Response({
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': customer.monthly_salary,
                'approved_limit': customer.approved_limit,
                'phone_number': customer.phone_number
            }, status=status.HTTP_201_CREATED)
        else:
            # If data is not valid, return errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoanEligibilityAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Deserialize the incoming request data
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            try:
                # Fetch the customer from the database
                customer = Customer.objects.get(customer_id=customer_id)
                
                # Calculate the credit score components
                # 1. Past loans paid on time
                past_loans = Loan.objects.filter(customer=customer)
                loans_paid_on_time = past_loans.filter(emis_paid_on_time=True).count()
                
                # 2. Number of loans taken
                num_loans_taken = past_loans.count()
                
                # 3. Loan activity in the current year (can be filtered by date)
                current_year_loans = past_loans.filter(date_of_approval__year=datetime.now().year).count()
                
                # 4. Loan approved volume (total amount of loans approved)
                approved_volume = past_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
                
                # Calculate the credit score based on the given criteria
                credit_score = (loans_paid_on_time * 10 + num_loans_taken * 5 +
                                current_year_loans * 10 + approved_volume / 1000000)  # example scaling factor

                # 5. If current loans exceed the approved limit, credit score becomes 0
                current_loans_sum = past_loans.filter(date_of_approval__isnull=False).aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
                if current_loans_sum > customer.approved_limit:
                    credit_score = 0

                # Check the eligibility based on the credit score
                if credit_score > 50:
                    approval = True
                    corrected_interest_rate = interest_rate
                elif 50 >= credit_score > 30:
                    approval = True
                    corrected_interest_rate = max(interest_rate, 12)
                elif 30 >= credit_score > 10:
                    approval = True
                    corrected_interest_rate = max(interest_rate, 16)
                else:
                    approval = False
                    corrected_interest_rate = interest_rate  # No loan approval
                
                # If total EMIs exceed 50% of monthly salary, don't approve loans
                current_emis = past_loans.filter(date_of_approval__isnull=False).aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
                if current_emis > Decimal(0.5) * customer.monthly_salary:
                    approval = False

                # Calculate the monthly installment for the loan
                if approval:
                    monthly_installment = loan_amount / tenure
                else:
                    monthly_installment = 0

                # Prepare the response data
                response_data = {
                    'customer_id': customer_id,
                    'approval': approval,
                    'interest_rate': interest_rate,
                    'corrected_interest_rate': corrected_interest_rate,
                    'tenure': tenure,
                    'monthly_installment': monthly_installment
                }

                # Serialize and return the response
                response_serializer = CheckEligibilityResponseSerializer(data=response_data)
                if response_serializer.is_valid():
                    return Response(response_serializer.data)
                else:
                    return Response(response_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            except Customer.DoesNotExist:
                return Response({"detail": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CreateLoanView(APIView):

    def post(self, request, *args, **kwargs):
        # Step 1: Validate request data
        serializer = CreateLoanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract the validated data
        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        try:
            # Step 2: Fetch customer and check eligibility
            customer = get_object_or_404(Customer, customer_id=customer_id)

            # Check if current loans exceed the approved limit
            past_loans = Loan.objects.filter(customer=customer)
            current_loans_sum = past_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or Decimal(0)

            if current_loans_sum > customer.approved_limit:
                return Response({
                    'loan_approved': False,
                    'message': 'Current loans exceed the approved limit.',
                    'customer_id': customer_id,
                    'monthly_installment': 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate the monthly installment
            monthly_installment = loan_amount / tenure

            # Step 3: Check eligibility and approve/reject loan
            if loan_amount > customer.approved_limit:
                return Response({
                    'loan_approved': False,
                    'message': 'Requested loan amount exceeds approved limit.',
                    'customer_id': customer_id,
                    'monthly_installment': monthly_installment
                }, status=status.HTTP_400_BAD_REQUEST)

            # If eligible, approve the loan and create loan entry
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                monthly_payment=monthly_installment,
                tenure=tenure,
                date_of_approval=datetime.now(),
                end_date=datetime.now() + timedelta(days=30 * tenure)
            )

            # Return success response
            return Response({
                'loan_id': loan.id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved successfully.',
                'monthly_installment': monthly_installment
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'loan_approved': False,
                'message': str(e),
                'customer_id': customer_id,
                'monthly_installment': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

class ViewLoanDetails(APIView):
    def get(self, request, loan_id, *args, **kwargs):
        # Fetch the loan by loan_id
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            raise NotFound(detail="Loan not found with the provided loan_id", code=404)

        # Serialize the loan and customer details
        loan_serializer = LoanSerializer(loan)
        
        return Response(loan_serializer.data)
    
class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        # Fetch the loans associated with the given customer_id
        loans = Loan.objects.filter(customer__customer_id=customer_id)

        # If no loans are found, return a 404 response
        if not loans.exists():
            raise NotFound(detail="No loans found for the provided customer_id", code=404)

        # Serialize the loan details
        loan_serializer = LoanListSerializer(loans, many=True)
        
        return Response(loan_serializer.data)    