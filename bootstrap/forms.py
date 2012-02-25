import os
from django.template import Context,RequestContext
from django.template.loader import get_template, select_template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django import forms
from django.utils.encoding import force_unicode

class NoSuchFormField(Exception):
    """""The form field couldn't be resolved."""""
    pass

def error_list(errors):
    return '<ul class="errors"><li>' + \
           '</li><li>'.join(errors) + \
           '</li></ul>'

class BootstrapMixin(object):

    def __bootstrap__(self):
        # do we have an explicit layout?
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            self.layout = self.Meta.layout
        else:
            # Construct a simple layout using the keys from the fields
            self.layout = self.fields.keys()

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'custom_fields'):
            self.custom_fields = self.Meta.custom_fields
        else:
            self.custom_fields = {}

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'template_base'):
            self.template_base = self.Meta.template_base
        else:
            self.template_base = "bootstrap"

    def as_div(self):
        """ Render the form as a set of <div>s. """

        self.top_errors = []
        self.prefix_fields = []

        output = self.render_fields(self.layout)

        if self.top_errors:
            errors = error_list(self.top_errors)
        else:
            errors = u''

        prefix = u''.join(self.prefix_fields)

        return mark_safe(prefix + errors + output)

    def render_fields(self, fields, separator=u""):
        """ Render a list of fields and join the fields by the value in separator. """

        output = []
        
        for field in fields:
            if isinstance(field, Fieldset):
                output.append(field.as_html(self))
            else:
                output.append(self.render_field(field))


        return separator.join(output)

    def render_field(self, field):
        """ Render a named field to HTML. """

        try:
            field_instance = self.fields[field]
        except KeyError:
            raise NoSuchFormField("Could not resolve form field '%s'." % field)

        bf = forms.forms.BoundField(self, field_instance, field)

        output = ''

        if bf.errors:
            # If the field contains errors, render the errors to a <ul>
            # using the error_list helper function.
            # bf_errors = error_list([escape(error) for error in bf.errors])
            bf_errors = ', '.join([e for e in bf.errors])
        else:
            bf_errors = ''

        if bf.is_hidden:
            # If the field is hidden, add it at the top of the form
            self.prefix_fields.append(unicode(bf))

            # If the hidden field has errors, append them to the top_errors
            # list which will be printed out at the top of form
            if bf_errors:
                self.top_errors.extend(bf.errors)

        else:

            # Find field + widget type css classes
            css_class = type(field_instance).__name__ + " " +  type(field_instance.widget).__name__

            # Add an extra class, Required, if applicable
            if field_instance.required:
                css_class += " required"

            if field_instance.help_text:
                # The field has a help_text, construct <span> tag
                help_text = '<span class="help_text">%s</span>' % force_unicode(field_instance.help_text)
            else:
                help_text = u''

            field_hash = {
                'class' : mark_safe(css_class),
                'label' : mark_safe(bf.label or ''),
                'help_text' :mark_safe(help_text),
                'field' : field_instance,
                'bf' : mark_safe(unicode(bf)),
                'bf_raw' : bf,
                'errors' : mark_safe(bf_errors),
                'field_type' : mark_safe(field.__class__.__name__),
            }
            
            if self.custom_fields.has_key(field):
                template = get_template(self.custom_fields[field])
            else:
                template = select_template([
                    os.path.join(self.template_base, 'field_%s.html' % type(field_instance.widget).__name__.lower()),
                    os.path.join(self.template_base, 'field_default.html'), ])
                
            # Finally render the field
            output = template.render(Context(field_hash))

        return mark_safe(output)

class BootstrapForm(forms.Form, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.__bootstrap__()

    # Default output is now as <div> tags.
    def __str__(self):
        return self.as_div()

    def __unicode__(self):
        return self.as_div()

class BootstrapModelForm(forms.ModelForm, BootstrapMixin):
    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.__bootstrap__()

    def __str__(self):
        return self.as_div()

    def __unicode__(self):
        return self.as_div()

class Fieldset(object):
    """ Fieldset container. Renders to a <fieldset>. """

    def __init__(self, legend, css_class=None, *fields):
        self.legend_html = legend and ('<legend>%s</legend>' % legend) or ''
        self.fields = fields
        self.css_class = css_class
    
    def as_html(self, form):
        class_str = self.css_class and (' class="%s"' % self.css_class) or ''
        return u'<fieldset%s>%s%s</fieldset>' %  (class_str, self.legend_html, form.render_fields(self.fields), )
            
