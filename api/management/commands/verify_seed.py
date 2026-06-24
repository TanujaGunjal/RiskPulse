"""
Verification script for seed_db command
Run with: python manage.py shell < verify_seed.py
"""

from models import Transaction, Alert
from django.db.models import Avg, Count, Min, Max
from datetime import datetime

print("\n" + "=" * 70)
print("DATABASE VERIFICATION REPORT")
print("=" * 70)
print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Transaction Statistics
print("TRANSACTIONS")
print("-" * 70)
total_transactions = Transaction.objects.count()
print(f"Total transactions: {total_transactions}")

if total_transactions > 0:
    # Risk statistics
    risk_distribution = (
        Transaction.objects
        .values('risk_tier')
        .annotate(count=Count('id'))
        .order_by('risk_tier')
    )
    
    print("\nRisk Tier Distribution:")
    for item in risk_distribution:
        tier = item['risk_tier'].upper()
        count = item['count']
        percentage = (count / total_transactions) * 100
        print(f"  {tier:12} : {count:6} ({percentage:5.1f}%)")
    
    # Risk score statistics
    avg_risk = Transaction.objects.aggregate(avg=Avg('final_risk'))['avg']
    min_risk = Transaction.objects.aggregate(min=Min('final_risk'))['min']
    max_risk = Transaction.objects.aggregate(max=Max('final_risk'))['max']
    
    print(f"\nFinal Risk Scores:")
    print(f"  Average: {avg_risk:.3f}")
    print(f"  Minimum: {min_risk:.3f}")
    print(f"  Maximum: {max_risk:.3f}")
    
    # Component scores
    avg_dvs = Transaction.objects.aggregate(avg=Avg('DVS'))['avg']
    avg_tns = Transaction.objects.aggregate(avg=Avg('TNS'))['avg']
    avg_ics = Transaction.objects.aggregate(avg=Avg('ICS'))['avg']
    avg_ccs = Transaction.objects.aggregate(avg=Avg('CCS'))['avg']
    
    print(f"\nComponent Scores (Average):")
    print(f"  DVS (Demographic):  {avg_dvs:.3f}")
    print(f"  TNS (Testing):      {avg_tns:.3f}")
    print(f"  ICS (Income):       {avg_ics:.3f}")
    print(f"  CCS (Consistency):  {avg_ccs:.3f}")
    
    # Sample records
    print(f"\nSample Records:")
    samples = Transaction.objects.order_by('?')[:3]
    for tx in samples:
        print(f"  - {tx.caseid}: Risk {tx.final_risk:.3f} ({tx.risk_tier})")

# Alert Statistics
print(f"\n{'=' * 70}")
print("ALERTS")
print("-" * 70)
total_alerts = Alert.objects.count()
print(f"Total alerts: {total_alerts}")

if total_alerts > 0:
    unresolved = Alert.objects.filter(is_resolved=False).count()
    resolved = Alert.objects.filter(is_resolved=True).count()
    
    print(f"  Unresolved: {unresolved}")
    print(f"  Resolved:   {resolved}")
    
    # Alert risk distribution
    alert_risk_dist = (
        Alert.objects
        .values('risk_tier')
        .annotate(count=Count('id'))
        .order_by('risk_tier')
    )
    
    print(f"\nAlert Risk Tier Distribution:")
    for item in alert_risk_dist:
        tier = item['risk_tier'].upper()
        count = item['count']
        percentage = (count / total_alerts) * 100
        print(f"  {tier:12} : {count:6} ({percentage:5.1f}%)")

# Summary
print(f"\n{'=' * 70}")
print("SUMMARY")
print("-" * 70)
print(f"Total Transaction Records:  {total_transactions:>10}")
print(f"Total Alert Records:        {total_alerts:>10}")
print(f"Alert to Transaction Ratio: {total_alerts/total_transactions*100:>9.1f}%")

# Verify referential integrity
orphaned_alerts = Alert.objects.filter(transaction__isnull=True).count()
if orphaned_alerts > 0:
    print(f"\n⚠️  WARNING: {orphaned_alerts} alerts with missing transactions!")
else:
    print(f"\n✓ Referential integrity OK: All alerts linked to transactions")

# Final status
if total_transactions > 0 and total_alerts >= 0:
    print("\n✓ Database verification PASSED")
else:
    print("\n✗ Database verification FAILED")

print("=" * 70 + "\n")
