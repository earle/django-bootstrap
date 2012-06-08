"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django import forms
from forms import BootstrapForm, Fieldset

class LoginForm(BootstrapForm):
    class Meta:
        layout = (
            Fieldset("Please Login", "username", "password", ),
        )

    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), max_length=100)


class InlineHelpForm(BootstrapForm):
    class Meta:
        help_style = "inline"
        layout = (
            Fieldset("Please Login", "username", "password", ),
        )

    username = forms.CharField(max_length=100, help_text="A username")
    password = forms.CharField(widget=forms.PasswordInput(), max_length=100)


class FormTests(TestCase):
    def test_form_fieldsets(self):
        """
        Tests that fieldsets are rendered properly.
        """
        expected = """<fieldset class="please_login"><legend>Please Login</legend><div id="div_id_username" class="control-group">
    <label class="control-label" for="id_username">Username</label>
    <div class="controls">
        <input id="id_username" type="text" name="username" maxlength="100" />
        
        
    </div>
</div> <!-- /clearfix -->
<div id="div_id_password" class="control-group">
    <label class="control-label" for="id_password">Password</label>
    <div class="controls">
        <input id="id_password" type="password" name="password" maxlength="100" />
        
        
    </div>
</div> <!-- /clearfix -->
</fieldset>"""
        form = LoginForm()
        self.assertEqual(str(form), expected)

    def test_help_inline(self):
        """
        Tests that inline help spans are rendered properly.
        """
        expected = """<fieldset class="please_login"><legend>Please Login</legend><div id="div_id_username" class="control-group">
    <label class="control-label" for="id_username">Username</label>
    <div class="controls">
        <input id="id_username" type="text" name="username" maxlength="100" />
        
        
        <span class="help-inline">A username</span>
        
    </div>
</div> <!-- /clearfix -->
<div id="div_id_password" class="control-group">
    <label class="control-label" for="id_password">Password</label>
    <div class="controls">
        <input id="id_password" type="password" name="password" maxlength="100" />
        
        
    </div>
</div> <!-- /clearfix -->
</fieldset>"""
        form = InlineHelpForm()
        self.assertEqual(str(form), expected)
