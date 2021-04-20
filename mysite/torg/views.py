from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, TournamentRegistrationForm, AddPlayerTeamForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Tournament, PlayerTeam
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

            return redirect('/account/waiting_tournaments/')
    else:
        tournament_form = TournamentRegistrationForm()

    return render(request,
                  'account/create_tournaments.html',
                  {'tournament_form': tournament_form})

@login_required
def edit_tournaments(request, year, month, day, tournament):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day)

    if request.method == 'POST':
        users = get_user_model()
        obj = users.objects.get(id=request.user.id)
        tournament_form = TournamentRegistrationForm(request.POST, request.FILES, instance=tournament)
        if tournament_form.is_valid():
            tournament_form.save()
            return redirect('/account/ongoing_tournaments/')

    tournament_form = TournamentRegistrationForm(instance=tournament)

    return render(request,
                  'account/edit_tournaments.html',
                  {'tournament_form': tournament_form})

@login_required
def ongoing_tournaments(request):
    tournaments = Tournament.status_ongoing.filter(author = request.user)

    return render(request,
                  'account/ongoing_tournaments.html',
                  {'tournaments':tournaments
                   })


@login_required
def completed_tournaments(request):
    tournaments = Tournament.status_completed.filter(author = request.user)
    return render(request,
                  'account/completed_tournaments.html',
                  {'tournaments':tournaments})

@login_required
def waiting_tournaments(request):
    tournaments = Tournament.status_waiting.filter(author = request.user)
    return render(request,
                  'account/waiting_tournaments.html',
                  {'tournaments':tournaments})

@login_required
def tournament_detail(request, year, month, day, tournament):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day)
    all_players = PlayerTeam.objects.all()
    players = [player for player in all_players if (player.tournament.name == tournament.name and
                                                    player.tournament.author == request.user)]


    if request.method == 'POST':
        player_team_form = AddPlayerTeamForm(initial={'tournament': tournament}, data=request.POST)
        if player_team_form.is_valid():
            new_player_team = player_team_form.save(commit=False)
            new_player_team.tournament = tournament
            try:
                new_player_team.save()

            except IntegrityError:
                message = "Gracz lub dryżyna o podanej nazwie już istnieje w tym turnieju, proszę zmienić nazwę"
                return render(request,
                                      'account/tournament_detail.html',
                                      {'tournament': tournament,
                                       'players': players,
                                        'player_team_form': player_team_form,
                                       'message': message})
            return HttpResponseRedirect(request.path_info)

    else:
        player_team_form = AddPlayerTeamForm()

    if request.method == "POST" and request.POST.get('delete_items'):
        items_to_delete = request.POST.getlist('delete_items')
        PlayerTeam.objects.filter(pk__in=items_to_delete).delete()
        return HttpResponseRedirect(request.path_info)

    return render(request,
                  'account/tournament_detail.html',
                  {'tournament': tournament,
                   'players': players,
                    'player_team_form': player_team_form})

@login_required
def tournament_delete(request,year, month, day, tournament):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day)

    if request.method == 'POST' and request.POST.get('delete'):
        tournament.delete()
        return redirect('/account/ongoing_tournaments/')

    return render(request,
                  'account/tournament_delete.html',
                  {'tournament': tournament})

@login_required
def tournament_complete(request,year, month, day, tournament):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day)

    if request.method == 'POST' and request.POST.get('complete'):
        tournament.tournament_status = 'complete'
        tournament.save()
        return redirect('/account/completed_tournaments/')

    return render(request,
                  'account/tournament_complete.html',
                  {'tournament': tournament})

@login_required
def tournament_start(request,year, month, day, tournament):
    tournament = get_object_or_404(Tournament, slug=tournament,
                                                created__year=year,
                                                created__month=month,
                                                created__day=day)

    if request.method == 'POST' and request.POST.get('start'):
        tournament.tournament_status = 'ongoing'
        tournament.save()
        return redirect('/account/ongoing_tournaments/')

    return render(request,
                  'account/tournament_start.html',
                  {'tournament': tournament})