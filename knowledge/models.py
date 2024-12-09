from django.db import models
from django.utils import timezone

class NormalUser(models.Model):
    # 用户名称
    name = models.CharField(max_length=100)
    
    # 用户类型，默认值是 'inquirer'（提问者）
    USER_TYPE_CHOICES = [
        ('expert', 'Expert'),     # 专家
        ('inquirer', 'Inquirer')  # 提问者
    ]
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='inquirer')
    
    def __str__(self):
        return self.name
    
class asker(models.Model):
    owner = models.ForeignKey(NormalUser, on_delete=models.SET_NULL, null=True)
	
class expert(models.Model):
    owner = models.ForeignKey(NormalUser, on_delete=models.SET_NULL, null=True)
    expert_id = models.CharField(max_length=100)
    max_tasks = models.IntegerField(default=3)
    skill_level = models.IntegerField(default=1)
    arrive_time = models.DateTimeField(default=timezone.now)
    leave_time = models.DateTimeField(default=timezone.now + timezone.timedelta(days=1))
    credibility = models.CharField(max_length=100, default=0.5)