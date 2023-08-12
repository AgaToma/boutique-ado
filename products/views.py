from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            # ensuring case insensitive sorting on name field by adding (annotating) a temporary field on the model
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        # sorting by category
        if 'category' in request.GET:
            # split categories at commas in received request into a list
            categories = request.GET['category'].split(',')
            # filter out only products with categories in the list, adding name because of the foreign key relation
            # between category and product
            products = products.filter(category__name__in=categories)
            # changing category strings from received url into objects, to be able to access their fields in templates
            categories = Category.objects.filter(name__in=categories)

        # search query
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))     
            #check if query text is contained either in product name or description
            queries = Q(name__icontains=query)|Q(description__icontains=query)
            products = products.filter(queries)

    # set this variable to return sorting to template
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        # list of category objects returned to context, so we can use them in templates later on
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)

def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        # request.FILES is needed to capture image of the product if one is submitted
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)
