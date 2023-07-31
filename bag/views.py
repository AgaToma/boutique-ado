from django.shortcuts import render, redirect

# Create your views here.

def view_bag(request):
    """A view to return the bag contents page"""

    return render(request, 'bag/bag.html' )


def add_to_bag(request, item_id):
    """Add a quantity of the specified product to the shopping bag"""

    # obtain quantity from product detail template form, change to integer as it comes as string
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    # access the request's session, get variable bag if already exists, if not initialize to an empty dictionary
    # this is to store bag for the duration of the session
    bag = request.session.get('bag', {})
    # add products and quantity to the created dictionary

    if item_id in list(bag.keys()):
        bag[item_id] += quantity
    else:
        bag[item_id] = quantity
    # overriting the variable bag in the session with its updated version
    request.session['bag'] = bag
    return redirect(redirect_url)