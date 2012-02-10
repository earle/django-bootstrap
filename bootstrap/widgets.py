from django.forms.widgets import RadioInput, RadioFieldRenderer, RadioSelect,TextInput
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe


class OptionsRadioInput(RadioInput):
    def __unicode__(self):
        if 'id' in self.attrs:
            label_for = ' for="%s_%s"' % (self.attrs['id'], self.index)
        else:
            label_for = ''
        choice_label = conditional_escape(force_unicode(self.choice_label))
        return mark_safe(u'<label%s>%s <span>%s</span></label>' %
                         (label_for, self.tag(), choice_label))


class OptionsRadioRenderer(RadioFieldRenderer):
    def render(self):
        return mark_safe(u'<ul class="inputs-list">\n%s\n</ul>' %
                         u'\n'.join([u'<li>%s</li>' %
                         force_unicode(w) for w in self]))


class OptionsRadio(RadioSelect):
    renderer = OptionsRadioRenderer

class AppendedText(TextInput):
    def render(self, name, value, attrs=None):
        return '%s<span class="add-on">%s</span>' % (super(AppendedText,self).render(name, value, attrs),self.attrs['append_text'])
