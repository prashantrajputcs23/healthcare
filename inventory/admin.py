from django.contrib import admin
from .models import *


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['parent', 'name']


@admin.register(ActiveIngredient)
class ActiveIngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


class ProductIngredientInline(admin.TabularInline):
    model = ProductIngredient
    extra = 1
    autocomplete_fields = ['ingredient']
    fields = ['ingredient', 'strength']
    verbose_name = "Active Ingredient"
    verbose_name_plural = "Active Ingredients"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'dosage_form', 'manufacturer']
    search_fields = ['name', 'category__name', 'manufacturer']
    list_filter = ['category', 'dosage_form']
    inlines = [ProductIngredientInline]


@admin.register(PharmacyProduct)
class PharmacyProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'quantity_in_stock', 'price', 'discount', 'is_discount_active', 'reorder_level']
    search_fields = ['product__name', 'sku']
    list_filter = ['is_discount_active', 'organisation']
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_info', 'email', 'phone']


class PurchaseOrderDetailInline(admin.TabularInline):
    model = PurchaseOrderDetail
    extra = 1
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'total_amount', 'organisation', 'site', 'created_by', 'created_at')
    search_fields = ('supplier__name', 'id')
    list_filter = ('supplier', 'created_at')
    inlines = [PurchaseOrderDetailInline]
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


class SalesOrderDetailInline(admin.TabularInline):
    model = SalesOrderDetail
    extra = 1
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'patient', 'total_amount', 'is_paid', 'organisation', 'site', 'created_by',
        'created_at')
    search_fields = ('patient__name', 'bill_to', 'id')
    list_filter = ('is_paid', 'created_at')
    inlines = [SalesOrderDetailInline]
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'invoice_number', 'order_type', 'total_amount', 'organisation', 'site', 'created_by', 'created_at')
    search_fields = ('invoice_number', 'related_order__id', 'purchase_order__id')
    list_filter = ('order_type', 'created_at')
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'transaction_type', 'quantity', 'organisation', 'site', 'created_by', 'created_at')
    search_fields = ('product__product__name',)
    list_filter = ('transaction_type', 'created_at')
    readonly_fields = ['site', 'created_by', 'organisation', 'created_at', 'updated_at']
