from django.shortcuts import render


def panel_view(request):
    return render(request, 'mobile/panel.html')