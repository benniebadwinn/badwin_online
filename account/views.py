from django.shortcuts import render, redirect
from account.forms import SignUpForm
from django.contrib.auth.models import User
from django.contrib import messages
import random
from .models import UserOTP
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.urls import reverse_lazy
from django.urls import reverse
from .forms import UserPublicDetailsForm
from django.http import  HttpResponse, HttpResponseRedirect
# from main.models import Post

from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignupForm, LoginUserForm, PasswordChangingForm, EditUserProfileForm, UserPublicDetailsForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
# from main.models import Blog, BlogComment
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfuile
from main.models import Blog, BlogComment
from .models import subscriptions
from django.shortcuts import render, redirect,get_object_or_404
from moontag_app.models import ProductAttribute


success_url = reverse_lazy("django_registration_complete")

def panel(request):
	return render(request, "user/admin_page.html")



def signup(request):
	if request.method == 'POST':
		get_otp = request.POST.get('otp') #213243 #None

		if get_otp:
			get_user = request.POST.get('usr')
			usr = User.objects.get(username=get_user)
			if int(get_otp) == UserOTP.objects.filter(user = usr).last().otp:
				usr.is_active = True
				usr.save()
				messages.success(request, f'Account has been Created For {usr.first_name}')
				return redirect(reverse('account:login'))
				# return redirect('account:login')
			else:
				messages.warning(request, f'You Entered a Wrong OTP')
				return render(request, 'user/login.html', {'otp': True, 'usr': usr})
        # if User.objects.filter(username=username):
        #     messages.error(request, "Username already exist! Try other username")
        #     return redirect('user/signup.html')
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			name = form.cleaned_data.get('name').split(' ')
       
	
			usr = User.objects.get(username=username)
			usr.email = username
			usr.first_name = name[0]
			if len(name) > 1:
				usr.last_name = name[1]
			usr.is_active = False
			usr.save()
			usr_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user = usr, otp = usr_otp)

			mess = f"Hello {usr.first_name},\nYour OTP is {usr_otp}\nThanks!"

			send_mail(
				"Welcome to Badwin - Verify Your Email",
				mess,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)

			return render(request, 'user/signup.html', {'otp': True, 'usr': usr})

		
	else:
		form = SignUpForm()


	return render(request, 'user/signup.html', {'form':form})


def resend_otp(request):
	if request.method == "GET":
		get_usr = request.GET['usr']
		if User.objects.filter(username = get_usr).exists() and not User.objects.get(username = get_usr).is_active:
			usr = User.objects.get(username=get_usr)
			usr_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user = usr, otp = usr_otp)
			mess = f"Hello {usr.first_name},\nYour OTP is {usr_otp}\nThanks!"

			send_mail(
				"Welcome to Badwin - Verify Your Email",
				mess,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)
			return HttpResponse("Resend")

	return HttpResponse("Can't Send ")


def login_view(request):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		get_otp = request.POST.get('otp') #213243 #None

		if get_otp:
			get_usr = request.POST.get('usr')
			usr = User.objects.get(username=get_usr)
			if int(get_otp) == UserOTP.objects.filter(user = usr).last().otp:
				usr.is_active = True
				usr.save()
				login(request, usr)
				return redirect('home')
			else:
				messages.warning(request, f'You Entered a Wrong OTP')
				return render(request, 'user/login.html', {'otp': True, 'usr': usr})


		usrname = request.POST['username']
		passwd = request.POST['password']

		user = authenticate(request, username = usrname, password = passwd) #None
		if user is not None:
			login(request, user)
			return redirect('/')
		elif not User.objects.filter(username = usrname).exists():
			messages.warning(request, f'Please enter a correct username and password. Note that both fields may be case-sensitive.')
			return redirect('account:login')
		elif not User.objects.get(username=usrname).is_active:
			usr = User.objects.get(username=usrname)
			usr_otp = random.randint(100000, 999999)
			UserOTP.objects.create(user = usr, otp = usr_otp)
			mess = f"Hello {usr.first_name},\nYour OTP is {usr_otp}\nThanks for shopping with us !"

			send_mail(
				"Welcome to Badwin - Verify Your Email",
				mess,
				settings.EMAIL_HOST_USER,
				[usr.email],
				fail_silently = False
				)
			return render(request, 'user/login.html', {'otp': True, 'usr': usr})
		else:
			messages.warning(request, f'Please enter a correct username and password.Note that both fields may be case-sensitive')
			return redirect('account:login')

	form = AuthenticationForm()
	return render(request, 'user/login.html', {'form': form})
    



