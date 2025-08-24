#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univ_services.settings')
django.setup()

from financial.models import StudentFee

# Check if fee 750544049 exists
fee = StudentFee.objects.filter(id=750544049).first()
print(f'Fee 750544049 exists: {fee is not None}')
if fee:
    print(f'Fee belongs to user: {fee.student.id}')
    print(f'Fee type: {fee.fee_type.name}')
    print(f'Fee amount: {fee.amount}')
    print(f'Fee status: {fee.status}')
else:
    print('Fee 750544049 does not exist in the database')

# Show all fees for user 3
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(id=3)
fees = StudentFee.objects.filter(student=user)
print(f'\nUser {user.id} has {fees.count()} fees:')
for fee in fees:
    print(f'ID: {fee.id}, Type: {fee.fee_type.name}, Amount: {fee.amount}, Status: {fee.status}')