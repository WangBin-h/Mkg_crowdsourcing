# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Question, Expert, Asker
from .DTA_utils import DTAAlgorithm  # 引入你的分配算法
from django.utils import timezone

# 信号处理函数 - 当用户提交问题时触发
@receiver(post_save, sender=Question)
def handle_question_submission(sender, instance, created, **kwargs):
    if created:  # 确保是新创建的问题
        print(f"New question submitted: {instance.title}")
        current_time = timezone.now()
        dta_algorithm = DTAAlgorithm(method='Greedy')  # 你可以根据需要选择不同的分配方法
        dta_algorithm.allocate_tasks(current_time)

# 信号处理函数 - 当专家完成注册时触发
@receiver(post_save, sender=Expert)
def handle_expert_registration(sender, instance, created, **kwargs):
    if created:  # 确保是新注册的专家
        print(f"New expert registered: {instance.expert_id}")
        current_time = timezone.now()
        dta_algorithm = DTAAlgorithm(method='Greedy')  # 选择分配方法
        dta_algorithm.allocate_tasks(current_time)

# 信号处理函数 - 当专家回答完问题时触发
@receiver(post_save, sender=Question)
def handle_expert_answer_submission(sender, instance, created, **kwargs):
    if instance.answered:  # 如果问题已回答
        print(f"Expert answered the question: {instance.title}")
        current_time = timezone.now()
        dta_algorithm = DTAAlgorithm(method='Greedy')  # 选择分配方法
        dta_algorithm.allocate_tasks(current_time)
