from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Share, Fare
# from .forms import 

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

class Home(LoginView):
    template_name = 'home.html'

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
    fields = ['name', 'amount', 'date', 'category', 'paid_by', 'split_between']

    def form_valid(self, form):
        form.instance.share_id = self.kwargs['share_id']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self): # renders correct info in form
        form = super().get_form()
        form.fields['split_between'].required = False
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
    fields = ['name', 'amount', 'date', 'category', 'paid_by', 'split_between']

    def dispatch(self, request, *args, **kwargs): # protects URL route from those who do not have access
        self.share = get_object_or_404( # Django shortcut to return single object and if not found generate 404
            Share.objects.filter(participants=request.user).distinct(), pk=self.kwargs['share_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self): # renders correct info in form
        form = super().get_form()
        form.fields['split_between'].required = False
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

    



















    





