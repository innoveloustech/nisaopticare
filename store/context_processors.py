from .models import Category, SubCategory, Gender, StoreInfo

def categories_processor(request):
    return {
        'categories': Category.objects.all(),
        'subcategories': SubCategory.objects.all(),
        'genders': Gender.objects.all(),
    }

def store_info(request):
    try:
        info = StoreInfo.objects.first()
        return {'store_info': info}
    except:
        return {'store_info': None}  