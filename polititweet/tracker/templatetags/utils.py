from django import template

register = template.Library()

@register.filter
def split_into_columns(data, columns="2"):
    columns = int(columns)
    split = [[] for i in range(columns)]
    for i in range(len(data)):
        split[i % columns].append(data[i])
    return split