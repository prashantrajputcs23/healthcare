from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from patient.models import Patient
from .models import ProductCategory, PharmacyProduct, Product, get_request, Site, SalesOrder, SalesOrderDetail, \
    PurchaseOrder, PurchaseOrderDetail, Supplier


class PharmacyProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=ProductCategory.objects.none(), label="Category", required=True)
    product = forms.ModelChoiceField(queryset=Product.objects.none(), label="Product", required=True)

    class Meta:
        model = PharmacyProduct
        fields = ['product', 'category', 'price', 'sku', 'quantity_in_stock', 'discount', 'is_discount_active',
                  'reorder_level']

    def __init__(self, *args, current_site=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ProductCategory.objects.all()
        self.fields['product'].queryset = Product.objects.all()
        if self.instance.pk and hasattr(self.instance, 'product') and self.instance.product:
            self.fields['category'].initial = self.instance.product.category

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column('product', css_class='col-md-6'),
                Column('category', css_class='col-md-6'),
            ),
            Row(
                Column('price', css_class='col-md-6'),
                Column('sku', css_class='col-md-6'),
            ),
            Row(
                Column('quantity_in_stock', css_class='col-md-6'),
                Column('discount', css_class='col-md-6'),
            ),
            Row(
                Column('reorder_level', css_class='col-md-6'),
            ),
            Row(
                Column('is_discount_active', css_class='col-md-6'),
            ),
            Row(
                Column(Submit('action', 'save', css_class='btn btn-primary'), css_class='col-1'),
            ),
        )


class SalesOrderForm(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

    class Meta:
        model = SalesOrder
        fields = ['patient', 'payment_mode', 'is_paid']

    def __init__(self, *args, **kwargs):
        super(SalesOrderForm, self).__init__(*args, **kwargs)


class SalesOrderDetailForm(forms.ModelForm):
    class Meta:
        model = SalesOrderDetail
        fields = ['product', 'quantity', 'price_per_unit', 'discount', 'total']

    def __init__(self, *args, **kwargs):
        super(SalesOrderDetailForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'quantity'
        self.fields['price_per_unit'].widget.attrs['readonly'] = True
        self.fields['price_per_unit'].widget.attrs['class'] = 'price-per-unit'
        self.fields['discount'].widget.attrs['readonly'] = True
        self.fields['discount'].widget.attrs['class'] = 'discount'
        self.fields['total'].widget.attrs['readonly'] = True
        self.fields['total'].widget.attrs['class'] = 'product_total_amount'


SalesOrderDetailFormSet = inlineformset_factory(
    SalesOrder,
    SalesOrderDetail,
    form=SalesOrderDetailForm,
    extra=5,
    can_delete=True
)


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'total_amount']

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['total_amount'].widget.attrs['readonly'] = True


class PurchaseOrderDetailForm(forms.ModelForm):
    class Meta:
        model = SalesOrderDetail
        fields = ['product', 'quantity', 'price_per_unit', 'total']

    def __init__(self, *args, **kwargs):
        super(PurchaseOrderDetailForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'quantity'
        self.fields['price_per_unit'].widget.attrs['readonly'] = True
        self.fields['price_per_unit'].widget.attrs['class'] = 'price-per-unit'
        self.fields['total'].widget.attrs['class'] = 'product_total_amount'
        self.fields['total'].widget.attrs['readonly'] = True


PurchaseOrderDetailFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderDetail,
    form=PurchaseOrderDetailForm,
    extra=5,
    can_delete=True
)
