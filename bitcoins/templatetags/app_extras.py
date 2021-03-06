from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def trim(value):
    return value.strip()


@register.filter(name='obscure_except_ending')
def obscure_except_ending(string, trailing_chars_to_show=5):
    """
    Obscures the beginning of a string with *s and leaves
    `trailing_chars_to_show` in plaintext.
    """
    if not string:
        return ""

    string_len = len(string)

    if string_len <= trailing_chars_to_show:
        # Less to hide than exists
        return string

    reveal_len = string_len-trailing_chars_to_show

    return '*' * reveal_len + string[reveal_len:]


@register.filter(name='format_status_string')
def format_status_string(string):
    GREEN_STATUSES = ['complete', 'valid', 'cash paid out']
    # YELLOW_STATUSES = ['waiting for verifications']
    RED_STATUSES = ['canceled', 'invalid']

    if string.lower() in GREEN_STATUSES:
        return mark_safe(u'<span class ="text-green">%s</span> ' % (string))
    # if string.lower() in YELLOW_STATUSES:
    #     return mark_safe('<span class ="text-amethyst">%s</span>' % (string))
    elif string.lower() in RED_STATUSES:
        return mark_safe(u'<span class ="text-red">%s</span>' % (string))
    else:
        return mark_safe(u'%s' % (string))


@register.filter(name='format_fiat_amount')
def format_fiat_amount(amount, currency_symbol, currency_code=None):
    if currency_code:
        return "%s%s %s" % (currency_symbol, '{:,.2f}'.format(amount), currency_code)
    else:
        return "%s%s" % (currency_symbol, '{:,.2f}'.format(amount))


@register.filter(name='hide_long_string')
def hide_long_string(string, front_chars_to_show=6):
    """
    Hides long string by default and lets you toggle it open to show more
    Useful for btc addresses on small screens
    """
    if not string:
        return ""

    string_len = len(string)

    if string_len <= front_chars_to_show:
        # Less to hide than exists
        return string

    pre_string = ""
    post_string = ""
    i = 0
    while i < string_len:
        if i < front_chars_to_show - 1:
            pre_string += string[i]
        else:
            post_string += string[i]
        i += 1

    return mark_safe(u'<a class="long-string-toggle" style="cursor:pointer;">%s<span id="ellipsis">...</span><span id="post-string" style="display:none;">%s<span></a>' % (pre_string, post_string))


@register.filter(name='remove_quotes')
def remove_quotes(string):
    """
    Obscures the beginning of a string with *s and leaves
    `trailing_chars_to_show` in plaintext.
    """
    string = string.replace("\"", "")
    string = string.replace("\'", "")
    return string
