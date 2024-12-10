from django.shortcuts import render
from django.http import JsonResponse

from knowledge.models import NormalUser, asker, expert
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
            asker.objects.create(owner=normal_user)
        elif user_type == 'expert':
            expert.objects.create(owner=normal_user)

        return render(request, 'knowledge/login.html', {'success': True, 'show_login': True})

    return render(request, 'basic/register.html')

def login(request):
    return  render(request, 'knowledge/login.html')

def expert_dashboard(request):
    return render(request, 'expert_dashboard.html')  # 专家专属页面

def inquirer_dashboard(request):
    return render(request, 'inquirer_dashboard.html')  # 提问者专属页面

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
                    return redirect('/expert_dashboard/')  # 跳转到专家页面
                elif normal_user.user_type == 'inquirer':
                    return redirect('/inquirer_dashboard/')  # 跳转到提问者页面
            else:
                return render(request, 'knowledge/login.html', {'login_failed': True, 'msg': '用户未激活'})
        else:
            return render(request, 'knowledge/login.html', {'login_failed': True, 'msg': '账户名或密码错误，请重新登录'})

    return JsonResponse({'code': 405, 'msg': '方法不允许'}, status=405)

def logout_(request):
	logout(request)
	return redirect('/accounting/login')

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