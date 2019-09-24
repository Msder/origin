from django.shortcuts import render, HttpResponse, redirect
import os
import random
import math
from django.conf import settings
import datetime
from django.http import JsonResponse
from django.contrib import auth
from geetest import GeetestLib
import pymysql

pc_geetest_id = '4f7485df36d9055f9856eac69fcec6e9'
pc_geetest_key = 'f1324e97d7e3380632e6942a25f9364b'


def datetimeToStr(data):
    lstInfo = []
    for i in data:
        lstInfo.append(list(i))
    for i in lstInfo:
        noob = i[3]
        ymd = str(noob).split(' ')[0].split('-')
        dms = str(noob).split(' ')[1].split(':')
        # print(ymd,dms)
        i[3] = ymd
        i.insert(4, dms)
    return lstInfo

def main(request):
    user = request.session.get('user', None)
    print(request.session.get('user'))


    db = pymysql.connect('140.143.73.84', 'test', '123456', 'news', 3306)
    cursor = db.cursor()
    cursor.execute('select id,title,creater,createTime,viewTime from news limit 0,8')
    date = cursor.fetchall()
    cursor.execute('select count(id) from news')
    total = cursor.fetchone()[0]
    db.close()
    lstInfo = datetimeToStr(date)
    print(lstInfo)
    page = math.ceil(total / 8)
    # request.session['user'] = 'noob'
    # del request.session['user']
    # del request.session['power']
    # del request.session['editor']
    if user == None:
        db = pymysql.connect('140.143.73.84', 'test', '123456', 'news', 3306)
        cursor = db.cursor()
        cursor.execute('select id,title,creater,createTime,viewTime from news')
        date = cursor.fetchall()
        db.close()
        return render(request, 'index.html', {'info': 'NoInfo', 'date':lstInfo ,'page': page})
    else:
        db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
        cursor = db.cursor()
        cursor.execute('select editor from detailedInfo where name="{}"'.format(user))
        editor = cursor.fetchall()[0][0]
        db.close()
        return render(request, 'index.html', {'info': user, 'editor':editor, 'date':lstInfo, 'page': page})



def register(request):
    if request.method == "POST":

        ret = {
            'status': None,
            'msg': '',
        }

        username = request.POST.get("username")
        password = request.POST.get("password")

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:
            # 验证码正确

            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=password)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)  # 将登录用户赋值给 request.user
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    else:
        user = request.session.get('user', None)
        if user == None:
            return render(request, "register.html")
        else:
            return redirect('/')


# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def login(request):
    user = request.session.get('user', None)
    if user == None:
        return render(request, 'login.html')
    else:
        return redirect('/')


def uploadRegisterData(request):
    image = request.FILES.get('image')
    # print(image)
    phone = request.POST.get('phone')
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    print(phone, user, pwd, image)
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
    cursor = db.cursor()
    cursor.execute('select * from detailedInfo where name="{}"'.format(user))
    data = cursor.fetchall()
    print(data)
    if len(data) > 0:
        db.close()
        return JsonResponse({'msg': 'NO'})
    else:
        cursor.execute('insert into detailedInfo(name,pwd,power,phone) values("{}","{}","common",{})'.format(user, pwd, phone))
        db.commit()
        db.close()
        request.session['user'] = user
        request.session['power'] = 'common'
        request.session['editor'] = 0
        return JsonResponse({'msg': 'OK'})

def checkUser(request):
    user = request.POST.get('user')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
    cursor = db.cursor()
    cursor.execute('select name from detailedInfo where name="{}"'.format(user))
    data = cursor.fetchall()
    db.close()
    if len(data)>0:
        return JsonResponse({'msg': 'Used'})
    else:
        return JsonResponse({'msg': 'noUsed'})


def logout(request):
    del request.session['user']
    del request.session['power']
    del request.session['editor']
    return JsonResponse({'msg': 'OK'})


def loginData(request):
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
    cursor = db.cursor()
    cursor.execute('select name, pwd from detailedInfo where name="{}" and pwd="{}"'.format(user, pwd))
    data = cursor.fetchall()

    if len(data) > 0:
        cursor.execute('select power,editor from detailedInfo where name="{}" and pwd="{}"'.format(user, pwd))
        power = cursor.fetchall()
        db.close()
        request.session['user'] = user
        request.session['power'] = power[0][0]
        request.session['editor'] = power[0][1]
        return JsonResponse({'msg': 'OK'})
    else:
        db.close()
        return JsonResponse({'msg': 'ERROR'})


def personalCenter(request):
    user = request.session.get('user', None)
    if user == None:
        return redirect('login/')
    else:
        power = request.session.get('power')
        editor = request.session.get('editor')
        return render(request, 'personalCenter.html', {'user': user, 'power': power,'editor': editor})


