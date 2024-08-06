from django.db import models

class Scenario(models.Model):
    GENDER = {
        "MALE": "male",
        "FEMALE": "female"
    }

    name = models.CharField(max_length=100)
    description = models.TextField()
    gender = models.CharField(max_length=6, choices=GENDER)

    def __str__(self):
        return self.name
