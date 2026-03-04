from django.shortcuts import redirect

class AgeGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/':
            if not request.session.get('is_adult'):
                return redirect('age_gate')

        response = self.get_response(request)
        return response