def listUser(request):
    user = request.session.get('user', None)
    power = request.session.get('power')
    if user == None:
        return redirect('login/')
    elif power != 'admin':
        return redirect('personalCenter/')
    else:
        db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
        cursor = db.cursor()
        cursor.execute('select name, teacher from detailedInfo where power!="admin"')
        data = cursor.fetchall()
        print('非管理员账户一共有：', data)
        db.close()
        return render(request, 'setPower.html', {'user': user, 'power': power, 'listUser': data})


def changeThePower(request):
    user = request.POST.get('user')
    teacherValue = request.POST.get('teacherValue')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'personInfo', 3306)
    cursor = db.cursor()
    cursor.execute('update detailedInfo set teacher={} where name="{}"'.format(teacherValue, user))
    db.commit()
    db.close()
    print('update detailedInfo set teacher={} where name="{}"'.format(teacherValue, user))
    return JsonResponse({'msg': 'OK'})


def setQuestion(request):
    user = request.session.get('user', None)
    power = request.session.get('power')
    if user == None:
        return redirect('login/')
    elif power != 'admin':
        return redirect('personalCenter/')
    else:
        lstMainType = []
        lstType = []
        db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
        cursor = db.cursor()
        for i in range(3):
            cursor.execute('select count(id) from questions where mainType={}'.format(i+1))
            lstMainType.append(str(cursor.fetchone()[0]))
        for i in range(15):
            cursor.execute('select count(qtype) from questions where qtype={}'.format(i+1))
            lstType.append(str(cursor.fetchone()[0]))
        db.close()
        lstMainType = '-'.join(lstMainType)
        lstType = '-'.join(lstType)
        print(lstType)
        return render(request, 'setQuestion.html',  {'user': user, 'power': power, 'mainType':lstMainType, 'type': lstType})


def uploadQuestion(request):
    user = request.session.get('user', None)
    power = request.session.get('power')
    if user == None:
        return redirect('login/')
    elif power != 'admin':
        return redirect('personalCenter/')
    else:
        return render(request, 'uploadQuestion.html',  {'user': user, 'power': power})


def uploadSingle(request):
    titleText = request.POST.get('titleText', None)
    titleImg = request.FILES.get('titleImg', None)
    optionA = request.POST.get('optionA', None)
    optionAImg = request.FILES.get('optionAImg', None)
    optionB = request.POST.get('optionB', None)
    optionBImg = request.FILES.get('optionBImg', None)
    optionC = request.POST.get('optionC', None)
    optionCImg = request.FILES.get('optionCImg', None)
    optionD = request.POST.get('optionD', None)
    optionDImg = request.FILES.get('optionDImg', None)
    answer = request.POST.get('answer')
    type = request.POST.get('type')
    difficulty = request.POST.get('difficulty')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select count(id) from  questions where mainType=1')
    data = cursor.fetchall()[0][0]+1
    print("一共有几条题目？", data)

    singlePath = os.path.join(settings.MEDIA_ROOT,'single')
    if os.path.exists(singlePath) != True:
        os.makedirs(singlePath)
    dirPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data))

    while(os.path.exists(dirPath)):
        data = data + 1
        dirPath = os.path.join(settings.MEDIA_ROOT, 'single',str(data))
    os.makedirs(dirPath)

    if titleImg != None:
        titleImgPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data), titleImg.name)
        with open(titleImgPath, 'wb+') as pic:
            for p in titleImg.chunks():
                pic.write(p)
    else:
        titleImgPath = None

    if optionAImg != None:
        optionAImgPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data), optionAImg.name)
        with open(optionAImgPath, 'wb+') as pic:
            for p in optionAImg.chunks():
                pic.write(p)
    else:
        optionAImgPath = None

    if optionBImg != None:
        optionBImgPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data), optionBImg.name)
        with open(optionBImgPath, 'wb+') as pic:
            for p in optionBImg.chunks():
                pic.write(p)
    else:
        optionBImgPath = None

    if optionCImg != None:
        optionCImgPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data), optionCImg.name)
        with open(optionCImgPath, 'wb+') as pic:
            for p in optionCImg.chunks():
                pic.write(p)
    else:
        optionCImgPath = None

    if optionDImg != None:
        optionDImgPath = os.path.join(settings.MEDIA_ROOT, 'single', str(data), optionDImg.name)
        with open(optionDImgPath, 'wb+') as pic:
            for p in optionDImg.chunks():
                pic.write(p)
    else:
        optionDImgPath = None
    print(titleText,titleImgPath)
    print(optionA,optionAImgPath)
    print(optionB,optionBImgPath)
    print(optionC,optionCImgPath)
    print(optionD,optionDImgPath)
    print(type)
    print(difficulty)
    sql = 'insert into questions(mainType,titleText,titleImg,answer,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,qtype,difficulty) values(1,"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",{},{})'.format(titleText,repr(titleImgPath),answer,optionA,repr(optionAImgPath),optionB,repr(optionBImgPath),optionC,repr(optionCImgPath),optionD,repr(optionDImgPath),type,difficulty)
    print(sql)
    cursor.execute(sql)
    db.commit()
    db.close()
    return JsonResponse({'msg': 'OK'})



