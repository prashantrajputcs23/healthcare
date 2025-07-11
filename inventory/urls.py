from django.urls import path
from .views import *
from .import_export import upload_pharmacy_products

app_name = 'inventory'

urlpatterns = [
    path('pharmacy/products', PharmacyProductList.as_view(), name='pharmacy_products'),
    path('pharmacy/product/add', create_pharmacy_product, name='create_pharmacy_product'),
    path('pharmacy/product/<pk>/update', update_pharmacy_product, name='update_pharmacy_product'),
    path('pharmacy/sales', SalesOrderView.as_view(), name='sales'),
    path('pharmacy/sales/table', SalesListView.as_view(), name='sales_table'),
    path('pharmacy/sales/new', create_sales_order, name='create_sales_order'),
    path('pharmacy/purchases', PurchaseOrderView.as_view(), name='purchases'),
    path('pharmacy/purchases/table', PurchaseOrderListView.as_view(), name='purchases_table'),
    path('pharmacy/purchase/new', create_purchase_order, name='create_purchase_order'),
    path('print/sales/<pk>', PrintSales.as_view(), name='print_sales'),
    path('pharmacy/get-product-detail', get_product_details, name='get_product_details'),
    path('pharmacy/get_product_choices', get_product_choices, name='get_product_choices'),
]

# Import Export

urlpatterns += [
    path('upload_pharmacy_products', upload_pharmacy_products, name='upload_pharmacy_products'),
]
