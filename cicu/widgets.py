
from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from PIL import Image

from .models import UploadedFile

# Basic configuration for jcrop from django
optionsInput = """
<input id="cicu-options-%s"
       data-size-warning="%s"
       data-ratio-width="%s"
       data-ratio-height="%s"
       data-modal-button-label="%s"
       data-change-button-text="%s"
       data-size-alert-message="%s"
       data-size-error-message="%s"
       data-modal-save-crop-message="%s"
       data-modal-close-crop-message="%s"
       data-uploading-message="%s"
       data-file-upload-label="%s"
       style="display: none;" />
"""


class CicuException(Exception):
    pass


class CicuUploaderInput(forms.ClearableFileInput):
    template_with_clear = ''  # We don't need this
    template_with_initial = '%(input)s'

    def __init__(self, attrs=None, options=None):
        if not options:
            options = {}
        super(CicuUploaderInput, self).__init__(attrs)

        self.use_custom_css = options.get('use_custom_css', False)

        # Jcrop configuration
        self.options = ()
        self.options += (options.get('sizeWarning', 'True'),)
        self.options += (options.get('ratioWidth', ''),)
        self.options += (options.get('ratioHeight', ''),)

        # Input message customization and translation
        self.options += (options.get('modalButtonLabel', _('Upload image')),)
        self.options += (options.get('changeButtonText', _('Change Image')),)
        self.options += (
            options.get(
                'sizeAlertMessage',
                _('Warning: The area selected is too small.  Min size:')
            ),
        )
        self.options += (
            options.get(
                'sizeErrorMessage',
                _("Image doesn't meet the minimum size requirements ")
            ),
        )
        self.options += (options.get('modalSaveCropMessage', _('Set image')),)
        self.options += (options.get('modalCloseCropMessage', _('Close')),)
        self.options += (options.get('uploadingMessage', _('Uploading your image')),)
        self.options += (options.get('fileUploadLabel', _('Select image from your computer')),)

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        if value:
            filename = u'%s%s' % (settings.MEDIA_URL, value)
        else:
            filename = ''
        attrs.update({
            'class': attrs.get('class', '') + 'ajax-upload',
            'data-filename': filename,  # This is so the javascript can get the actual value
            'data-required': self.is_required or '',
            'data-upload-url': reverse('ajax-upload'),
            'data-crop-url': reverse('cicu-crop'),
            'type': 'file',
            'accept': 'image/*',
        })
        output = super(CicuUploaderInput, self).render(name, value, attrs)
        option = optionsInput % ((name,) + self.options)
        autoDiscoverScript = "<script>$(function(){CicuWidget.autoDiscover();});</script>"
        return mark_safe(output + option + autoDiscoverScript)

    def value_from_datadict(self, data, files, name):
        # If a file was uploaded or the clear checkbox was checked, use that.
        file = super(CicuUploaderInput, self).value_from_datadict(data, files, name)
        if file is not None:  # super class may return a file object, False, or None
            return file  # Default behaviour
        elif name in data:  # This means a file id was specified in the POST field
            try:
                uploaded_file = UploadedFile.objects.get(id=data.get(name))
                img = Image.open(uploaded_file.file.path, mode='r')
                width, height = img.size
                optionWidth = int(self.options[1])
                optionHeight = int(self.options[2])
                sizeWarning = self.options[0] == 'True'
                if ((width < optionWidth or height < optionHeight) and sizeWarning):
                    raise Exception(
                        'Image don\'t have correct ratio %sx%s' % (self.options[1], self.options[2])
                    )
                return uploaded_file.file
            except Exception:
                return None
        return None

    def _media(self):

        js = (
            "cicu/js/jquery.Jcrop.min.js",
            "cicu/js/jquery.iframe-transport.js",
            "cicu/js/cicu-widget.js",
            )

        css = ["cicu/css/jquery.Jcrop.min.css"]
        if not self.use_custom_css:
            css.append("cicu/css/cicu-widget.css")

        return forms.widgets.Media(css={'all': css}, js=js)

    media = property(_media)
