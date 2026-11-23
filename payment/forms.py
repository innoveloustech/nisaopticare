from django import forms
from .models import PROVINCE_CHOICES, ShippingAddress

class ShippingForm(forms.ModelForm):
	shipping_full_name = forms.CharField(label="Full Name *", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Full Name'}), required=True)
	shipping_email = forms.CharField(label="Email Address", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}), required=False)
	shipping_address = forms.CharField(label="Address *", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address'}), required=True)
	# shipping_address2 = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Address2'}), required=False)
	shipping_city = forms.CharField(label="City *", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'City'}), required=True)
	shipping_province = forms.ChoiceField(label="Province *", choices=PROVINCE_CHOICES, widget=forms.Select(attrs={'class':'form-control'}), required=True)
	shipping_zipcode = forms.CharField(label="Zipcode", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Zipcode'}), required=False)
	shipping_country = forms.CharField(
			label="Country *",
			initial="Pakistan",
			widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Pakistan', 'readonly': 'readonly'}),
			required=True
		)
	class Meta:
		model = ShippingAddress
		fields = ['shipping_full_name', 'shipping_email', 'shipping_address', 'shipping_city', 'shipping_province', 'shipping_zipcode', 'shipping_country']

		exclude = ['user',]


class PaymentForm(forms.Form):
	card_name =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Name On Card'}), required=True)
	card_number =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Card Number'}), required=True)
	card_exp_date =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Expiration Date'}), required=True)
	card_cvv_number =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'CVV Code'}), required=True)
	card_address1 =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Address 1'}), required=True)
	card_address2 =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Address 2'}), required=False)
	card_city =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing City'}), required=True)
	card_state = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing State'}), required=True)
	card_zipcode =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Zipcode'}), required=True)
	card_country =  forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Billing Country'}), required=True)
