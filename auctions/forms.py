from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import User,Listing, Comment,Bid, Category
from django.shortcuts import render
import imghdr
from urllib.request import urlopen
from django.forms.widgets import Select


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["description"]
        labels = {
        "description": "Add a comment: "
    }

    def clean(self):
        if self.description == '':
            raise ValidationError('Empty error message')

def index(request):
    return render(request, "auctions/index.html")


class ListingForm(ModelForm):
    class Meta:
        CHOICES= Category
        model = Listing
        fields = ["title", "description", "category"]
        widgets = {
            'category': Select(choices=( (x.id, x.name) for x in CHOICES.objects.all() )),
        }




    def clean_image(self):
        
        print(self.cleaned_data['title'])
        try:
            print(imghdr.what(None, urlopen(self.cleaned_data['title']).read()))
        except (IOError, TypeError,ValueError):
            print("error")
            raise ValidationError("That entry already exists")
        return 1    

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["price"]
        labels = {
        "price": "Add your bid: "
    }

    def clean_price(self):
        print(self.cleaned_data.get("price"))
        print(int(self.request.POST["minbid"]))
        price=self.cleaned_data.get("price")
        minvalue=int(self.request.POST["minbid"])
        if price < minvalue :
            raise ValidationError('Your bid should be higher than the minimum price')
        return price
    #overrides init method to allow accessing request in clean method
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(BidForm, self).__init__(*args, **kwargs)