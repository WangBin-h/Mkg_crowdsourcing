from django.shortcuts import render
from django.http import JsonResponse

from knowledge.models import NormalUser, Asker, Expert, Question
from .redis_utils import get_medical_org_by_id, get_medical_orgs_by_category, get_graph_data
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import authenticate, logout

def register(request):
    if request.method == 'POST':
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        pwd = request.POST.get('password', '')
        user_type = request.POST.get('user_type', 'inquirer')  # 获取用户类型，默认为提问者
        
        # 检查用户名是否已存在
        if User.objects.filter(username=user_name).exists():
            # 如果用户名已经存在，返回注册页面并显示错误信息
            return render(request, 'knowledge/login.html', {'error': True, 'msg': '重复的用户名'})

        # 创建 User 实例
        user = User.objects.create_user(username=user_name, password=pwd, email=email)
        user.save()

        # 创建 NormalUser 实例
        normal_user = NormalUser(name=user_name, user_type=user_type)
        normal_user.save()

        # 创建 Asker 或 Expert 实例
        if user_type == 'inquirer':
            Asker.objects.create(owner=normal_user)
        elif user_type == 'expert':
            Expert.objects.create(owner=normal_user)

        return render(request, 'knowledge/login.html', {'success': True, 'show_login': True})

    return render(request, 'basic/register.html')

def login(request):
    return  render(request, 'knowledge/login.html')

def expert_dashboard(request):
    if request.user.is_authenticated:
        normal_user = request.user
        # 获取当前登录用户的专家信息
        ownername = NormalUser.objects.get(name=normal_user)
        expert = Expert.objects.get(owner=ownername)

        context = {
            'expert': expert,  # 将专家信息传递到模板
        }
        return render(request, 'knowledge/expert_dashboard.html', context)  # 专家专属页面

def inquirer_dashboard(request):
    if request.user.is_authenticated:
        normal_user = request.user
        ownername = NormalUser.objects.get(name=normal_user)
        asker = Asker.objects.get(owner=ownername)
        questions = Question.objects.filter(asked_by=asker)
        
        # 处理表单提交
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')

            # 创建新的问题
            new_question = Question.objects.create(
                title=title,
                content=content,
                asked_by=asker,
                answered=False
            )

            # 重定向到当前页面，确保新问题显示
            return redirect('inquirer_dashboard')
        
        context = {
            'asker': asker,
            'questions': questions,
        }
    return render(request, 'knowledge/inquirer_dashboard.html', context)  # 提问者专属页面

def login_in(request):
    if request.method == 'GET':
        return render(request, 'knowledge/login.html')

    elif request.method == 'POST':
        user_name = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(username=user_name, password=pwd)

        if user:
            if user.is_active:
                auth_login(request, user)

                # 获取对应的 NormalUser 实例
                normal_user = NormalUser.objects.get(name=user_name)

                # 根据用户类型跳转到不同的页面
                if normal_user.user_type == 'expert':
                    return redirect('../expert_dashboard/')  # 跳转到专家页面
                elif normal_user.user_type == 'inquirer':
                    return redirect('../inquirer_dashboard/')  # 跳转到提问者页面
            else:
                return render(request, 'knowledge/login.html', {'login_failed': True, 'msg': '用户未激活'})
        else:
            return render(request, 'knowledge/login.html', {'login_failed': True, 'msg': '账户名或密码错误，请重新登录'})

    return JsonResponse({'code': 405, 'msg': '方法不允许'}, status=405)

def logout_(request):
	logout(request)
	return redirect('/accounting/login')

def submit_answer(request):
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        question_id = request.POST.get('question_id')
        
        # question = Question.objects.get(id=question_id)

        # 创建并保存答案
        # answer = Answer.objects.create(question=question, expert=request.user.expert, text=answer_text)

        # 更新问题状态
        # question.status = 'answered'
        # question.save()

        return redirect('expert_dashboard')  # 跳转到专家页面
    
    
def medical_org_detail(request, org_id):
    """
    获取单个医疗机构详情
    """
    data = get_medical_org_by_id(org_id)
    if not data:
        return JsonResponse({"error": "Medical organization not found"}, status=404)
    return JsonResponse(data)

def medical_orgs_by_category(request, category):
    """
    获取特定类别的医疗机构列表
    """
    data = get_medical_orgs_by_category(category)
    return JsonResponse(data, safe=False)

def graph_data(request):
    """
    获取知识图谱中的图数据
    """
    data = get_graph_data()
    return JsonResponse(data, safe=False)

def medical_org_detail(request, org_id):
    data = get_medical_org_by_id(org_id)
    if not data:
        return render(request, "404.html", {"message": "Medical organization not found"})
    return render(request, "medical_org_detail.html", {"data": data})

def medical_org_detail(request, org_id):
    """
    渲染医疗机构详情页面
    """
    data = get_medical_org_by_id(org_id)
    if not data:
        return render(request, "404.html", {"message": "医疗机构未找到"})
    return render(request, "medical_org_detail.html", {"data": data})

def category_list(request):
    """
    渲染医疗机构类别列表页面
    """
    categories = ["医院", "诊所", "药店"]  # 假设类别是静态的或从 Redis 中获取
    return render(request, "category_list.html", {"categories": categories})


import random
import json
import numpy as np
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expert


# 读取JSON文件
def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# 简单的EM算法实现，计算专家的信誉度
def em_algorithm(answers, correct_answers, max_iter=100, epsilon=1e-4):
    """
    使用EM算法估计专家的信誉度
    :param answers: 用户提供的答案列表
    :param correct_answers: 正确答案列表
    :param max_iter: 最大迭代次数
    :param epsilon: 收敛阈值
    :return: 估计的信誉度
    """
    # 初始化信誉度为0.5
    credibility = 0.5

    for iteration in range(max_iter):
        # E-step: 计算专家答案的正确性概率
        correct_probabilities = []
        for i, answer in enumerate(answers):
            correct_answer = correct_answers[i]
            # 根据当前的信誉度计算回答正确的概率
            correctness_prob = credibility if answer == correct_answer else (1 - credibility)
            correct_probabilities.append(correctness_prob)

        # M-step: 更新信誉度，基于所有问题的正确性概率
        # 信誉度是所有正确答案概率的平均值
        credibility = np.mean(correct_probabilities)

        # 判断是否收敛
        if np.abs(credibility - np.mean(correct_probabilities)) < epsilon:
            break

    return credibility


# 问卷页面
@login_required
def questionare(request):
    # 判断用户是否为专家且尚未完成问卷
    try:
        expert = Expert.objects.get(owner=request.user.normaluser)
        if expert.questionare_done:  # 如果问卷已完成，直接跳转到专家仪表盘
            return redirect('expert_dashboard')
    except Expert.DoesNotExist:
        return redirect('inquirer_dashboard')  # 如果不是专家，跳转到提问者仪表盘

    # 从 JSON 文件中加载问题数据
    question_data = load_json_file(r'C:\Users\86131\Desktop\question.json')

    # 随机抽取 15 个问题
    questions = random.sample(question_data, 15)
    correct_answers = [question['answer'] for question in questions]  # 收集正确答案

    if request.method == 'POST':
        answers = request.POST.getlist('answers')  # 获取用户的所有回答

        # 使用EM算法计算信誉度
        updated_credibility = em_algorithm(answers, correct_answers)

        # 更新专家的信誉度
        expert.credibility = updated_credibility
        expert.questionare_done = True  # 修改字段名为 questionare_done
        expert.save()

        # 问卷提交后跳转到专家仪表盘
        return redirect('expert_dashboard')

    return render(request, 'questionare.html', {'questions': questions})
