from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acessar itens de dicionário com chave variável no template"""
    try:
        return dictionary.get(key)
    except:
        return None
