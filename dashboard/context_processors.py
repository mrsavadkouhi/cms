from django.urls import resolve


def path_data(request):
	try:
		return {'path_data': resolve(request.path)}
	except:
		return {'path_data': ''}
