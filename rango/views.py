from django.shortcuts import render
from .models import Category, Page
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required


def index(request):
    # Get the top five list category order by likes
    category_list = Category.objects.order_by('-likes')[:5]
    # Send it to the context template
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}

    # Try to fetch a category by slug name
    # if it can't, raises an DoesNotExist exception
    try:
        category = Category.objects.get(slug=category_name_slug)
        # Get the name of the category
        context_dict['category_name'] = category.name
        # Get the associatives pages with the foreign key
        pages = Page.objects.filter(category=category)
        # Save the page for the context
        context_dict['pages'] = pages
        # Add the category objects for the context
        context_dict['category'] = category
        # Test for the slug
        context_dict['slug'] = category_name_slug
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)


def about(request):
    return render(request, 'rango/about.html')


def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)

            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                return category(request, category_name_slug)
        else:
            print form.errors

    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}

    return render(request, 'rango/add_page.html', context_dict)

def register(request):

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {'user_form': user_form,
                                                   'profile_form': profile_form,
                                                   'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your account is desactived')
        else:
            print "Invalid login details: {0} {1}".format(username, password)
            return HttpResponse("Invalid login detailed supplied")
    else:
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    return HttpResponse("If you can see this, so you are logged in!")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')
