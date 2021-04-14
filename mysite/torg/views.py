from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, TournamentRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Tournament
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.shortcuts import redirect

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username = cd['username'], password = cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Uwierzytelnianie zakończyło sie sukcesem')
                else:
                    return HttpResponse('Konto jest zablokowane.')
            else:
                return HttpResponse('Nieprawidłowe dane uwierzytelniające.')

    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            profile = Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard'})

@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form=UserEditForm(instance=request.user)
        profile_form=ProfileEditForm(instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})

@login_required
def create_tournaments(request):
    if request.method == 'POST':
        users = get_user_model()
        obj = users.objects.get(id=request.user.id)
        print(obj)
        tournament_form = TournamentRegistrationForm(initial={'author':obj}, data=request.POST)
        if tournament_form.is_valid():
            new_tournament = tournament_form.save(commit=False)
            new_tournament.author = obj
            try:
                new_tournament.save()

            except IntegrityError:
                message = "Turniej o podanej nazwie już istnieje, proszę zmień nazwę dla nowego turnieju"
                return render(request,
                              'account/create_tournaments.html',
                                          {'tournament_form': tournament_form,
                                          "message": message})

            return redirect('/account/ongoing_tournaments/')
    else:
        tournament_form = TournamentRegistrationForm()

    return render(request,
                  'account/create_tournaments.html',
                  {'tournament_form': tournament_form})

@login_required
def ongoing_tournaments(request):
    tournaments = Tournament.status_ongoing.all()
    return render(request,
                  'account/ongoing_tournaments.html',
                  {'tournaments':tournaments})

@login_required
def completed_tournaments(request):
    tournaments = Tournament.status_completed.all()
    return render(request,
                  'account/completed_tournaments.html',
                  {'tournaments':tournaments})