def uploadMultiple(request):
    titleText = request.POST.get('titleText', None)
    titleImg = request.FILES.get('titleImg', None)
    optionA = request.POST.get('optionA', None)
    optionAImg = request.FILES.get('optionAImg', None)
    optionB = request.POST.get('optionB', None)
    optionBImg = request.FILES.get('optionBImg', None)
    optionC = request.POST.get('optionC', None)
    optionCImg = request.FILES.get('optionCImg', None)
    optionD = request.POST.get('optionD', None)
    optionDImg = request.FILES.get('optionDImg', None)
    answer = request.POST.get('theAnswer', None)
    type = request.POST.get('type1')
    difficulty = request.POST.get('difficulty1')
    print(titleText,titleImg)
    print(optionA,optionAImg)
    print(optionB,optionBImg)
    print(optionC,optionCImg)
    print(optionD,optionDImg)
    print(type,difficulty)

    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select count(id) from  questions where mainType=2')
    data = cursor.fetchall()[0][0] + 1
    print("一共有几条多选？", data)

    multiplePath = os.path.join(settings.MEDIA_ROOT, 'multiple')
    if os.path.exists(multiplePath) != True:
        os.makedirs(multiplePath)
    dirPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data))

    while (os.path.exists(dirPath)):
        data = data + 1
        dirPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data))
    os.makedirs(dirPath)

    if titleImg != None:
        titleImgPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data), titleImg.name)
        with open(titleImgPath, 'wb+') as pic:
            for p in titleImg.chunks():
                pic.write(p)
    else:
        titleImgPath = None

    if optionAImg != None:
        optionAImgPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data), optionAImg.name)
        with open(optionAImgPath, 'wb+') as pic:
            for p in optionAImg.chunks():
                pic.write(p)
    else:
        optionAImgPath = None

    if optionBImg != None:
        optionBImgPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data), optionBImg.name)
        with open(optionBImgPath, 'wb+') as pic:
            for p in optionBImg.chunks():
                pic.write(p)
    else:
        optionBImgPath = None

    if optionCImg != None:
        optionCImgPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data), optionCImg.name)
        with open(optionCImgPath, 'wb+') as pic:
            for p in optionCImg.chunks():
                pic.write(p)
    else:
        optionCImgPath = None

    if optionDImg != None:
        optionDImgPath = os.path.join(settings.MEDIA_ROOT, 'multiple', str(data), optionDImg.name)
        with open(optionDImgPath, 'wb+') as pic:
            for p in optionDImg.chunks():
                pic.write(p)
    else:
        optionDImgPath = None
    # print(titleText, titleImgPath)
    # print(optionA, optionAImgPath)
    # print(optionB, optionBImgPath)
    # print(optionC, optionCImgPath)
    # print(optionD, optionDImgPath)
    # print(type)
    # print(difficulty)
    sql = 'insert into questions(mainType,titleText,titleImg,answer,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,qtype,difficulty) values(2,"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",{},{})'.format(
        titleText, repr(titleImgPath), answer, optionA, repr(optionAImgPath), optionB, repr(optionBImgPath), optionC,
        repr(optionCImgPath), optionD, repr(optionDImgPath), type, difficulty)
    print(sql)
    cursor.execute(sql)
    db.commit()
    db.close()
    return JsonResponse({'msg': 'OK'})


def uploadJudge(request):
    titleText = request.POST.get('titleText', None)
    titleImg = request.FILES.get('titleImg', None)
    answer = request.POST.get('answer2', None)
    type = request.POST.get('type2')
    difficulty = request.POST.get('difficulty2')
    print(titleText,titleImg)
    print(answer,type,difficulty)

    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select count(id) from  questions where mainType=3')
    data = cursor.fetchall()[0][0] + 1
    print("一共有几条判断？", data)

    judgePath = os.path.join(settings.MEDIA_ROOT, 'judge')
    if os.path.exists(judgePath) != True:
        os.makedirs(judgePath)
    dirPath = os.path.join(settings.MEDIA_ROOT, 'judge', str(data))

    while (os.path.exists(dirPath)):
        data = data + 1
        dirPath = os.path.join(settings.MEDIA_ROOT, 'judge', str(data))
    os.makedirs(dirPath)

    if titleImg != None:
        titleImgPath = os.path.join(settings.MEDIA_ROOT, 'judge', str(data), titleImg.name)
        with open(titleImgPath, 'wb+') as pic:
            for p in titleImg.chunks():
                pic.write(p)
    else:
        titleImgPath = None

    sql = 'insert into questions(mainType,titleText,titleImg,answer,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,qtype,difficulty) values(3,"{}","{}","{}","None","None","None","None","None","None","None","None",{},{})'.format(
        titleText, repr(titleImgPath), answer, type, difficulty)
    print(sql)
    cursor.execute(sql)
    db.commit()
    db.close()
    return JsonResponse({'msg': 'OK'})