# @login_required(login_url="/accounts/login/")
def create_profile(request):
    current_user = request.user
    title = "Create Profile"
    if request.method == 'POST':
        form = UserPublicDetailsForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = current_user
            profile.save()
        return HttpResponseRedirect('/')

    else:
        form = UserPublicDetailsForm()
    return render(request, 'user/create_profile.html', {"form": form, "title": title})
            



class profile(LoginRequiredMixin, generic.View):
    model = Blog
    login_url = 'account:login'
    template_name = "authors/profile.html"

    def get(self, request, user_name):
        user_related_data = Blog.objects.filter(author__username=user_name)[:6]
        user_profile_data = UserProfuile.objects.get(user=request.user.id)
        context = {
            "user_related_data": user_related_data,
            'user_profile_data': user_profile_data
        }
        return render(request, self.template_name, context)


@login_required(login_url="/accounts/login/")
def update_profile(request,id):
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user = user)
    form = UpdateProfileForm(instance=profile)
    if request.method == "POST":
            form = UpdateProfileForm(request.POST,request.FILES,instance=profile)
            if form.is_valid():  
                
                profile = form.save(commit=False)
                profile.save()
                return redirect('profile') 
            
    ctx = {"form":form}
    return render(request, 'update_prof.html', ctx)




@login_required
@csrf_exempt
def following(request):
	if request.method == 'POST' and request.user.is_authenticated:
		data = {}
		for usr in request.user.profile.following.all():
			data[usr.id] = {
			 'first_name' : usr.first_name,
			 'last_name': usr.last_name,
			 'username' : usr.username,
			 'pic' : usr.profile.profile_pic.url
			 }
		
		return JsonResponse(data)
	raise Http404()

@login_required
@csrf_exempt
def followers(request):
	if request.method == 'POST' and request.user.is_authenticated:
		data = {}
		for usr in request.user.profile.followers.all():
			data[usr.id] = {
			 'first_name' : usr.first_name,
			 'last_name': usr.last_name,
			 'username' : usr.username,
			 'pic' : usr.profile.profile_pic.url,
			 'followed_back': usr in request.user.profile.following.all()
			 }
		
		return JsonResponse(data)
	raise Http404()

@login_required
def notifications(request):
	noti = Notification.objects.filter(user=request.user, seen = False)
	noti = serializers.serialize('json', noti)
	return JsonResponse({'data':noti})

@login_required
def notifications_seen(request):
	Notification.objects.filter(user=request.user, seen = False).update(seen = True)
	return HttpResponse(True)

@csrf_exempt
@login_required
def clear_notifications(request):
	if request.method == "POST":
		Notification.objects.filter(user=request.user).delete()
		return HttpResponse(True)
	return HttpResponse(False)

def islogin(request):
	return JsonResponse({'is_login':request.user.is_authenticated})







class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangingForm
    login_url = 'account:login'
    success_url = reverse_lazy('password_success')


def password_success(request):
    return render(request, "authors/password_change_success.html")


class UpdateUserView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    form_class = EditUserProfileForm
    login_url = 'account:login'
    template_name = "authors/edit_user_profile.html"
    success_url = reverse_lazy('home')
    success_message = "User updated"

    def get_object(slef):
        return slef.request.user

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                             "Please submit the form carefully")
        return redirect('home')


class DeleteUser(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = User
    login_url = 'account:login'
    template_name = 'authors/delete_user_confirm.html'
    success_message = "User has been deleted"
    success_url = reverse_lazy('home')



	
class UpdatePublicDetails(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    login_url = "account:login"
    form_class = UserPublicDetailsForm
    template_name = "authors/edit_public_details.html"
    success_url = reverse_lazy('home')
    success_message = "User updated"

    def get_object(slef):
        return slef.request.user.userprofuile

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Please submit the form carefully")
        return redirect('home')


    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Please submit the form carefully")
        return redirect('home')
	

# subscribe
def Subscribe(request):
  email = request.POST['email']
  subscription = subscriptions(user = request.user, email = email)
  subscription.save()
  messages.error(request, "Subscription Added!")
  return redirect("/")

@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(
        request, "account/dashboard/user_wishlist.html", {"wishlist": products}
    )


@login_required
def wishlist_product_toggle(request, id):
	
    product = get_object_or_404(ProductAttribute, pk=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.success(
            request, product.product.title + " has been removed from your wishlist"
        )
    else:
        product.users_wishlist.add(request.user)
        messages.success(request, "Added " + product.product.title + " to your wishlist")
        
    return HttpResponseRedirect(request.META["HTTP_REFERER"])



@login_required
def dashboard(request):
    # order_id = request.session.get('order_id', None)
    # order = get_object_or_404(Order, id=order_id)
    return render(request, "account/dashboard/dashboard.html")
