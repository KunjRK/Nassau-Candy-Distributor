from django.shortcuts import render
from django.db.models import Avg, Count, Case, When, FloatField
from .models import Shipment

def dashboard_view(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    region = request.GET.get('region')
    mode = request.GET.get('mode')
    threshold = int(request.GET.get('threshold', 5))

    # 2. Apply Filters to QuerySet
    shipments = Shipment.objects.all()
    if start_date and end_date:
        shipments = shipments.filter(order_date__range=[start_date, end_date])
    if region and region != "All":
        shipments = shipments.filter(region=region)
    if mode and mode != "All":
        shipments = shipments.filter(ship_mode=mode)

    # 3. Calculate Dashboard Modules / KPIs
    # Calculate Lead Time via Database Annotation
    annotated = shipments.annotate(
        l_time=ExpressionWrapper(F('ship_date') - F('order_date'), output_field=fields.DurationField())
    )

    # Route Efficiency Overview
    route_stats = annotated.values('route').annotate(
        avg_lt=Avg('l_time'),
        count=Count('id')
    ).order_by('avg_lt')

    # Delay Frequency Calculation
    total_count = shipments.count()
    # Mocking threshold logic for the summary
    delay_count = sum(1 for s in shipments if s.lead_time > threshold)
    delay_freq = (delay_count / total_count * 100) if total_count > 0 else 0

    context = {
        'shipments': shipments[:100], # For Route Drill-Down
        'route_stats': route_stats,
        'delay_freq': delay_freq,
        'total_volume': total_count,
        'threshold': threshold,
    }
    return render(request, 'dashboard2.html', context)