#编辑新闻的页面
def editInfo(request):
    user = request.session.get('user',None)
    editor = request.session.get('editor')
    if user == None:
        return redirect('login/')
    return render(request, 'editInfo.html', {'user': user, 'editor': editor})

def uploadInfo(request):
    user = request.session.get('user')
    title = request.POST.get('title')
    content = request.POST.get('content')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'news', 3306)
    cursor = db.cursor()
    cursor.execute('insert into news(title,content,creater,viewTime) values("{}","{}","{}",0);'.format(title,content,user))
    db.commit()
    db.close()
    return JsonResponse({'msg': 'OK'})


def infoPage(request,id):
    user = request.session.get('user')
    editor = request.session.get('editor')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'news', 3306)
    cursor = db.cursor()
    cursor.execute('select title,content,creater,createTime,viewTime from news where id={}'.format(id))
    data = cursor.fetchall()
    db.close()
    print(data)
    lstInfo = datetimeToStr(data)
    print(lstInfo)
    lstInfo[0][1] = repr(lstInfo[0][1]).replace(r'\n','<br>').replace(' ','&nbsp')[1:-1]
    # print(repr(data[1]).replace(r'\n','<br>').replace(' ','&nbsp')[1:-1])
    return render(request, 'infoPage.html',{'user': user, 'editor': editor, 'data':lstInfo})


def testPage(request):
    lstInfo = []
    user = request.session.get('user')
    editor = request.session.get('editor')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select mainType,titleText,titleImg,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg from questions')
    data = cursor.fetchall()
    for i in data:
        lstInfo.append(list(i))

    for i in lstInfo:
        index = 2
        if i[0] != 3:
            while(index<=10):
                if i[index] != 'None':
                    i[index] = i[index][1:-1]
                    # print(i[index])
                    pos = i[index].find('static')
                    # print('首次出现位置为：',pos)
                    i[index] = i[index][pos:]
                    # print(i[index])
                    i[index] = '/' + i[index]
                index += 2
    db.close()
    print(lstInfo)
    return render(request, 'testPage.html', {'user': user, 'editor': editor, 'questions':lstInfo})


def changePage(request,page):
    print(type(page))
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'news', 3306)
    cursor = db.cursor()
    cursor.execute('select id,title,creater,createTime,viewTime from news limit {},8'.format(8*(page-1)))
    date = cursor.fetchall()
    print(date)
    db.close()
    return JsonResponse({'msg':'OK','news': date})


def chooseRandom(begin,end,num):
    randomLst = []
    while(len(randomLst)<num):
        a = random.randint(begin,end)
        if a not in randomLst:
            randomLst.append(a)
    return randomLst


