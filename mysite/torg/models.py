from django.db import models
from django.conf import settings

class OngoingManager(models.Manager):
    def get_queryset(self):
        return super(OngoingManager, self).get_queryset().filter(ongoing=True)

class CompletedManager(models.Manager):
    def get_queryset(self):
        return super(CompletedManager, self).get_queryset().filter(ongoing=False)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return 'Profil użytkownika {}'.format(self.user.username)

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    slug = models.SlugField(max_length=250, unique_for_date='created')
    created = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
    ongoing = models.BooleanField(default=True)
    status_ongoing = OngoingManager()
    status_completed = CompletedManager()
    objects = models.Manager()



    # Powoduje, że nie można dwóch takich samych turniejów przez jednego autora
    class Meta:
        ordering = ('-created',)
        unique_together = [['author', 'name']]

    def __str__(self):
        return 'Organizator: {}, turniej: {}'.format(self.author.username, self.name)

class PlayerTeam(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    # Powoduje, że nie można dodać gracza o tej samej nazwie do jednego turnieju
    class Meta:
        unique_together = [['tournament', 'name']]

    def __str__(self):
        return 'Gracz/Drużyna: {}'.format(self.name)