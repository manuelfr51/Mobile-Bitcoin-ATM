from django.http import HttpResponse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.contrib import messages
from annoying.decorators import render_to
from django.utils.timezone import now
from django.views.decorators.debug import sensitive_variables, sensitive_post_parameters

from bstamp.forms import BitstampAPIForm
from bstamp.models import BSCredential


@sensitive_variables('username', 'api_key', 'secret_key', 'credentials')
@sensitive_post_parameters('username', 'api_key', 'secret_key')
@login_required
@render_to('merchants/bitstamp.html')
def bitstamp(request):
    user = request.user
    merchant = user.get_merchant()
    credential = merchant.get_bitstamp_credentials()

    form = BitstampAPIForm()
    if request.method == 'POST' and merchant:
        form = BitstampAPIForm(data=request.POST)
        if form.is_valid():
            # TODO: VALIDATE CREDENTIALS AND THEN UPDATE MODEL HERE

            api_key = form.cleaned_data['api_key']
            secret_key = form.cleaned_data['secret_key']
            credentials = BSCredential.objects.create(
                    merchant=merchant,
                    api_key=api_key,
                    api_secret=secret_key
            )
            try:
                balance = credentials.get_balance()
                messages.success(request, _('Your Bitstamp API info has been updated'))
            except:
                # question - Is this how I should do it?
                credentials.delete()
                messages.warning(request, _('Your Bitstamp API credentials are not valid'))

            return HttpResponseRedirect(reverse_lazy('bitstamp'))

    return {
        'user': user,
        'merchant': merchant,
        'form': form,
        'on_admin_page': True,
        'credential': credential,
    }

@sensitive_variables('username', 'api_key', 'secret_key', 'credentials')
@login_required
def refresh_credentials(request):
    user = request.user
    merchant = user.get_merchant()
    credential = merchant.get_bitstamp_credentials()
    try:
        balance = credential.get_balance()
        messages.success(request, _('Your Bistamp API info has been refreshed'))
    except:
        messages.warning(request, _('Your Bistamp API info could not be validated'))
    return HttpResponse("*ok*")


@sensitive_variables('username', 'api_key', 'secret_key', 'credentials')
@login_required
def disable_credentials(request):
    user = request.user
    merchant = user.get_merchant()
    credential = merchant.get_bitstamp_credentials()
    credential.disabled_at = now()
    credential.save()
    return HttpResponse("*ok*")
