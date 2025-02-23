from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Transaction

# Register your models here.
@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'merchant', 'amount', 'status', 'is_flagged', 'approved_by']
    search_fields = ['merchant', 'amount']
    list_filter = ['status', 'is_flagged', 'timestamp']
    history_list_display = ['status', 'amount', 'is_flagged', 'approved_by']

