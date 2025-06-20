from django.shortcuts import render
from django.http import JsonResponse

def test_user_view(request):
    """
    Simple view to return a test user in JSON format.
    Reference: See .project/SPEC.md section on API endpoint conventions.
    """
    test_user = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com"
    }
    return JsonResponse(test_user)
