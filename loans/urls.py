from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, LoanEligibilityAPIView,CreateLoanView,ViewLoanDetails,ViewLoansByCustomer

router = DefaultRouter()
router.register(r'register', CustomerViewSet, basename='register') 

urlpatterns = [
    path('', include(router.urls)),  
    path('check-eligibility/', LoanEligibilityAPIView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<str:loan_id>/', ViewLoanDetails.as_view(), name='view_loan_details'),
    path('view-loans/<int:customer_id>/', ViewLoansByCustomer.as_view(), name='view_loans_by_customer'),
]
