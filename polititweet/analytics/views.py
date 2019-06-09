from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from unicodecsv import csv
from .models import Visit

@user_passes_test(lambda u: u.is_superuser)
def index(request):
    visits = Visit.objects.all()
    ips = [distinct_ip["ip"] for distinct_ip in visits.values('ip').distinct()]
    urls = [distinct_url["url"] for distinct_url in visits.values('url').distinct()]

    # tabulate URLs
    print(urls)
    url_counts = {url: 0 for url in urls}
    for visit in visits:
        url_counts[visit.url] += 1

    # tabulate IPs
    ip_counts = {ip: 0 for ip in ips}
    for visit in visits:
        ip_counts[visit.ip] += 1

    if request.GET.get('export', None) != None:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'

        writer = csv.writer(response)
        writer.writerow(['ip', 'url', 'time'])
        for visit in visits:
            writer.writerow([visit.ip, visit.url, visit.time])

        return response

    message = None

    if request.GET.get('delete', None) != None:
        time = request.GET.get('delete')
        if time == "week":
            deleted_objects = Visit.objects.filter(time__lt=timezone.now() - timedelta(days=7)).delete()
            message = "Successfully deleted all visits older than one week."
        if time == "day":
            deleted_objects = Visit.objects.filter(time__lt=timezone.now() - timedelta(days=1)).delete()
            message = "Successfully deleted all visits older than one day."
        if time == "all":
            deleted_objects = Visit.objects.all().delete()
            message = "Successfully deleted all visits."

    return render(request, "analytics/dashboard.html", context={
        "visits": visits.count(),
        "ips": len(ips),
        "urls": len(urls),
        "message": message,
        "top_urls": [(url, url_counts[url]) for url in sorted(urls, key=lambda k: url_counts[k], reverse=True)[:10]],
        "top_ips": [(ip, ip_counts[ip]) for ip in sorted(ips, key=lambda k: ip_counts[k], reverse=True)[:10]],
        "recent_visits": visits.order_by("-time")[:25],
    })