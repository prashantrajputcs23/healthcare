import uuid
from django.contrib.sites.models import Site
from django.db import models
import uuid
from django.utils import timezone
from django.db.models import Max
from healthcare.utils import current_site, get_request, current_org
from patient.models import Patient
from user.models import Organization, User
from web.models import Statistics


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class DosageFormChoice(models.TextChoices):
    TABLET = 'tablet', 'Tablet'
    CAPSULE = 'capsule', 'Capsule'
    SYRUP = 'syrup', 'Syrup'
    INJECTION = 'injection', 'Injection'
    GEL = 'gel', 'Gel'
    OIL = 'oil', 'Oil'
    OINTMENT = 'ointment', 'Ointment'
    CREAM = 'cream', 'Cream'
    DROPS = 'drops', 'Drops'
    INHALER = 'inhaler', 'Inhaler'
    SPRAY = 'spray', 'Spray'
    SUPPOSITORY = 'suppository', 'Suppository'
    PATCH = 'patch', 'Patch'
    POWDER = 'powder', 'Powder'
    GRANULES = 'granules', 'Granules'
    LOZENGE = 'lozenge', 'Lozenge'
    PASTE = 'paste', 'Paste'
    SHAMPOO = 'shampoo', 'Shampoo'
    SOLUTION = 'solution', 'Solution'
    SUSPENSION = 'suspension', 'Suspension'
    EMULSION = 'emulsion', 'Emulsion'
    TRANSDERMAL_PATCH = 'transdermal_patch', 'Transdermal Patch'
    ORAL_STRIP = 'oral_strip', 'Oral Strip'


class ActiveIngredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255, unique=True)
    dosage_form = models.CharField(max_length=100, choices=DosageFormChoice.choices, blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductIngredient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_ingredients')
    ingredient = models.ForeignKey(ActiveIngredient, on_delete=models.CASCADE, related_name='product_ingredients')
    strength = models.CharField(max_length=50, help_text='Potency of the ingredient (e.g., 500mg)', blank=True,
                                null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'ingredient', 'strength')

    def __str__(self):
        return f"{self.ingredient.name} in {self.product.name} - {self.strength}"


class PharmacyProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='pharmacy_product')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100, choices=DosageFormChoice.choices, default=DosageFormChoice.TABLET)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    discount = models.IntegerField(null=True, blank=True, help_text='discount in %', default=8)
    is_discount_active = models.BooleanField(default=True)
    reorder_level = models.PositiveIntegerField(default=25)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='pharmacy_products')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='pharmacy_products')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pharmacy_products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product__name', '-quantity_in_stock']

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(PharmacyProduct, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} ({self.quantity_in_stock} {self.sku})'

    def update_stock(self, delta):
        """
        Adjust stock by a delta amount.
        - Positive delta: increase stock (e.g., purchase)
        - Negative delta: decrease stock (e.g., sales)
        """
        if delta == 0:
            return
        self.quantity_in_stock += delta
        self.save(update_fields=['quantity_in_stock'])

    def is_below_reorder_level(self):
        """Check if the product is below the reorder level."""
        return self.quantity_in_stock <= self.reorder_level


class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contact_info = models.TextField()
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f'{self.name} - {self.phone}'


class PaymentChoices(models.TextChoices):
    CASH = 'cash'
    UPI = 'UPI'


class PurchaseOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='purchase_orders')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='purchase_orders')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='purchase_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, default='pending')  # Assuming this field exists

    @classmethod
    def all(cls):
        return cls.objects.filter(site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(PurchaseOrder, self).save(*args, **kwargs)

    def __str__(self):
        return f"Purchase Order #{self.id} from {self.supplier.name}"

    def receive_order(self):
        """Process received purchase order and update stock."""
        # Process all purchase order details and update stock.
        for detail in self.purchase_order_details.all():
            # Calculate the delta between previous stock (if any) and new quantity
            previous_quantity = detail.previous_quantity if hasattr(detail, 'previous_quantity') else 0
            new_quantity = detail.quantity
            delta = new_quantity - previous_quantity

            # Update stock based on the calculated delta
            if delta != 0:
                detail.product.update_stock(delta, 'incoming')  # 'incoming' direction for stock increase

            # Update previous quantity to the new quantity
            detail.previous_quantity = new_quantity
            detail.save(update_fields=['previous_quantity'])

        # Optionally mark the order as completed or do any other post-processing tasks
        # Example: self.status = 'completed' (but you mentioned no status, so this may not be needed)
        self.save()  # Save changes to the order (e.g., status update if needed)


class PurchaseOrderDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='purchase_order_details')
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE, related_name='purchase_details')
    sku = models.CharField(max_length=100, null=True, choices=DosageFormChoice.choices, default=DosageFormChoice.choices)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='purchase_order_details')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='purchase_order_details')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='purchase_order_details')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        super(PurchaseOrderDetail, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.product.name} in {self.purchase_order.id}"


class SalesOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_mode = models.CharField(choices=PaymentChoices.choices, default=PaymentChoices.CASH)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sales_orders')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='sales_orders')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def all(cls):
        return cls.objects.filter(site=current_site())

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request():
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()

        super(SalesOrder, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.name}"


class SalesOrderDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='sales_order_details')
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sales_order_details')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='sales_order_details')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales_order_details')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()
        self.gross_amount = self.quantity * self.price_per_unit
        # self.total = self.quantity*self.price_per_unit
        super(SalesOrderDetail, self).save(*args, **kwargs)

        if self.sales_order:
            self.sales_order.total_amount = sum(
                detail.total for detail in self.sales_order.sales_order_details.all()
            )
            self.sales_order.save()

    def __str__(self):
        return f"{self.product.product.name} in {self.sales_order.id}"

    class Meta:
        unique_together = ['sales_order', 'product']


def generate_invoice_number():
    current_year = timezone.now().year
    last_invoice = Invoice.objects.filter(invoice_number__startswith=f"INV-{current_year}").order_by(
        'invoice_number').last()
    if not last_invoice:
        next_number = 1
    else:
        last_number = int(last_invoice.invoice_number.split('-')[-1])
        next_number = last_number + 1
    invoice_number = f"INV-{current_year}-{str(next_number).zfill(5)}"
    return invoice_number


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    order_type = models.CharField(max_length=20, choices=[('sale', 'Sale'), ('purchase', 'Purchase')])
    related_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, blank=True, null=True,
                                         related_name='invoice')
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, blank=True, null=True,
                                          related_name='invoice')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    slip = models.ImageField(upload_to='invoices', null=True, blank=True, help_text='must upload purchase bill')
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invoices')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='invoices')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='invoices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically set the created_by, organisation, and site fields
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()

        # Automatically generate invoice number if it's not set
        if not self.invoice_number:
            # Get the latest invoice number from the same organisation and site
            last_invoice = Invoice.objects.filter(organisation=self.organisation, site=self.site).order_by(
                '-invoice_number').first()

            if last_invoice and last_invoice.invoice_number:
                # Extract the last invoice number and increment it
                try:
                    last_number = int(
                        last_invoice.invoice_number.split(' ')[1])  # Get the last number part and convert it to int
                    new_number = str(last_number + 1)  # Increment the number
                except Exception as e:
                    new_number = '1'  # If there's an issue with the split or conversion, start from 1
            else:
                # If no previous invoice, start from 1
                new_number = '1'

            # Ensure the number is at least 3 digits (pad with leading zeroes if needed)
            new_number_padded = new_number.zfill(3)

            # Generate new invoice number
            self.invoice_number = f"SN {new_number_padded}"

        # Ensure the invoice number is unique
        while Invoice.objects.filter(invoice_number=self.invoice_number).exists():
            last_invoice = Invoice.objects.filter(organisation=self.organisation, site=self.site).order_by(
                '-invoice_number').first()
            if last_invoice and last_invoice.invoice_number:
                try:
                    last_number = int(last_invoice.invoice_number.split(' ')[1])
                    new_number = str(last_number + 1)
                    new_number_padded = new_number.zfill(3)
                    self.invoice_number = f"SN {new_number_padded}"
                except Exception as e:
                    new_number = '1'
                    self.invoice_number = f"SN {new_number.zfill(3)}"

        super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

    def mark_as_paid(self):
        self.is_paid = True
        self.save()

class InventoryTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, null=True, on_delete=models.CASCADE, related_name='inventory_transactions')
    product = models.ForeignKey(PharmacyProduct, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=[('incoming', 'Incoming'), ('outgoing', 'Outgoing')])
    quantity = models.PositiveIntegerField()
    organisation = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='inventory_transactions')
    site = models.ForeignKey(Site, on_delete=models.PROTECT, related_name='inventory_transactions')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inventory_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.created_by_id and get_request().user.is_authenticated:
            self.created_by = get_request().user
        if not self.organisation_id:
            self.organisation = current_org()
        if not self.site_id:
            self.site = current_site()

        # Update the stock for the product based on the transaction type
        if self.transaction_type == 'incoming':
            self.product.quantity_in_stock += self.quantity  # Increase stock for incoming transactions
        elif self.transaction_type == 'outgoing':
            self.product.quantity_in_stock -= self.quantity  # Decrease stock for outgoing transactions
        self.product.save()  # Save the product after adjusting the stock

        super(InventoryTransaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} {self.quantity} of {self.product.product.name}"
