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

class BootstrapMixin(object):

    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'custom_fields'):
            self.custom_fields = self.Meta.custom_fields
        else:
            self.custom_fields = {}

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'template_base'):
            self.template_base = self.Meta.template_base
        else:
            self.template_base = "bootstrap"

        if hasattr(self, 'Meta') and hasattr(self.Meta, 'help_style'):
            self.help_style = self.Meta.help_style
        else:
            self.help_style = "block"

    # For backward compatibility
    __bootstrap__ = __init__

    def top_errors_as_html(self):
        """ Render top errors as set of <div>'s. """
        return ''.join(["<div class=\"alert alert-error\">%s</div>" % error
                        for error in self.top_errors])

    def get_layout(self):
        """ Return the user-specified layout if one is available, otherwise
            build a default layout containing all fields.
        """
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'layout'):
            return self.Meta.layout
        else:
            # Construct a simple layout using the keys from the fields
            return self.fields.keys()

    def as_div(self):
        """ Render the form as a set of <div>s. """

        self.top_errors = self.non_field_errors()
        self.prefix_fields = []

        output = self.render_fields(self.get_layout())

        if self.top_errors:
            errors = self.top_errors_as_html()
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
                help_text = '<span class="help-%s">%s</span>' % (self.help_style, force_unicode(field_instance.help_text))
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
                'label_id': bf._auto_id(),
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

    def __unicode__(self):
        # Default output is now as <div> tags.
        return self.as_div()


class BootstrapForm(BootstrapMixin, forms.Form):
    pass


class BootstrapModelForm(BootstrapMixin, forms.ModelForm):
    pass


class Fieldset(object):
    """ Fieldset container. Renders to a <fieldset>. """

    def __init__(self, legend, *fields, **kwargs):
        self.legend = legend
        self.fields = fields
        self.css_class = kwargs.get('css_class', '_'.join(legend.lower().split()))

    def as_html(self, form):
        legend_html = self.legend and (u'<legend>%s</legend>' % self.legend) or ''
        return u'<fieldset class="%s">%s%s</fieldset>' % (self.css_class, legend_html, form.render_fields(self.fields))

