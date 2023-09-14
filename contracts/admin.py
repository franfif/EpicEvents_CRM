from django.contrib import admin
from contracts.models import Contract, ContractStatus


admin.site.register(Contract)
admin.site.register(ContractStatus)
