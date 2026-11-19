from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import FinanceEntryForm
from .models import FinanceEntry


@login_required
def finance_list(request):
    entries = FinanceEntry.objects.filter(user=request.user)
    total_einnahmen = entries.filter(category=FinanceEntry.EINNAHMEN).aggregate(total=Sum("amount"))["total"] or 0
    total_ausgaben = entries.filter(
        Q(category=FinanceEntry.AUSGABEN) | Q(category=FinanceEntry.FIXKOSTEN)
    ).aggregate(total=Sum("amount"))["total"] or 0
    context = {
        "entries": entries,
        "total_einnahmen": total_einnahmen,
        "total_ausgaben": total_ausgaben,
        "saldo": total_einnahmen - total_ausgaben,
    }
    return render(request, "finanzen/finance_list.html", context)


@login_required
def finance_add(request):
    if request.method == "POST":
        form = FinanceEntryForm(request.POST, instance=FinanceEntry(user=request.user))
        if form.is_valid():
            form.save()
            return redirect("finanzen:list")
    else:
        form = FinanceEntryForm(initial={"timestamp": timezone.now()})
    return render(request, "finanzen/finance_form.html", {"form": form})


@login_required
def finance_edit(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = FinanceEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("finanzen:list")
    else:
        form = FinanceEntryForm(instance=entry)
    return render(request, "finanzen/finance_form.html", {"form": form, "entry": entry})


@require_POST
@login_required
def finance_delete(request, pk):
    entry = get_object_or_404(FinanceEntry, pk=pk, user=request.user)
    entry.delete()
    return redirect("finanzen:list")
