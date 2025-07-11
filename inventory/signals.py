from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from .models import SalesOrderDetail, PurchaseOrderDetail, Invoice, SalesOrder, InventoryTransaction


# ==== SALES ORDER SIGNALS ====

@receiver(pre_save, sender=SalesOrderDetail)
def adjust_stock_on_sales_detail_change(sender, instance, **kwargs):
    """
    Adjusts stock when a SalesOrderDetail is modified.
    """
    if instance.pk:
        try:
            previous = SalesOrderDetail.objects.get(pk=instance.pk)
            delta = instance.quantity - previous.quantity  # sales = decrease stock
            # Create or update the inventory transaction based on the delta
            InventoryTransaction.objects.create(
                product=instance.product,
                transaction_type='outgoing',
                quantity=delta,
                organisation=instance.sales_order.organisation,
                site=instance.sales_order.site,
                created_by=instance.sales_order.created_by
            )
            instance.product.update_stock(-delta)
        except SalesOrderDetail.DoesNotExist:
            # New sales
            instance.product.update_stock(-instance.quantity)
            InventoryTransaction.objects.create(
                product=instance.product,
                transaction_type='outgoing',
                quantity=instance.quantity,
                organisation=instance.sales_order.organisation,
                site=instance.sales_order.site,
                created_by=instance.sales_order.created_by
            )
    else:
        # New sales
        instance.product.update_stock(-instance.quantity)
        InventoryTransaction.objects.create(
            product=instance.product,
            transaction_type='outgoing',
            quantity=instance.quantity,
            organisation=instance.sales_order.organisation,
            site=instance.sales_order.site,
            created_by=instance.sales_order.created_by
        )


@receiver(post_delete, sender=SalesOrderDetail)
def restore_stock_on_sales_detail_delete(sender, instance, **kwargs):
    """
    Reverse stock when SalesOrderDetail is deleted and create a corresponding InventoryTransaction.
    """
    instance.product.update_stock(instance.quantity)
    InventoryTransaction.objects.create(
        product=instance.product,
        transaction_type='incoming',
        quantity=instance.quantity,
        organisation=instance.sales_order.organisation,
        site=instance.sales_order.site,
        created_by=instance.sales_order.created_by
    )


# ==== PURCHASE ORDER SIGNALS ====

@receiver(pre_save, sender=PurchaseOrderDetail)
def adjust_stock_on_purchase_detail_change(sender, instance, **kwargs):
    """
    Adjusts stock when a PurchaseOrderDetail is modified.
    """
    if instance.pk:
        try:
            previous = PurchaseOrderDetail.objects.get(pk=instance.pk)
            delta = instance.quantity - previous.quantity  # purchase = increase stock
            # Create or update the inventory transaction based on the delta
            InventoryTransaction.objects.create(
                product=instance.product,
                transaction_type='incoming',
                quantity=delta,
                organisation=instance.purchase_order.organisation,
                site=instance.purchase_order.site,
                created_by=instance.purchase_order.created_by
            )
            instance.product.update_stock(delta)
        except PurchaseOrderDetail.DoesNotExist:
            instance.product.update_stock(instance.quantity)
            InventoryTransaction.objects.create(
                product=instance.product,
                transaction_type='incoming',
                quantity=instance.quantity,
                organisation=instance.purchase_order.organisation,
                site=instance.purchase_order.site,
                created_by=instance.purchase_order.created_by
            )
    else:
        # New purchase
        instance.product.update_stock(instance.quantity)
        InventoryTransaction.objects.create(
            product=instance.product,
            transaction_type='incoming',
            quantity=instance.quantity,
            organisation=instance.purchase_order.organisation,
            site=instance.purchase_order.site,
            created_by=instance.purchase_order.created_by
        )


@receiver(post_delete, sender=PurchaseOrderDetail)
def reduce_stock_on_purchase_detail_delete(sender, instance, **kwargs):
    """
    Reverse stock when PurchaseOrderDetail is deleted and create a corresponding InventoryTransaction.
    """
    instance.product.update_stock(-instance.quantity)
    InventoryTransaction.objects.create(
        product=instance.product,
        transaction_type='outgoing',
        quantity=instance.quantity,
        organisation=instance.purchase_order.organisation,
        site=instance.purchase_order.site,
        created_by=instance.purchase_order.created_by
    )


# ==== SALES ORDER SIGNAL: CREATE/UPDATE INVOICE ====

@receiver(post_save, sender=SalesOrder)
def create_or_update_invoice(sender, instance, created, **kwargs):
    """
    Creates or updates an invoice when a SalesOrder is created or updated.
    """
    if created:  # If SalesOrder is newly created
        # Create the invoice for this SalesOrder
        invoice = Invoice.objects.create(
            related_order=instance,
            order_type='sale',  # Assuming this is a sale, you can check more conditions for purchase if needed
            total_amount=instance.total_amount,  # Assuming the SalesOrder has a `total_amount`
            organisation=instance.organisation,
            site=instance.site,
            created_by=instance.created_by
        )

        # Optionally, create InventoryTransactions for all SalesOrderDetails associated with the SalesOrder
        for sales_detail in instance.sales_order_details.all():
            InventoryTransaction.objects.create(
                product=sales_detail.product,
                transaction_type='outgoing',
                quantity=sales_detail.quantity,
                organisation=instance.organisation,
                site=instance.site,
                created_by=instance.created_by
            )
    else:  # If SalesOrder is updated
        # You can choose to update the invoice if needed
        try:
            invoice = instance.invoice  # Check if the related invoice exists
            invoice.total_amount = instance.total_amount  # Update the invoice total if sales order total is updated
            invoice.save()
        except Invoice.DoesNotExist:
            # If no invoice exists, create one (this is rare but can happen if the Invoice was deleted)
            Invoice.objects.create(
                related_order=instance,
                order_type='sale',
                total_amount=instance.total_amount,
                organisation=instance.organisation,
                site=instance.site,
                created_by=instance.created_by
            )

