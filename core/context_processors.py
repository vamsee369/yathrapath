from .models import Temple


def footer_context(request):
    return {
        'total_temples': Temple.objects.count(),
    }
