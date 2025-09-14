# claims/views.py (Corrected)
# claims/views.py (Corrected)

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.exceptions import ObjectDoesNotExist
# ** THE FIX IS HERE: Import BOTH models **
from .models import Claim, ClaimDetail

def claim_list(request):
    queryset = Claim.objects.select_related('details').all().order_by('-discharge_date')
    patient_name = request.GET.get('patient_name', '').strip()
    insurer = request.GET.get('insurer', '').strip()
    status = request.GET.get('status', '').strip()

    if patient_name:
        queryset = queryset.filter(patient_name__icontains=patient_name)
    if insurer:
        queryset = queryset.filter(insurer_name=insurer)
    if status:
        queryset = queryset.filter(status=status)

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'page_obj': page_obj,
        'insurers': Claim.objects.values_list('insurer_name', flat=True).distinct().order_by('insurer_name'),
        'status_choices': Claim.STATUS_CHOICES,
        'query_params': query_params.urlencode(),
        'current_patient_name': patient_name,
        'current_insurer': insurer,
        'current_status': status,
    }

    if request.htmx:
        return render(request, 'claims/partials/claims_table.html', context)
        
    return render(request, 'claims/claim_list.html', context)


def claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    try:
        details = claim.details
    except ObjectDoesNotExist:
        details = None
    context = {'claim': claim, 'details': details}
    return render(request, 'claims/partials/claim_detail.html', context)


@require_POST
def flag_claim(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    claim.is_flagged = not claim.is_flagged
    claim.save()
    
    # After flagging, we must re-fetch the details to show the updated state
    try:
        details = claim.details
    except ObjectDoesNotExist:
        details = None
        
    context = {'claim': claim, 'details': details}
    response = render(request, 'claims/partials/claim_detail.html', context)
    response['HX-Trigger'] = 'claimUpdated'
    return response


@require_POST
def save_note(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    note_text = request.POST.get('notes', '')
    
    claim_detail, created = ClaimDetail.objects.get_or_create(claim=claim)
    claim_detail.notes = note_text
    claim_detail.save()

    context = {'claim': claim, 'details': claim_detail}
    response = render(request, 'claims/partials/claim_detail.html', context)
    response['HX-Trigger'] = 'claimUpdated'
    return response