def uploadPageSetting(request):
    questionType = request.POST.get('pageSettins')
    lst = questionType.split('-')
    print(questionType,type(questionType))
    for i in range(0,len(lst)):
        lst[i] = int(lst[i])
    print(lst)
    singleLst = []
    multiplaLst = []
    jungleLst = []
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    for i in lst:
        cursor.execute('select mainType,titleText,titleImg,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,difficulty,id,answer from questions where mainType=1 and qtype={}'.format(i))
        singleDate = cursor.fetchall()
        cursor.execute('select mainType,titleText,titleImg,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,difficulty,id,answer from questions where mainType=2 and qtype={}'.format(i))
        multiplaDate = cursor.fetchall()
        cursor.execute('select mainType,titleText,titleImg,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg,difficulty,id,answer from questions where mainType=3 and qtype={}'.format(i))
        jungleDate = cursor.fetchall()
        for j in singleDate:
            singleLst.append(list(j))
        for j in multiplaDate:
            multiplaLst.append(list(j))
        for j in jungleDate:
            jungleLst.append(list(j))
    print(singleLst)
    print('符合的单选题有：',len(singleLst))
    print(multiplaLst)
    print('符合的多选题有：', len(multiplaLst))
    print(jungleLst)
    print('符合的判断有：', len(jungleLst))


    #一个抽单选题思路，难度1抽5个，难度2抽10个，难度3抽10个，难度4抽5个，他们如果有不够的话，从剩下的题目中随机抽补上。
    if(len(singleLst)<30 or len(multiplaLst)<5 or len(jungleLst)<10):
        db.close()
        return JsonResponse({'msg': 'ERROR', 'single':len(singleLst), 'multipla':len(multiplaLst), 'jungle':len(jungleLst)})
    else:
        totalSingle = []
        needSingleLst = []
        diff1SingleLst = [i for i in singleLst if i[11]==1]
        diff2SingleLst = [i for i in singleLst if i[11]==2]
        diff3SingleLst = [i for i in singleLst if i[11]==3]
        diff4SingleLst = [i for i in singleLst if i[11]==4]
        print(len(diff1SingleLst),diff1SingleLst)
        print(len(diff2SingleLst),diff2SingleLst)
        print(len(diff3SingleLst),diff3SingleLst)
        print(len(diff4SingleLst),diff4SingleLst)
        if(len(diff1SingleLst) <= 5):
            totalSingle.extend(diff1SingleLst)
        else:
            randomSingleList = chooseRandom(0, len(diff1SingleLst) - 1, 5)
            needSingleLst.extend(diff1SingleLst)
            for i in randomSingleList:
                totalSingle.append(diff1SingleLst[i])
                needSingleLst.remove(diff1SingleLst[i])

        if(len(diff2SingleLst) <= 10):
            totalSingle.extend(diff2SingleLst)
        else:
            randomSingleList = chooseRandom(0, len(diff2SingleLst) - 1, 10)
            needSingleLst.extend(diff2SingleLst)
            for i in randomSingleList:
                totalSingle.append(diff2SingleLst[i])
                needSingleLst.remove(diff2SingleLst[i])

        if(len(diff3SingleLst) <= 10):
            totalSingle.extend(diff3SingleLst)
        else:
            randomSingleList = chooseRandom(0, len(diff3SingleLst) - 1, 10)
            needSingleLst.extend(diff3SingleLst)
            for i in randomSingleList:
                totalSingle.append(diff3SingleLst[i])
                needSingleLst.remove(diff3SingleLst[i])

        if(len(diff4SingleLst) <= 5):
            totalSingle.extend(diff4SingleLst)
        else:
            randomSingleList = chooseRandom(0, len(diff4SingleLst) - 1, 5)
            needSingleLst.extend(diff4SingleLst)
            for i in randomSingleList:
                totalSingle.append(diff4SingleLst[i])
                needSingleLst.remove(diff4SingleLst[i])

        while(len(totalSingle)<30):
            needNum = 30 - len(totalSingle)
            randomSingleList = chooseRandom(0, len(needSingleLst) - 1, needNum)
            for i in randomSingleList:
                totalSingle.append(needSingleLst[i])


        #此处为多选
        totalMultipla = []
        needMultiplaLst = []
        diff1MultiplaLst = [i for i in multiplaLst if i[11] == 1]
        diff2MultiplaLst = [i for i in multiplaLst if i[11] == 2]
        diff3MultiplaLst = [i for i in multiplaLst if i[11] == 3]
        diff4MultiplaLst = [i for i in multiplaLst if i[11] == 4]
        print("难度1：",len(diff1MultiplaLst), diff1MultiplaLst)
        print(len(diff2MultiplaLst), diff2MultiplaLst)
        print(len(diff3MultiplaLst), diff3MultiplaLst)
        print(len(diff4MultiplaLst), diff4MultiplaLst)
        if (len(diff1MultiplaLst) <= 2):
            totalMultipla.extend(diff1MultiplaLst)
        else:
            randomMultiplaList = chooseRandom(0, len(diff1MultiplaLst) - 1, 2)
            needMultiplaLst.extend(diff1MultiplaLst)
            for i in randomMultiplaList:
                totalMultipla.append(diff1MultiplaLst[i])
                needMultiplaLst.remove(diff1MultiplaLst[i])

        if (len(diff2MultiplaLst) <= 1):
            totalMultipla.extend(diff2MultiplaLst)
        else:
            randomMultiplaList = chooseRandom(0, len(diff2MultiplaLst) - 1, 1)
            needMultiplaLst.extend(diff2MultiplaLst)
            for i in randomMultiplaList:
                totalMultipla.append(diff2MultiplaLst[i])
                needMultiplaLst.remove(diff2MultiplaLst[i])

        if (len(diff3MultiplaLst) <= 1):
            totalMultipla.extend(diff3MultiplaLst)
        else:
            randomMultiplaList = chooseRandom(0, len(diff3MultiplaLst) - 1, 1)
            needMultiplaLst.extend(diff3MultiplaLst)
            for i in randomMultiplaList:
                totalMultipla.append(diff3MultiplaLst[i])
                needMultiplaLst.remove(diff3MultiplaLst[i])

        if (len(diff4MultiplaLst) <= 1):
            totalMultipla.extend(diff4MultiplaLst)
        else:
            randomMultiplaList = chooseRandom(0, len(diff4MultiplaLst) - 1, 1)
            needMultiplaLst.extend(diff4MultiplaLst)
            for i in randomMultiplaList:
                totalMultipla.append(diff4MultiplaLst[i])
                needMultiplaLst.remove(diff4MultiplaLst[i])

        while (len(totalMultipla) < 5):
            needNum = 5 - len(totalMultipla)
            randomMultipla = chooseRandom(0, len(needMultiplaLst) - 1, needNum)
            for i in randomMultiplaList:
                totalMultipla.append(needMultiplaLst[i])



        #以下是判断
        totalJungle = []
        needJungleLst = []
        diff1JungleLst = [i for i in jungleLst if i[11] == 1]
        diff2JungleLst = [i for i in jungleLst if i[11] == 2]
        diff3JungleLst = [i for i in jungleLst if i[11] == 3]
        diff4JungleLst = [i for i in jungleLst if i[11] == 4]
        print("难度1：", len(diff1JungleLst), diff1JungleLst)
        print(len(diff2JungleLst), diff2JungleLst)
        print(len(diff3JungleLst), diff3JungleLst)
        print(len(diff4JungleLst), diff4JungleLst)
        if (len(diff1JungleLst) <= 3):
            totalJungle.extend(diff1JungleLst)
        else:
            randomJungleList = chooseRandom(0, len(diff1JungleLst) - 1, 3)
            needJungleLst.extend(diff1JungleLst)
            for i in randomJungleList:
                totalJungle.append(diff1JungleLst[i])
                needJungleLst.remove(diff1JungleLst[i])

        if (len(diff2JungleLst) <= 2):
            totalJungle.extend(diff2JungleLst)
        else:
            randomJungleList = chooseRandom(0, len(diff2JungleLst) - 1, 2)
            needJungleLst.extend(diff2JungleLst)
            for i in randomJungleList:
                totalJungle.append(diff2JungleLst[i])
                needJungleLst.remove(diff2JungleLst[i])

        if (len(diff3JungleLst) <= 2):
            totalJungle.extend(diff3JungleLst)
        else:
            randomJungleList = chooseRandom(0, len(diff3JungleLst) - 1, 2)
            needJungleLst.extend(diff3JungleLst)
            for i in randomJungleList:
                totalJungle.append(diff3JungleLst[i])
                needJungleLst.remove(diff3JungleLst[i])

        if (len(diff4JungleLst) <= 2):
            totalJungle.extend(diff4JungleLst)
        else:
            randomJungleList = chooseRandom(0, len(diff4JungleLst) - 1, 2)
            needJungleLst.extend(diff4JungleLst)
            for i in randomJungleList:
                totalJungle.append(diff4JungleLst[i])
                needJungleLst.remove(diff4JungleLst[i])

        while (len(totalJungle) < 10):
            needNum = 10 - len(totalJungle)
            randomJungleList = chooseRandom(0, len(needJungleLst) - 1, needNum)
            for i in randomJungleList:
                totalJungle.append(needJungleLst[i])



        for i in totalSingle:
            print(i)
        print(len(totalSingle))

        for i in totalMultipla:
            print(i)
        print(len(totalMultipla))

        for i in totalJungle:
            print(i)
        print(len(totalJungle))

        totalQuestion = []
        totalQuestion.extend(totalSingle)
        totalQuestion.extend(totalMultipla)
        totalQuestion.extend(totalJungle)

        totalIDLst = []
        for i in totalQuestion:
            totalIDLst.append(str(i[12]))
        totalIDStr = '-'.join(totalIDLst)
        print(totalIDStr)

        totalAnswerLst = []
        for i in totalQuestion:
            totalAnswerLst.append(str(i[13]))
        totalAnswerStr = '-'.join(totalAnswerLst)
        print(totalAnswerStr)
        cursor.execute('insert into page(qtype,questions,answer) values("{}","{}","{}")'.format(questionType,totalIDStr,totalAnswerStr))
        db.commit()
        cursor.execute('select count(id) from page')
        pageNum = int(cursor.fetchone()[0])
        cursor.execute('alter table score add column page{} int(3) default 999;'.format(pageNum))
        db.commit()
        cursor.execute('alter table worryQuestion add column page{} varchar(200);'.format(pageNum))
        db.commit()
        cursor.execute('alter table worryQuestion add column page{}Answer varchar(200);'.format(pageNum))
        db.commit()
        cursor.execute('alter table worryQuestion add column page{}Percent varchar(150);'.format(pageNum))
        db.commit()
        db.close()
        return JsonResponse({'msg': 'OK'})


