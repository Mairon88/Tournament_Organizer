from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.defaultfilters import slugify
import jsonfield


class WaitingManager(models.Manager):
    def get_queryset(self):
        return super(WaitingManager, self).get_queryset().filter(tournament_status='waiting')

class OngoingManager(models.Manager):
    def get_queryset(self):
        return super(OngoingManager, self).get_queryset().filter(tournament_status='ongoing')

class CompletedManager(models.Manager):
    def get_queryset(self):
        return super(CompletedManager, self).get_queryset().filter(tournament_status='complete')

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return 'Profil użytkownika {}'.format(self.user.username)

class Tournament(models.Model):
    STATUS_CHOICES = (
        ('waiting', 'Waiting'),
        ('ongoing', 'Ongoing'),
        ('complete', 'Complete')
    )

    TOURNAMENT_TYPE = (
        ('tree', 'Drzewko'),
        ('league', 'Liga')
    )

    name = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    logo = models.ImageField(upload_to='tournaments/%Y/%m/%d', blank=True)
    slug = models.SlugField(max_length=250, unique_for_date='created')
    created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(auto_now=True)
    tournament_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='waiting')
    tournament_type = models.CharField(max_length=10, choices=TOURNAMENT_TYPE, default='tree')
    num_of_players = models.IntegerField(default=2, validators=[MinValueValidator(2), MaxValueValidator(32)])
    json_data = models.JSONField(default=dict)
    objects = models.Manager()
    status_waiting = WaitingManager()
    status_ongoing = OngoingManager()
    status_completed = CompletedManager()


    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.author)) #slugify(str(self.author)+"-"+self.name)
        super(Tournament, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tournament_detail',
                       args=[
                             self.created.year,
                             self.created.strftime('%m'),
                             self.created.strftime('%d'),
                             self.slug,
                             self.id])

    # Powoduje, że nie można dwóch takich samych turniejów przez jednego autora
    class Meta:
        ordering = ('-created',)
        unique_together = [['author', 'name']]

    def __str__(self):
        return self.name

class PlayerTeam(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)
    objects = models.Manager()

    # Powoduje, że nie można dodać gracza o tej samej nazwie do jednego turnieju
    class Meta:
        unique_together = [['tournament', 'name']]

    def __str__(self):
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player_team_1 = models.ForeignKey(PlayerTeam, on_delete=models.CASCADE, related_name='player_team_1')
    player_team_2 = models.ForeignKey(PlayerTeam, on_delete=models.CASCADE, related_name='player_team_2')
    score_1 = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    score_2 = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)

    objects = models.Manager()