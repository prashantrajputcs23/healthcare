from healthcare.utils import current_site, current_org
from user.models import Branch


def site(request):
    return {'current_site': current_site()}


def org(request):
    try:
        return {'org': current_org()}
    except Exception as e:
        return {'org': None}


def branches(request):
    try:
        return {'branches': Branch.all_branches()}
    except Exception as e:
        return {'branches': None}