def choosePage(request):
    user = request.session.get('user',None)
    power = request.session.get('power',None)
    editor = request.session.get('editor',None)
    if user == None:
        return render(request,'index.html')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select qtype from page')
    date = cursor.fetchall()
    lst =['机器人形象','机器人定义','机器人分类','机器人结构','稳定性','斜面','摩擦力','力','功','单摆','杠杆','轮轴','滑轮组','传动链','风扇']
    lst1 = []
    for i in date:
        kk = i[0].split('-')
        kk1 = [int(j) for j in kk]
        kk2 = [lst[j-1] for j in kk1]
        lst1.append(kk2)
    print(lst1)


    cursor.execute('select * from worryQuestion where name="{}"'.format(user))
    reallyPercent = []
    date = cursor.fetchone()
    print(date)

    #得查询到有多少个卷子了
    cursor.execute('desc worryQuestion')
    pageNum = len(cursor.fetchall())
    pageNum = int((pageNum - 4)/3 + 1)
    print(pageNum)
    if date == None:
        reallyPercent = [None for i in range(0,pageNum)]
    else:
        for i in range(0,pageNum):
            reallyPercent.append(date[3*i+3])
        print(reallyPercent)
        for i in range(0,len(reallyPercent)):
            if reallyPercent[i] == None:
                reallyPercent[i] = 'KK'
            else:
                reallyPercent[i] = reallyPercent[i].split('N')

                for j in range(0,len(reallyPercent[i])):
                    reallyPercent[i][j] = reallyPercent[i][j].split('-')
                    if j == 0:
                        reallyPercent[i][j][0] = '单选'
                    elif j == 1:
                        reallyPercent[i][j][0] = '多选'
                    elif j == 2:
                        reallyPercent[i][j][0] = '判断'
                    else:
                        reallyPercent[i][j][0] = lst[int(reallyPercent[i][j][0])-1]
                    reallyPercent[i][j][1] = reallyPercent[i][j][1].split('.')

    db.close()
    print(reallyPercent)
    return render(request,'choosePage.html',{'user': user, 'power': power,'editor': editor,'pageInfo':lst1, 'questionPercent': reallyPercent})

