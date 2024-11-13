# MonastirCenter/custom_middleware.py

from django.http import HttpResponseForbidden

class CustomAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and not request.user.is_authenticated:
            # If the response is a 404 error and the user is not authenticated,
            # return a custom error response.
            return HttpResponseForbidden("You don't have access to this page.")
        return response
