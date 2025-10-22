from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.forms import UserCreationForm

from decimal import Decimal, ROUND_HALF_UP # typically used when handling dollar amounts

from .models import Share, Fare
from .forms import FareForm

# Create your views here.

####

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('share-index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

class Login(LoginView):
    template_name = 'login.html'

class Home(ListView):
    model = Share
    context_object_name = 'shares'
    template_name = 'home.html'

    def get_queryset(self):
        return (Share.objects.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shares = context['shares']

        total_fares = 0
        for share in shares:
            total_fares += len(share.fare_set.all())

        total_expenses = 0
        for share in shares:
            for fare in share.fare_set.all():
                total_expenses += fare.amount
        print(total_expenses)
       
        context["total_shares"] = shares.count()
        context["total_fares"] = total_fares
        context["total_expenses"] = total_expenses
        
        return context
    

def about(request):
    return render(request, 'about.html')

####

class ShareIndex(LoginRequiredMixin, ListView):
    model = Share
    context_object_name = 'shares'
    template_name = 'shares/index.html'
    ordering = ['-created_at']

    def get_queryset(self):
        return (Share.objects.filter(participants=self.request.user)) # restricts the query set to only participants (inclduing creator)


class ShareDetail(DetailView):
    model = Share
    template_name = 'shares/detail.html'
    
    def get_queryset(self):
        return (Share.objects.filter(participants=self.request.user)) # restricts the query set to only participants (inclduing creator)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        share = self.object
        user = self.request.user
        fares = share.fare_set.all()
        
        total_expenses = sum(f.amount for f in fares)

        my_expenses = Decimal("0")
        for fare in fares:
            count = fare.split_between.count()
            if count and fare.split_between.filter(pk=user.pk).exists():
                my_expenses += (fare.amount / count)

        my_expenses = my_expenses.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        category_totals = {}
        for fare in fares:
            label = fare.get_category_display()
            category_totals[label] = category_totals.get(label, Decimal("0")) + fare.amount
        sorted_category_totals = dict(sorted(category_totals.items(), key=lambda item: item[1], reverse=True)) # sorting by value in descending order

        participants = list(share.participants.all())
        balances = []

        for p in participants:

            owes = Decimal("0")
            for fare in fares:
                count = fare.split_between.count()
                if count and fare.split_between.filter(pk=p.pk).exists():
                    owes += (fare.amount / count)

            paid = Decimal("0")
            for fare in fares:
                if fare.paid_by_id == p.pk:
                    paid += fare.amount

            net = paid - owes

            owes = owes.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            paid = paid.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            net = net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            balances.append({"participant": p, "owes": owes, "paid": paid, "net": net})
            print(balances)
            sorted_balances = sorted(balances, key=lambda p: (p["participant"].id != user.id)) # sorts logged in user first
            
        context["total_fares"] = fares.count()
        context["total_expenses"] = total_expenses
        context["my_expenses"] = my_expenses
        context["balances"] = sorted_balances
        context["category_totals"] = sorted_category_totals

        return context

class ShareCreate(LoginRequiredMixin, CreateView):
    model = Share
    fields = ['title', 'currency', 'participants']

    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        self.object.participants.add(self.request.user) # add creator as a participant
        return response

class ShareUpdate(LoginRequiredMixin, UpdateView):
    model = Share
    fields = ['title', 'currency', 'participants']

    def get_queryset(self):
        return (Share.objects.filter(creator=self.request.user)) # restricts the query set to only creator

class ShareDelete(LoginRequiredMixin, DeleteView):
    model = Share
    success_url = '/shares/'

    def get_queryset(self):
        return (Share.objects.filter(creator=self.request.user)) # restricts the query set to only creator
    
####

class FareCreate(LoginRequiredMixin, CreateView):
    model = Fare
    form_class = FareForm

    def form_valid(self, form):
        form.instance.share_id = self.kwargs['share_id']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self): # renders correct info in form
        form = super().get_form()
        form.fields['split_between'].queryset = self.share.participants.all() # limit form field to only show Share participants
        form.fields['paid_by'].queryset = self.share.participants.all() # limit form field to only show Share participants
        return form


class FareDetail(LoginRequiredMixin, DetailView):
    model = Fare
    template_name = 'shares/fare-detail.html'

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

class FareUpdate(LoginRequiredMixin, UpdateView):
    model = Fare
    form_class = FareForm

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self): # renders correct info in form
        form = super().get_form()
        form.fields['split_between'].queryset = self.share.participants.all() # limit form field to only show Share participants
        form.fields['paid_by'].queryset = self.share.participants.all() # limit form field to only show Share participants
        return form

class FareDelete(LoginRequiredMixin, DeleteView):
    model = Fare

    def get_success_url(self):
        return reverse("share-detail", kwargs={"pk": self.object.share.pk})

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

    



















    