def needTest(request,id):
    user = request.session.get('user')
    editor = request.session.get('editor')
    print(id)
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select questions from page where id={}'.format(id))
    questionStr = cursor.fetchone()[0]
    questionLst = questionStr.split('-')
    questionLst = [int(i) for i in questionLst]
    questionLst1 = []
    lstInfo = []
    for i in questionLst:
        cursor.execute('select mainType,titleText,titleImg,optiona,optionaImg,optionb,optionbImg,optionc,optioncImg,optiond,optiondImg from questions where id={}'.format(i))
        questionLst1.append(cursor.fetchone())

    for i in questionLst1:
        lstInfo.append(list(i))

    for i in lstInfo:
        index = 2
        if i[0] != 3:
            while(index<=10):
                if i[index] != 'None':
                    i[index] = i[index][1:-1]
                    # print(i[index])
                    pos = i[index].find('static')
                    # print('首次出现位置为：',pos)
                    i[index] = i[index][pos:]
                    # print(i[index])
                    i[index] = '/' + i[index]
                index += 2
    print(len(questionLst1),questionLst1)
    pageNum = 'page' + str(id)
    cursor.execute('select {} from score where name="{}"'.format(pageNum,user))
    score = cursor.fetchone()
    if score == None:
        score = 999
    else:
        score = score[0]

    cursor.execute('select {} from worryQuestion where name="{}"'.format(pageNum,user))
    worryExist = cursor.fetchone()
    if worryExist == None:
        worryExist = 'A'
    else:
        worryExist = worryExist[0]
    print(worryExist)
    cursor.execute('select {} from worryQuestion where name="{}"'.format(pageNum+'Answer', user))
    correctAnswer = cursor.fetchone()
    if correctAnswer == None:
        correctAnswer = 'A'
    else:
        correctAnswer = correctAnswer[0]
    db.close()

    return render(request,'testPage.html',{'user': user, 'editor': editor, 'questions':lstInfo, 'score': score , 'worry':worryExist, 'answer': correctAnswer})


