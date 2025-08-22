from django.shortcuts import render
from django.conf import settings
import requests
from django.contrib.auth.decorators import login_required, permission_required
from collections import Counter
from datetime import datetime

@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
def dashboard(request):
    response = requests.get(settings.API_URL)
    posts_dict = response.json()  # Es un dict, no una lista

    # Extraer solo los valores (los datos de cada registro)
    posts = list(posts_dict.values())

    # Filtrar solo registros válidos (con user, email y message)
    valid_posts = [
        p for p in posts
        if p.get('user') and p.get('email') and p.get('message')
    ]

    total_responses = len(valid_posts)
    total_users = len(set(p['user'] for p in valid_posts))
    total_emails = len(set(p['email'] for p in valid_posts))
    total_messages = len(set(p['message'] for p in valid_posts))

    # Tabla: usuario y mensaje
    table_rows = [
        {'user': p['user'], 'message': p['message']}
        for p in valid_posts
    ]

    # Gráfico: respuestas por fecha (agrupa por día)
    date_counts = Counter()
    for p in valid_posts:
        date_str = p.get('date') or p.get('timestamp')
        if date_str:
            try:
                # Intenta formato con milisegundos y Z
                date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").date()
            except ValueError:
                try:
                    # Intenta formato sin Z
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f").date()
                except ValueError:
                    try:
                        # Intenta formato sin milisegundos
                        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()
                    except Exception:
                        continue
            date_counts[date_obj] += 1

    chart_labels = [str(date) for date in sorted(date_counts)]
    chart_data = [date_counts[date] for date in sorted(date_counts)]

    data = {
        'title': "Park-A-Pal Dashboard",
        'total_responses': total_responses,
        'total_users': total_users,
        'total_emails': total_emails,
        'total_messages': total_messages,
        'table_rows': table_rows,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'dashboard/index.html', data)