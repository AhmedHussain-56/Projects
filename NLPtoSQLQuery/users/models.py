from django.db import models

# Create your models here.
class UserRegistrationModel(models.Model):
    name = models.CharField(max_length=100)
    loginid = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(unique=True, max_length=100)
    email = models.CharField(unique=True, max_length=100)
    locality = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    def __str__(self):
        return self.loginid
    class Meta:
        db_table = 'UserRegistrations'


class QueryLog(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    natural_query = models.TextField()
    sql_query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.username}"

    class Meta:
        db_table = "query_log"