def uploadAnswer(request):
    user = request.session.get('user',None)
    score = 100
    answerStr = request.POST.get('answer')
    answerLst = answerStr.split('-')
    print('所有的答案是：',answerLst)
    id = request.POST.get('pageID')
    db = pymysql.connect('140.143.73.84', 'test', '123456', 'questions', 3306)
    cursor = db.cursor()
    cursor.execute('select answer from page where id={}'.format(id))
    theAnswer = cursor.fetchone()[0]
    theAnswerLst = theAnswer.split('-')

    totalQuestionLst = []

    cursor.execute('select questions from page where id={}'.format(id))
    allQuestionsID = cursor.fetchone()[0]

    cursor.execute('select qtype from page where id={}'.format(id))
    allQType = cursor.fetchone()[0]
    allQTypeLst = allQType.split('-')
    allQTypeLst = [int(i) for i in allQTypeLst]

    allQuestionsLst = allQuestionsID.split('-')
    allQuestionsLst = [int(i) for i in allQuestionsLst]
    questionNumLst = [0 for i in range(0,len(allQTypeLst))]
    worryQuestionLst = [0 for i in range(0,len(allQTypeLst))]
    # print(len(answerLst),answerLst)
    # print(len(theAnswerLst),theAnswerLst)
    worryAnswerLst = []
    for i in range(0,45):
        cursor.execute('select qtype from questions where id={}'.format(allQuestionsLst[i]))
        qtype = cursor.fetchone()[0]
        if answerLst[i] != theAnswerLst[i]:
            if(i >= 0 and i <= 29):
                score -= 2
                worryAnswerLst.append([i, theAnswerLst[i],1, qtype])
            if(i >= 30 and i <= 34):
                if answerLst[i] in theAnswerLst[i]:
                    score -=2
                else:
                    score -=4
                worryAnswerLst.append([i, theAnswerLst[i], 2, qtype])
            if(i >= 35 and i<=44):
                score -= 2
                worryAnswerLst.append([i, theAnswerLst[i], 3, qtype])

        for j in range(0,len(allQTypeLst)):
            if allQTypeLst[j] == qtype:
                questionNumLst[j]+=1
    print("成绩为：",score,worryAnswerLst)

    singleWorry = 0
    multiplaWorry = 0
    jungleWorry = 0

    for i in range(0,len(worryAnswerLst)):
        for j in range(0, len(allQTypeLst)):
            if worryAnswerLst[i][3] == allQTypeLst[j]:
                worryQuestionLst[j] += 1;
        if worryAnswerLst[i][2] == 1:
            singleWorry += 1
        if worryAnswerLst[i][2] == 2:
            multiplaWorry += 1
        if worryAnswerLst[i][2] == 3:
            jungleWorry += 1

    print(allQTypeLst)
    print(questionNumLst)
    print(worryQuestionLst)
    totalQuestionLst.append(['A',[str(singleWorry),str(30)]])
    totalQuestionLst.append(['B',[str(multiplaWorry),str(5)]])
    totalQuestionLst.append(['C',[str(jungleWorry),str(10)]])
    for i in range(0, len(questionNumLst)):
        if questionNumLst[i] != 0:
            totalQuestionLst.append([str(allQTypeLst[i]), [str(worryQuestionLst[i]),str(questionNumLst[i])]])

    print(totalQuestionLst)

    for i in range(0,len(totalQuestionLst)):
        totalQuestionLst[i][1] = '.'.join(totalQuestionLst[i][1])
        totalQuestionLst[i] = '-'.join(totalQuestionLst[i])

    totalQuestionStr = 'N'.join(totalQuestionLst)

    print(totalQuestionStr)

    pageNum = 'page' + str(id)
    pageAnswer = pageNum + 'Answer'
    worryAnswerID = [str(i[0]) for i in worryAnswerLst]
    worryAnswerIDStr = '-'.join(worryAnswerID)
    worryAnswer = [str(i[1]) for i in worryAnswerLst]
    worryAnswerStr = '-'.join(worryAnswer)
    cursor.execute('select * from worryQuestion where name="{}"'.format(user))
    alreadyHaveWorry = len(cursor.fetchall())
    print(alreadyHaveWorry,worryAnswerID,worryAnswerIDStr)
    if alreadyHaveWorry == 0:
        cursor.execute('insert into worryQuestion(name,{},{}) values("{}","{}","{}")'.format(pageNum, pageAnswer, user, worryAnswerIDStr, worryAnswerStr))
        db.commit()
    else:
        cursor.execute('update worryQuestion set {}="{}" where name="{}"'.format(pageNum, worryAnswerIDStr, user))
        db.commit()
        cursor.execute('update worryQuestion set {}="{}" where name="{}"'.format(pageNum+'Answer', worryAnswerStr, user))
        db.commit()


    print(pageNum,user,score)
    cursor.execute('select * from score where name="{}"'.format(user))
    alreadyHave = len(cursor.fetchall())
    if(alreadyHave == 0):
        cursor.execute('insert into score(name,{}) values("{}",{})'.format(pageNum,user,score))
    else:
        cursor.execute('update score set {}={} where name="{}"'.format(pageNum,score,user))
    db.commit()
    cursor.execute('update worryQuestion set {}="{}" where name="{}"'.format(pageNum+'Percent', totalQuestionStr, user))
    db.commit()
    db.close()
    return JsonResponse({'msg':'OK', 'worry': worryAnswerLst, 'score':score})