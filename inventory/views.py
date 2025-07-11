import sweetify
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView
from django_filters.views import FilterView
from healthcare.utils import is_uuid, get_page_context, entry_per_page
from .filters import PharmacyProductFilter, SalesOrderFilter, PurchaseOrderFilter
from .forms import *
from .models import *


class PharmacyProductList(FilterView):
    model = PharmacyProduct
    template_name = 'inventory/pharmacy_product_list.html'
    context_object_name = "products"
    paginate_by = entry_per_page
    filterset_class = PharmacyProductFilter

    def get_queryset(self):
        """Filter products by the current site."""
        queryset = super().get_queryset()
        return queryset.filter(site=current_site())


def create_pharmacy_product(request):
    if request.method == 'POST':
        mutable_post = request.POST.copy()
        category_id = mutable_post.get('category')
        product_id = mutable_post.get('product')
        if not is_uuid(category_id):
            new_category, _ = ProductCategory.objects.get_or_create(name=category_id)
            mutable_post['category'] = new_category.pk
            category_id = new_category.pk
        if not is_uuid(product_id):
            new_product, _ = Product.objects.get_or_create(name=product_id, category_id=category_id)
            mutable_post['product'] = new_product.pk
        form = PharmacyProductForm(mutable_post)
        if form.is_valid():
            pp = form.save()
            sweetify.success(request, title='Success', text=f'{pp.product.name} successfully added.')
            if request.POST.get("action") == "save":
                return redirect(reverse_lazy('inventory:pharmacy_products'))
    else:
        form = PharmacyProductForm()
    return render(request, 'inventory/pharmacy_product_form.html', {'form': form})


def update_pharmacy_product(request, pk):
    instance = get_object_or_404(PharmacyProduct, pk=pk)
    form = PharmacyProductForm(instance=instance)
    if request.method == 'POST':
        form = PharmacyProductForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
        sweetify.success(request, title='Success', text=f'{instance.product.name} successfully updated.')
        if request.POST.get("action") == "save":
            return redirect(reverse_lazy('inventory:pharmacy_products'))
        elif request.POST.get("action") == "save_and_add_more":
            return redirect(reverse_lazy('inventory:create_pharmacy_product'))
    return render(request, 'inventory/pharmacy_product_form.html', {'form': form})


class SalesOrderView(TemplateView):
    template_name = 'inventory/sales_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SalesOrderFilter(self.request.GET).form
        return context


class SalesListView(FilterView):
    model = SalesOrder
    template_name = 'inventory/partials/sales_order_table.html'
    filterset_class = SalesOrderFilter
    paginate_by = entry_per_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.object_list
        if not self.request.user.is_superuser:
            filtered_queryset = filtered_queryset.filter(created_by=self.request.user)
        context['total_sales'] = filtered_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        context.update(get_page_context(self, queryset=filtered_queryset))
        return context


def create_sales_order(request):
    context = dict()
    if request.method == 'POST':
        sales_order_form = SalesOrderForm(request.POST)
        mutable_post = request.POST.copy()
        patient = mutable_post['patient']
        if not is_uuid(patient):
            patient = Patient.objects.create(name=patient)
            mutable_post['patient'] = patient.pk
        sales_order_form = SalesOrderForm(mutable_post)
        formset = SalesOrderDetailFormSet(request.POST)
        if sales_order_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Save the Sales Order
                sales_order = sales_order_form.save(commit=False)
                sales_order.created_by = request.user
                sales_order.total_amount = 0.0
                sales_order.save()
                # Save the SalesOrderDetails
                details = formset.save(commit=False)
                for detail in details:
                    detail.sales_order = sales_order
                    detail.organisation = sales_order.organisation
                    detail.site = sales_order.site
                    detail.created_by = request.user
                    detail.save()
                sweetify.success(request, title="Successfully Saved",
                                 text=f"Sales order of amount {sales_order} Saved.")
                return redirect(reverse_lazy('inventory:print_sales', kwargs={'pk': sales_order.pk}))
        else:
            form_set_non_field_errors = []
            for error in formset.errors:
                if error:
                    form_set_non_field_errors = error.get('__all__')
                    context.update({
                        'form_set_non_field_errors': form_set_non_field_errors
                    })
            print(sales_order_form.errors)
            print(formset.errors)
            print('non_field_error')
            print(form_set_non_field_errors)

    else:
        sales_order_form = SalesOrderForm()
        formset = SalesOrderDetailFormSet()
    context.update({
        'sales_order_form': sales_order_form,
        'formset': formset,
    })
    return render(request, 'inventory/sales_order_form_factory.html', context)


