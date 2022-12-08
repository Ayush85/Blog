from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Blog import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token
from django.core.mail import EmailMessage
from .form import BlogModel, BlogForm

# Create your views here.

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username = username, password = pass1)
        if user is not None:
            login(request, user)
            fname = user.first_name
            return redirect('/',  name=fname)

        else:
            messages.error(request,"Bad credintials!")
            return redirect('signin')


    return render(request, "signin.html")



def logout_view(request):
    logout(request)
    return redirect('/')

def home(request):
    context = {'blogs': BlogModel.objects.all().order_by('-id')}
    return render(request, 'home.html', context)

def blog_detail(request, slug):
    context = {}
    try:
        blog_obj = BlogModel.objects.filter(slug=slug).first()
        context['blog_obj'] = blog_obj
    except Exception as e:
        print(e)
    return render(request, 'blog_detail.html', context)


def see_blog(request):
    context = {}

    try:

        blog_objs = BlogModel.objects.filter(user=request.user).order_by('-id')
        context['blog_objs'] = blog_objs
    except Exception as e:
        print(e)

    print(context)
    return render(request, 'see_blog.html', context)


def add_blog(request):
    context = {'form': BlogForm}
    try:
        if request.method == 'POST':
            form = BlogForm(request.POST)
            print(request.FILES)
            image = request.FILES.get('image', '')
            title = request.POST.get('title')
            user = request.user

            if form.is_valid():
                print('Valid')
                content = form.cleaned_data['content']

            blog_obj = BlogModel.objects.create(
                user=user, title=title,
                content=content, image=image
            )
            print(blog_obj)
            return redirect('/add-blog/')
    except Exception as e:
        print(e)

    return render(request, 'add_blog.html', context)


def blog_update(request, slug):
    context = {}
    try:

        blog_obj = BlogModel.objects.get(slug=slug)

        if blog_obj.user != request.user:
            return redirect('/')

        initial_dict = {'content': blog_obj.content}
        form = BlogForm(initial=initial_dict)
        if request.method == 'POST':
            form = BlogForm(request.POST)
            print(request.FILES)
            image = request.FILES['image']
            title = request.POST.get('title')
            user = request.user

            if form.is_valid():
                content = form.cleaned_data['content']


            blog_obj.delete()
            blog_obj = BlogModel.objects.create(
                user=user, title=title,
                content=content, image=image
            )

        context['blog_obj'] = blog_obj
        context['form'] = form
    except Exception as e:
        print(e)

    return render(request, 'update_blog.html', context)


def blog_delete(request, id):
    try:
        blog_obj = BlogModel.objects.get(id=id)

        if blog_obj.user == request.user:
            blog_obj.delete()

    except Exception as e:
        print(e)

    return redirect('/see-blog/')

def signup(request):
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist. Please try another username")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.error(request,"your email address is already register")
            return redirect('signup')

        if len(username)>10:
            messages.error(request,"User name must be less than 10 characters")

        if pass1 != pass2:
            messages.error(request,"Password didn't match")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request,"Username must be Alpha-Numeric!")
            return redirect('signup')

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request,"Your account has been successfully created. We have sent you a verification email. Please verify your email in order to activate account")

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Verify your email @ Blogs!"
        message = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        # email.fail_silently = True
        email.send()
        return redirect('signin')

    return render(request, "signup.html")

def ForgetPassword(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')

            if not User.objects.filter(username=username).first():
                messages.error(request, 'No user found with this username.')
                return redirect('/forget-password/')
            myuser = User.objects.get(username=username)

            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Verify your email @ Blogs!"
            message = render_to_string('email_reset.html',{
                'name':myuser.first_name,
                'domain':current_site.domain,
                'username':myuser.username,
                'token': generate_token.make_token(myuser),
            })
            email = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [myuser.email],
            )
            # email.fail_silently = True
            email.send()




    except Exception as e:
        print(e)
    return render(request , 'forget-password.html')

def ChangePassword(request, username, token):
    
    
    myuser = User.objects.get(username=username)

    try:

        if request.method == 'POST':
            raw_password = request.POST['new_password']
            confirm_password = request.POST['reconfirm_password']
            myuser.set_password(raw_password)
            myuser.save()


            if  raw_password != confirm_password:
                messages.success(request, 'both should  be equal.')
                return redirect(f'/change-password/{token}/')
            
            return redirect('signin')

    except Exception as e:
        print(e)
    return render(request , 'change-password.html')


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        print(myuser.first_name)
        return redirect('home')


