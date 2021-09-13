from django import forms


class ItemPerPageForm(forms.Form):
	per_page = forms.CharField(
		max_length=4,
		widget=forms.Select(choices=((10, '10'),
		                             (20, '20'),
		                             (50, '50'),
		                             (100, '100'),
		                             (200, '200'),
		                             (500, '500'),
		                             )),
		required=False,
		initial=50,
		label='تعداد در هر صفحه',
	)
