# from django.shortcuts import render
# from .models import AvailableStock, Department, Complaint, Category

# # In views.py
# def showtotal(request):
#     # Count the number of stocks, departments, complaints, and categories
#     total_stocks = AvailableStock.objects.count()
#     total_departments = Department.objects.count()
#     total_complaints = Complaint.objects.count()
#     total_categories = Category.objects.count()

#     # Create a context dictionary
#     context = {
#         'total_stocks': total_stocks,
#         'total_departments': total_departments,
#         'total_complaints': total_complaints,
#         'total_categories': total_categories,
#         'something': 'available'
#     }

#     return context  # Return the context dictionary instead of rendering

# # In settings.py
# def custom_dashboard_callback(request, context):
#     from .views import showtotal
    
#     # Get the context dictionary directly
#     total_context = showtotal(request)
    
#     # Update the existing context with your totals
#     context.update(total_context)
    
#     return context


from django.shortcuts import render
from .models import AvailableStock, Department, Complaint, Category

def showtotal(request):
    # Check if the user is a superuser
    if request.user.is_superuser:
        # Count the number of stocks, departments, complaints, and categories
        total_stocks = AvailableStock.objects.count()
        total_departments = Department.objects.count()
        total_complaints = Complaint.objects.count()
        total_categories = Category.objects.count()

        return {
            'total_stocks': total_stocks,
            'total_departments': total_departments,
            'total_complaints': total_complaints,
            'total_categories': total_categories,
        }
    
    # Return an empty dictionary for non-superusers
    return {}

# In settings.py or wherever you define the custom dashboard callback
def custom_dashboard_callback(request, context):
    # Get the context dictionary directly
    total_context = showtotal(request)
    
    # Update the existing context with your totals
    context.update(total_context)
    
    return context