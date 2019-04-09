# From https://djangosnippets.org/snippets/1441/

from django import template

register = template.Library()

@register.inclusion_tag('tracker/pagination.html')
def pagination(page, url_parameters=None, begin_pages=2, end_pages=2, before_current_pages=4, after_current_pages=4):

    before = max(page.number - before_current_pages - 1, 0)
    after = page.number + after_current_pages
    
    begin = page.paginator.page_range[:begin_pages]
    middle = page.paginator.page_range[before:after]
    end = page.paginator.page_range[-end_pages:]
    last_page_number = end[-1]
    
    def collides(firstlist, secondlist):
        return any(item in secondlist for item in firstlist)
    
    if collides(middle, end):
        end = range(max(page.number-before_current_pages, 1), last_page_number+1)
        middle = []
        
    if collides(begin, middle):
        begin = range(1, min(page.number + after_current_pages, last_page_number)+1)
        middle = []
        
    if collides(begin, end):
        begin = range(1, last_page_number+1)
        end = []
    
    return {'page' : page,
            'begin' : begin,
            'middle' : middle,
            'end' : end,
            'url_parameters' : url_parameters}

@register.filter(name="enable_pagination")
def enable_pagination(value):
    return value.replace("&pagination=False","")