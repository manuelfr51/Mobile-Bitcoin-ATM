from django.contrib import admin

from bitcash.custom import ReadOnlyModelAdmin

from merchants.models import Merchant, OpenTime, MerchantWebsite

from utils import format_satoshis_with_units_rounded

from bitcash.custom import ReadOnlyModelAdmin


# https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
class CredentialFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Credentials'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'credential'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('none', 'No Credentials'),
            ('some', 'Some Credentials'),
            ('some_valid', 'Some Valid Credentials'),
            ('some_invalid', 'Some Invalid Credentials'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """

        # TODO: our current credentials logic in merchants/models is confusing,
        # this may change when that improves
        if self.value() == 'none':
            return queryset.filter(basecredential=None)
        if self.value() == 'some':
            return queryset.filter(basecredential__isnull=False).distinct()
        if self.value() == 'some_valid':
            return queryset.filter(basecredential__isnull=False, basecredential__last_failed_at=None).distinct()
        if self.value() == 'some_invalid':
            return queryset.filter(basecredential__isnull=False, basecredential__last_failed_at__isnull=False).distinct()


# https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
class IgnoredAtFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('active', 'OK to contact'),
            ('ignore', 'DO NOT contact'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'ignore':
            return queryset.filter(ignored_at__isnull=False)
        if self.value() == 'active':
            return queryset.filter(ignored_at=None)


# https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
class NeedsCoordinatesFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Needing Coordinates'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'coordinates'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('examine', 'May Need Coordinates'),
            ('done', 'Has Coordinates'),
            ('ignore', 'Ignore'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'examine':
            return queryset.filter(ignored_at=None, address_1__isnull=False, longitude_position=None).exclude(address_1='')
        if self.value() == 'done':
            return queryset.filter(longitude_position__isnull=False)
        if self.value() == 'ignore':
            return queryset.filter(ignored_at__isnull=False)


# https://docs.djangoproject.com/en/1.6/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
class NeedsSyndicationFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Needing Syndication'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'syndication'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('syndicated', 'Syndicated'),
            ('ready_to_syndicate', 'Ready to Syndicate'),
            ('ignore', 'Ignore'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'syndicated':
            return queryset.filter(syndicated_at__isnull=False)
        if self.value() == 'ready_to_syndicate':
            return queryset.filter(ignored_at=None,
                    syndicated_at=None,
                    longitude_position__isnull=False,
                    merchantwebsite__deleted_at=None,
                    merchantdoc__deleted_at=None,
                    ).distinct()
        if self.value() == 'ignore':
            return queryset.filter(ignored_at__isnull=False)


def set_latitude_longitude(modeladmin, request, queryset):
    for obj in queryset:
        obj.set_latitude_longitude()
set_latitude_longitude.short_description = "Set Latitiude and Longitude"


class MerchantAdmin(ReadOnlyModelAdmin):

    def owner_name(self, instance):
        return instance.user.full_name
    owner_name.allow_tags = True

    def user_email(self, instance):
        return '%s (<a href="%s">%s</a>)' % (instance.user.email,
                instance.user.get_admin_uri(), instance.user.id)
    user_email.allow_tags = True

    def btc_address(self, instance):
        return instance.get_destination_address()
    btc_address.allow_tags = True

    def website(self, instance):
        return instance.get_website_obj()
    website.allow_tags = True

    def current_api_credential(self, instance):
        api_cred = instance.get_api_credential()
        if api_cred:
            curr_balance = api_cred.get_latest_balance()
            if curr_balance:
                balance_fswur = format_satoshis_with_units_rounded(curr_balance.satoshis)
            else:
                balance_fswur = '0 mBTC'
            if api_cred.appears_usable():
                inactive_str = ''
            else:
                inactive_str = ' - INACTIVE'
            return '<a href="%s">%s with %s%s</a>' % (
                    api_cred.get_admin_uri(),
                    api_cred.get_credential_to_display(),
                    balance_fswur,
                    inactive_str,
                    )
    current_api_credential.allow_tags = True

    def api_summary(self, instance):
        api_creds = instance.get_all_api_creds()
        balance_obj = instance.get_highest_balance_obj()
        if balance_obj:
            max_fswur = format_satoshis_with_units_rounded(balance_obj.satoshis)
        else:
            max_fswur = '0 mBTC'
        return '%s creds (max was %s)</a>' % (api_creds.count(), max_fswur)
    api_summary.allow_tags = True

    def short_url(self, instance):
        short_url_obj = instance.get_short_url_obj()
        if short_url_obj:
            profile_uri = short_url_obj.get_profile_uri()
            if profile_uri:
                return '<a href="%s">%s</a> (<a href="%s">edit</a> or <a href="%s">add</a>)' % (
                        profile_uri, profile_uri,
                        short_url_obj.get_admin_uri(),
                        short_url_obj.get_new_admin_uri()
                        )
        return ''
    short_url.allow_tags = True

    list_display = (
        'id',
        'created_at',
        'business_name',
        'owner_name',
        'short_url',
        'user_email',
        'phone_num',
        'current_api_credential',
        'api_summary',
        'currency_code',
        'country',
        'state',
        'city',
        'address_1',
        'btc_address',
        'website',
        'cashin_markup_in_bps',
        'cashout_markup_in_bps',
        'latitude_position',
        'longitude_position',
        'ignored_at',
        'syndicated_at',
    )
    raw_id_fields = ('user', )
    search_fields = ['user__email', 'user__full_name', 'phone_num', 'business_name', ]
    list_filter = (
            NeedsCoordinatesFilter,
            NeedsSyndicationFilter,
            CredentialFilter,
            IgnoredAtFilter,
            'currency_code',
            'country',
            )

    class Meta:
        model = Merchant
    actions = [set_latitude_longitude]
admin.site.register(Merchant, MerchantAdmin)


class OpenTimeAdmin(ReadOnlyModelAdmin):

    list_display = ('id', 'merchant', 'weekday', 'from_time', 'to_time', 'is_closed_this_day')
    raw_id_fields = ('merchant', )

    class Meta:
        model = OpenTime

admin.site.register(OpenTime, OpenTimeAdmin)


class MerchantWebsiteAdmin(ReadOnlyModelAdmin):

    list_display = ('id', 'merchant', 'url', 'deleted_at', )
    raw_id_fields = ('merchant', )

    class Meta:
        model = MerchantWebsite

admin.site.register(MerchantWebsite, MerchantWebsiteAdmin)
