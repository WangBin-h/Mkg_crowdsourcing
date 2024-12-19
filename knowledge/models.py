from datetime import timedelta
from django.db import models
from django.utils import timezone


def default_leave_time():
    return timezone.now() + timedelta(days=1)

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
    
class Asker(models.Model):
    owner = models.ForeignKey(NormalUser, on_delete=models.SET_NULL, null=True)
	
class Question(models.Model):
    tasks_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()
    asked_by = models.ForeignKey(Asker, on_delete=models.CASCADE, null=True)
    answered_by = models.ForeignKey('Expert', on_delete=models.SET_NULL, null=True)
    answered = models.BooleanField(default=False)
    answer = models.TextField(null=True, blank=True)  # 只有在回答后才会有内容

    def __str__(self):
        return self.title
    
class Expert(models.Model):
    owner = models.ForeignKey(NormalUser, on_delete=models.SET_NULL, null=True)
    expert_id = models.CharField(max_length=100)
    max_tasks = models.IntegerField(default=3)
    skill_level = models.IntegerField(default=1)
    arrive_time = models.DateTimeField(default=timezone.now)
    leave_time = models.DateTimeField(default=default_leave_time)  # 使用普通函数作为默认值
    credibility = models.CharField(max_length=100, default="0.5")
    questionare_done = models.BooleanField(default=False)

