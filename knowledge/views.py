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
















from django.shortcuts import render, redirect
import json
import random


def em_algorithm(questions, user_answers, max_iter=10, tolerance=1e-4):

    # 初始化可信度
    theta = 0.5  # 初始可信度，假设为0.5

    def e_step(questions, user_answers, theta):

        probabilities = []
        for i, question in enumerate(questions):
            correct_answer = question['answer']
            user_answer = user_answers[i]

            # 假设用户答对问题的概率是 theta
            # 如果用户的答案与正确答案匹配，则认为用户答对问题
            correct = 1 if user_answer == correct_answer else 0
            probabilities.append(correct * theta + (1 - correct) * (1 - theta))

        return probabilities

    def m_step(probabilities, user_answers):

        correct_count = sum(
            probabilities[i] * (1 if user_answers[i] == questions[i]['answer'] else 0) for i in range(len(questions)))
        theta = correct_count / len(questions)
        return theta

    # 迭代执行E步和M步
    for iteration in range(max_iter):
        probabilities = e_step(questions, user_answers, theta)
        new_theta = m_step(probabilities, user_answers)

        # 检查收敛
        if abs(new_theta - theta) < tolerance:
            break

        theta = new_theta

    return theta


def questionare(request):
    # 读取问题 JSON 文件
    with open(r"C:\Users\86131\Desktop\question.json", "r", encoding="utf-8") as file:
        questions_data = json.load(file)

    # 随机抽取 15 个问题
    selected_questions = random.sample(questions_data, 15)

    if request.method == 'POST':
        # 获取用户提交的答案
        user_answers = request.POST.getlist('answers')  # 假设用户答案的名称是 'answers'

        # 使用 EM 算法计算用户的可信度
        credibility = em_algorithm(selected_questions, user_answers)

        # 保存可信度到 Expert 模型中
        if request.user.is_authenticated:
            normal_user = request.user
            ownername = NormalUser.objects.get(name=normal_user)
            try:
                expert = Expert.objects.get(owner=ownername)
                expert.credibility = credibility  # 更新可信度
                expert.save()
            except Expert.DoesNotExist:
                pass  # 如果专家记录不存在，则忽略


        return redirect('expert_dashboard')

    # 渲染问题页面
    return render(request, 'knowledge/questionare.html', {'questions': selected_questions})
