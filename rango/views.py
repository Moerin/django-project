from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from .forms import CategoryForm, PageForm, UserForm, UserProfileForm
from .models import Category, Page
from .bing_search import run_query


def index(request):

    # Get the top five list category order by likes
    category_list = Category.objects.order_by('-likes')[:5]
    # Send it to the context template
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}

    # Get the number of visits to the site.
    visits = int(request.session.get('visits', '0'))
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(
            last_visit[:-7],
            "%Y-%m-%d %H:%M:%S")
        if (datetime.now() - last_visit_time).seconds > 5:
            visits = visits + 1
            reset_last_visit_time = True
    else:
        reset_last_visit_time = True

    context_dict['visits'] = visits
    request.session['visits'] = visits

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())

    response = render(request, 'rango/index.html', context_dict)

    return response


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

        if request.method == 'POST':
            query = request.POST['query'].strip()

            if query:
                context_dict['results'] = run_query(query)

    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', context_dict)


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html', {'visits': count})


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
    if request.session.test_cookie_worked():
        print(">>>> TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

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
        return render(request, 'rango/restricted.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})


def track_url(request):
    redirection = '/rango/'

    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            requested_page = Page.objects.get(id=page_id)
            requested_page.views = requested_page.views + 1
            requested_page.save()

            redirection = requested_page.url

    return HttpResponseRedirect(redirection)

"""
To correct here, integrity error NOT NULL Constraint
with rango_userprofile.user_id
The user model seems not to be saved in the db
"""
def register_profile(request):
    registered = False

    if request.method == 'POST':
        profile_form = UserProfileForm(data=request.POST)

        if profile_form.is_valid():

            profile = profile_form.save(commit=False)

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print profile_form.errors

    else:
        profile_form = UserProfileForm()

    return render(request, 'rango/profile_registration.html', {'profile_form': profile_form,
                                                   'registered': registered})
