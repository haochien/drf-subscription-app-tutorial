from django.db import models


class TestModel(models.Model):
    test_id = models.AutoField(primary_key=True)
    display_name = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.IntegerField(default=1)


    def __str__(self):
        return str(self.display_name)