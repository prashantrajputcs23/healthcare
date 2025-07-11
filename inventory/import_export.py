import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.core.files.storage import default_storage
from django.urls import reverse_lazy
from openpyxl import load_workbook
from .models import ProductCategory, Product, PharmacyProduct


def upload_pharmacy_products(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_name = default_storage.save(file.name, ContentFile(file.read()))
        file_path = default_storage.path(file_name)
        try:
            df = pd.read_excel(file_path, dtype=str)
            required_columns = {'product_name', 'price', 'category_name', 'quantity', 'reorder_level', 'discount'}
            if not required_columns.issubset(df.columns):
                messages.error(request, "Invalid file format. Ensure correct columns are present.")
                return redirect('upload_page')

            with transaction.atomic():
                for _, row in df.iterrows():
                    category, _ = ProductCategory.objects.get_or_create(name=row['category_name'].strip())
                    product, _ = Product.objects.get_or_create(name=row['product_name'].strip(),
                                                               defaults={'category': category})
                    product.category = category  # Ensure category update if changed
                    product.save()

                    pharmacy_product, created = PharmacyProduct.objects.get_or_create(
                        product=product,
                        defaults={
                            'price': float(row['price']),
                            'quantity_in_stock': int(row['quantity']),
                            'reorder_level': int(row['reorder_level']),
                            'discount': int(row['discount']) if row['discount'] else 0
                        }
                    )

                    if not created:
                        pharmacy_product.price = float(row['price'])
                        pharmacy_product.quantity_in_stock = int(row['quantity'])
                        pharmacy_product.reorder_level = int(row['reorder_level'])
                        pharmacy_product.discount = int(row['discount']) if row['discount'] else 0
                        pharmacy_product.save()

            messages.success(request, "File uploaded and processed successfully!")
        except Exception as e:
            print(e)
            messages.error(request, f"Error processing file: {str(e)}")
        finally:
            print("Exception")
            default_storage.delete(file_path)

        return redirect(reverse_lazy('inventory:pharmacy_products'))

    return HttpResponse('Invalid request')