def get_product_details(request):
    product_id = request.GET.get('product_id')
    try:
        product = PharmacyProduct.objects.get(id=product_id)
        discounted_price = 0.0
        discount_percentage = 0.0
        try:
            discount_percentage = product.discount
            discounted_price = round((discount_percentage / 100) * float(product.price), 2)
        except Exception as e:
            pass

        return JsonResponse({
            'price_per_unit': product.price,
            'discount_percentage': discount_percentage,
            'discount_amount': discounted_price,
        })
    except PharmacyProduct.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def get_product_choices(request):
    query = request.GET.get('q', "")
    results = []

    if query:
        # Filter products based on multiple fields including related fields
        products = PharmacyProduct.objects.filter(
            Q(product__name__icontains=query) |
            Q(product__manufacturer__icontains=query) |
            Q(product__product_ingredients__ingredient__name__icontains=query)
        ).distinct()  # Use distinct to avoid duplicate results due to joins

        # Prepare results with relevant fields
        for product in products:
            product_data = {
                'id': str(product.id),  # Ensure the ID is a string for the JSON response
                'text': f"{product.product.name} ({product.product.manufacturer})",  # Customize the display text
                'price': product.price,
                'stock': product.quantity_in_stock,
                'manufacturer': product.product.manufacturer,
                'ingredients': [ingredient.ingredient.name for ingredient in product.product.product_ingredients.all()]
            }
            results.append(product_data)

    return JsonResponse({"results": results})


def update_sales_order(request):
    pass

def create_purchase_order(request):
    context = dict()
    if request.method == 'POST':
        mutable_post = request.POST.copy()
        supplier = mutable_post.get('supplier')

        # Check if supplier is a valid UUID or a new name
        if not is_uuid(supplier):
            # Create new supplier
            new_supplier = Supplier.objects.create(name=supplier)
            mutable_post['supplier'] = new_supplier.pk  # replace with actual UUID

        # Use modified POST data in forms
        purchase_order_form = PurchaseOrderForm(mutable_post)
        formset = PurchaseOrderDetailFormSet(mutable_post)

        if purchase_order_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                purchase_order = purchase_order_form.save(commit=False)
                purchase_order.created_by = request.user
                purchase_order.save()

                details = formset.save(commit=False)
                for detail in details:
                    detail.purchase_order = purchase_order
                    detail.organisation = purchase_order.organisation
                    detail.site = purchase_order.site
                    detail.created_by = request.user
                    detail.save()

                sweetify.success(
                    request,
                    title="Successfully Saved",
                    text=f"Purchase order of amount {purchase_order.total_amount} Saved."
                )
                return redirect(reverse_lazy('inventory:create_sales_order'))
        else:
            context['form_set_non_field_errors'] = [
                error.get('__all__') for error in formset.errors if '__all__' in error
            ]

    else:
        purchase_order_form = PurchaseOrderForm()
        formset = PurchaseOrderDetailFormSet()

    context.update({
        'purchase_order_form': purchase_order_form,
        'formset': formset,
    })
    return render(request, 'inventory/purchase_order_form.html', context)


class PurchaseOrderView(TemplateView):
    template_name = 'inventory/purchase_orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PurchaseOrderFilter(self.request.GET).form
        return context


class PurchaseOrderListView(FilterView):
    model = PurchaseOrder
    template_name = 'inventory/partials/purchase_order_table.html'
    filterset_class = PurchaseOrderFilter
    paginate_by = entry_per_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtered_queryset = self.object_list
        if not self.request.user.is_superuser:
            filtered_queryset = filtered_queryset.filter(user=self.request.user)
        context['total_purchase'] = filtered_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        context.update(get_page_context(self, queryset=filtered_queryset))
        return context


class PrintSales(DetailView):
    template_name = 'inventory/print_html.html'
    model = SalesOrder
