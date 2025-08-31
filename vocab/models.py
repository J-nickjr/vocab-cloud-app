from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    definition = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} 查詢 {self.word}"
