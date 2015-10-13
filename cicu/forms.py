import uuid
import os.path

from django import forms

from .models import UploadedFile


class UploadedFileForm(forms.ModelForm):

    class Meta:
        model = UploadedFile
        fields = ('file',)

    def clean_file(self):
        data = self.cleaned_data['file']

        try:
            extension = os.path.splitext(data.name)[1]
        except IndexError:
            extension = ''

        # Change the name of the file to something unguessable whilst preserving the extension
        # Construct the new name as <unique-hex>.<ext>
        data.name = u'%s.%s' % (uuid.uuid4().hex, extension)
        return data
